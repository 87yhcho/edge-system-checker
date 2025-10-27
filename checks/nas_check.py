"""
NAS 상태 점검 모듈
SSH를 통한 NAS 시스템 정보 수집
"""
import paramiko
from typing import Dict, Any


def run_ssh_command(
    host: str,
    username: str,
    password: str,
    command: str,
    port: int = 22,
    timeout: int = 10
) -> Dict[str, Any]:
    """SSH를 통해 명령어 실행"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            host,
            port=port,
            username=username,
            password=password,
            timeout=timeout
        )
        
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        stdout_text = stdout.read().decode('utf-8', errors='ignore')
        stderr_text = stderr.read().decode('utf-8', errors='ignore')
        exit_code = stdout.channel.recv_exit_status()
        
        ssh.close()
        
        return {
            'success': exit_code == 0,
            'stdout': stdout_text,
            'stderr': stderr_text,
            'exit_code': exit_code
        }
    except paramiko.AuthenticationException:
        return {
            'success': False,
            'error': 'Authentication failed',
            'stdout': '',
            'stderr': 'SSH authentication failed',
            'exit_code': -1
        }
    except paramiko.SSHException as e:
        return {
            'success': False,
            'error': f'SSH error: {str(e)}',
            'stdout': '',
            'stderr': str(e),
            'exit_code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stdout': '',
            'stderr': str(e),
            'exit_code': -1
        }


def test_ssh_connection(host: str, username: str, password: str, port: int = 22) -> Dict[str, Any]:
    """SSH 연결 테스트"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        ssh.close()
        return {
            'success': True,
            'message': f'SSH connection successful (port {port})'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'SSH connection failed: {str(e)}'
        }


