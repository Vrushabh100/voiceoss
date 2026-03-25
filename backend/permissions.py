import winreg, subprocess, ctypes, os

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

def get_startup_apps():
    apps = []
    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    apps.append({
                        'name': name,
                        'command': value,
                        'type': 'startup',
                        'enabled': True
                    })
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f'Startup apps error: {e}')
    return apps

def get_running_processes():
    procs = []
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             'Get-Process | Select-Object Name, Id, WorkingSet | ConvertTo-Csv -NoTypeInformation'],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split('\n')
        for line in lines[1:]:  # skip header
            line = line.strip().strip('"')
            if not line:
                continue
            parts = line.split('","')
            if len(parts) >= 2:
                try:
                    procs.append({
                        'name': parts[0].strip('"'),
                        'pid': parts[1].strip('"'),
                        'memory': str(round(int(parts[2].strip('"')) / 1024 / 1024, 1)) + ' MB' if len(parts) > 2 else 'N/A'
                    })
                except:
                    pass
    except Exception as e:
        print(f'Processes error: {e}')
    return procs

def get_disk_usage():
    try:
        result = subprocess.run(
            'wmic logicaldisk get size,freespace,caption',
            shell=True, capture_output=True, text=True
        )
        disks = []
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    free = int(parts[1])
                    total = int(parts[2])
                    used = total - free
                    disks.append({
                        'drive': parts[0],
                        'total_gb': round(total / 1e9, 1),
                        'free_gb': round(free / 1e9, 1),
                        'used_gb': round(used / 1e9, 1),
                        'percent_used': round(used / total * 100, 1) if total > 0 else 0
                    })
                except:
                    pass
        return disks
    except Exception as e:
        print(f'Disk error: {e}')
        return []

def kill_process(pid):
    try:
        subprocess.run(f'taskkill /f /pid {pid}', shell=True)
        return {'success': True, 'message': f'Killed process {pid}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def disable_startup_app(name):
    try:
        key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
        return {'success': True, 'message': f'Disabled {name}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    print('Admin:', is_admin())
    print('Startup apps:', len(get_startup_apps()))
    print('Running processes:', len(get_running_processes()))
    print('Disk usage:', get_disk_usage())
    print('Permissions OK!')