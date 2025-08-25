import json
import subprocess
from datetime import datetime, timedelta
from typing import Optional

from utils import relative_time, pretty_size, int_hours

_UN = 'unavailable'


def get_smart(device: str, cmd: Optional[list], missing_attribute: bool) -> tuple[str, dict]:
    return _parse_smart(*_read_smart(device, cmd), missing_attribute)


# "SMART Ref": "https://www.backblaze.com/blog/what-smart-stats-indicate-hard-drive-failures/",
def _parse_smart(code: int, data_: dict, missing_attribute: bool) -> tuple[str, dict]:
    if code == 9999:
        return 'Error', {}
    elif code == 255:
        return 'Sleep', {}
    elif code not in (0, 4, 64):
        return str(code), {}
    data = {}
    try:
        data = {
            'Last updated': f'{datetime.now():%H:%M, %d.%m.%Y}',
            'Model name': data_['model_name'],
            'Device': data_['device']['name'],
            'Size': pretty_size(data_["user_capacity"]["bytes"]),
            'temperature': data_['temperature']['current'],
            'Smart status': 'Healthy' if data_['smart_status']['passed'] else 'Failed',
        }

        atr = {}
        for val in data_['ata_smart_attributes']['table']:
            atr[val['id']] = val['raw']['value'] if val['id'] != 9 else int_hours(val['raw']['string'].split(' ')[0])
        attr_data = {
            'Power on time': relative_time(datetime.now() - timedelta(hours=atr[9])) if 9 in atr else _UN,
            'Power cycle count': atr.get(12, _UN),
            'Start stop count': atr.get(4, _UN),
            'Reallocated_Sector_Ct': atr.get(5, _UN),
            'Reported_Uncorrect': atr.get(187, _UN),
            'Command_Timeout': atr.get(188, _UN),
            'Current_Pending_Sector': atr.get(197, _UN),
            'Offline_Uncorrectable': atr.get(198, _UN),
        }
        if not missing_attribute:
            attr_data = {k: v for k, v in attr_data.items() if v != _UN}
        data.update(attr_data)

        logs = data_.get('ata_smart_self_test_log', {})
        for values in [logs.get('standard', {}).get('table', []), logs.get('extended', {}).get('table', [])]:
            for idx, val in enumerate(values):
                test, result = val['type']['string'], val['status']['string']
                if test == 'Short offline':
                    test = 'Short'
                if result == 'Completed without error':
                    result = 'OK'
                data[f'Test #{idx}'] = f'{test}, {result} @ {val["lifetime_hours"]} hrs'
    except Exception as e:
        print(f'SMART PARSE ERROR: {e}')
        return 'Error', data
    return 'Awake', data


def _read_smart(device: str, cmd: Optional[list]) -> tuple[int, dict]:
    call = ['/usr/sbin/smartctl']
    call += cmd or ['-ai', '--json=c', '-n', 'standby,255', f'/dev/{device}']
    try:
        data = subprocess.run(call, check=True,  capture_output=True).stdout
    except subprocess.CalledProcessError as e:
        if e.returncode in [4, 68, 64]:
            data = e.output
        else:
            print(f'SMART READ ERROR {e.returncode}:{e.output}')
            return e.returncode, {}
    try:
        data = json.loads(data)
        return data['smartctl']['exit_status'], data
    except Exception as e:
        print(f'SMART DECODE ERROR: {e}')
        return 9999, {}