def check_nas_status(nas_config: Dict[str, str]) -> Dict[str, Any]:
    """전체 NAS 점검 실행"""
    from utils.ui import (
        print_section, print_pass, print_fail, print_info,
        print_warning, print_key_value
    )
    
    print_section(4, 4, "NAS 상태 점검")
    
    # 설정 정보
    host = nas_config.get('ip', '192.168.10.30')
    username = nas_config.get('user', 'admin')
    password = nas_config.get('password', '')
    port = int(nas_config.get('port', 22))
    
    print_info(f"연결 정보: {username}@{host}:{port}")
    
    result = {
        'status': 'UNKNOWN',
        'connection': 'Not tested',
        'system': {},
        'storage': {}
    }
    
    # 1. SSH 연결 테스트
    print_info("SSH 연결 테스트 중...")
    conn_result = test_ssh_connection(host, username, password, port)
    
    if not conn_result['success']:
        print_fail(f"연결 실패: {conn_result['error']}")
        result['status'] = 'FAIL'
        result['connection'] = 'Failed'
        result['error'] = conn_result['error']
        return result
    
    print_pass("SSH 연결 성공")
    result['connection'] = 'Success'
    
    # 2. 시스템 정보 수집
    print("")
    print_info("시스템 정보 수집 중...")
    
    system_commands = {
        'hostname': 'hostname',
        'uptime': 'uptime',
        'load_average': 'cat /proc/loadavg'
    }
    
    for key, cmd in system_commands.items():
        cmd_result = run_ssh_command(host, username, password, cmd, port)
        if cmd_result['success']:
            result['system'][key] = cmd_result['stdout'].strip()
            print_key_value(key, cmd_result['stdout'].strip()[:60], 'PASS')
        else:
            result['system'][key] = f"Error: {cmd_result['stderr']}"
            print_key_value(key, f"Error: {cmd_result['stderr']}", 'FAIL')
    
    # 3. 디스크 사용량 확인
    print("")
    print_info("디스크 사용량 확인 중...")
    
    df_result = run_ssh_command(host, username, password, 'df -h', port)
    if df_result['success']:
        print_pass("디스크 사용량 조회 성공")
        result['storage']['disk_usage'] = df_result['stdout']
        
        # 주요 마운트 포인트만 출력
        lines = df_result['stdout'].split('\n')
        print("")
        print("  주요 볼륨:")
        for line in lines[:10]:  # 최대 10개
            if line.strip():
                print(f"    {line}")
    else:
        print_fail(f"디스크 사용량 조회 실패: {df_result['stderr']}")
        result['storage']['disk_usage'] = f"Error: {df_result['stderr']}"
    
    # 4. RAID 상태 확인
    print("")
    print_info("RAID 상태 확인 중...")
    
    mdstat_result = run_ssh_command(host, username, password, 'cat /proc/mdstat', port)
    if mdstat_result['success']:
        raid_output = mdstat_result['stdout']
        result['storage']['raid_status'] = raid_output
        
        if raid_output.strip():
            print_pass("RAID 상태 조회 성공")
            print("")
            # 간단히 요약 출력
            lines = raid_output.split('\n')[:15]  # 최대 15줄
            for line in lines:
                if line.strip():
                    print(f"    {line}")
        else:
            print_warning("RAID 정보가 없습니다 (소프트웨어 RAID 미사용)")
    else:
        print_warning(f"RAID 상태 확인 불가: {mdstat_result['stderr']}")
        result['storage']['raid_status'] = f"Error: {mdstat_result['stderr']}"
    
    # 5. /mnt/nas 마운트 상태 확인
    print("")
    print_info("/mnt/nas 마운트 상태 확인 중...")
    
    mount_result = run_ssh_command(host, username, password, 'mount | grep /mnt/nas', port)
    if mount_result['success'] and mount_result['stdout'].strip():
        print_pass("/mnt/nas 마운트됨")
        result['storage']['mnt_nas_status'] = mount_result['stdout'].strip()
        print(f"    {mount_result['stdout'].strip()}")
        
        # 디렉토리 내용 확인
        ls_result = run_ssh_command(host, username, password, 'ls -la /mnt/nas | head -20', port)
        if ls_result['success']:
            result['storage']['mnt_nas_contents'] = ls_result['stdout']
            print("")
            print("  /mnt/nas 내용:")
            for line in ls_result['stdout'].split('\n')[:10]:
                if line.strip():
                    print(f"    {line}")
    else:
        print_warning("/mnt/nas가 마운트되지 않았거나 존재하지 않음")
        result['storage']['mnt_nas_status'] = "Not mounted"
    
    # 6. UPS 상태 확인 (NAS에서)
    print("")
    print_info("NAS UPS 상태 확인 중...")
    
    # upsc 시도
    ups_result = run_ssh_command(host, username, password, 'upsc ups@localhost 2>/dev/null || echo "Not available"', port)
    if ups_result['success']:
        ups_output = ups_result['stdout'].strip()
        if ups_output and 'Not available' not in ups_output and len(ups_output) > 20:
            print_pass("NAS에서 UPS 정보 조회 성공")
            result['storage']['ups_status'] = ups_output
            
            # 주요 정보만 출력
            lines = ups_output.split('\n')[:10]
            print("")
            for line in lines:
                if line.strip() and ':' in line:
                    print(f"    {line}")
        else:
            # synoups 시도 (시놀로지)
            syno_result = run_ssh_command(host, username, password, 'synoups --status 2>/dev/null || echo "Not available"', port)
            if syno_result['success'] and 'Not available' not in syno_result['stdout']:
                print_pass("NAS UPS 상태 (synoups)")
                result['storage']['ups_status'] = syno_result['stdout']
                print(f"    {syno_result['stdout'].strip()[:200]}")
            else:
                print_warning("NAS에서 UPS 정보를 가져올 수 없음")
                result['storage']['ups_status'] = "Not available"
    
    # 전체 상태 판정
    print("")
    if result['connection'] == 'Success':
        result['status'] = 'PASS'
        print_pass("NAS 점검 결과: PASS")
    else:
        result['status'] = 'FAIL'
        print_fail("NAS 점검 결과: FAIL")
    
    return result

