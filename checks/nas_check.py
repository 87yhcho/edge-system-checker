"""
NAS 상태 점검 모듈 (개선 버전 v2)
- SSH 세션 재사용으로 성능 향상
- 판정 로직 개선 (PASS/WARN/FAIL)
- 타임아웃 개별 설정
- 보안 강화 옵션
- Synology 경로 fallback
- 다국어 지원 (정규식 파싱)
- RAID 장애 검출 강화
- utils.ui 폴백 지원
"""
import paramiko
import re
from typing import Dict, Any, Optional


class NASChecker:
    """NAS 상태 체크 클래스 (세션 재사용)"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 2222, timeout: int = 30):
        """
        Args:
            port: SSH 포트 (기본값 2222 - Synology 커스텀 SSH 포트)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.fallback_port = 22  # 2222 실패 시 표준 SSH 포트로 재시도
        self.default_timeout = timeout
        self.ssh: Optional[paramiko.SSHClient] = None
        self.errors = []
        self.warnings = []
        self.connected_port = None  # 실제 연결된 포트 기록
        
    def connect(self) -> bool:
        """SSH 연결 (포트 fallback 지원)"""
        # 1차 시도: 설정된 포트 (기본 2222)
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh.connect(
                self.host, 
                port=self.port, 
                username=self.username, 
                password=self.password, 
                timeout=self.default_timeout,
                look_for_keys=False,
                allow_agent=False
            )
            self.connected_port = self.port
            return True
        except Exception as e:
            first_error = str(e)
            
            # 2차 시도: fallback 포트 (22)
            if self.port != self.fallback_port:
                try:
                    self.ssh = paramiko.SSHClient()
                    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    self.ssh.connect(
                        self.host, 
                        port=self.fallback_port, 
                        username=self.username, 
                        password=self.password, 
                        timeout=self.default_timeout,
                        look_for_keys=False,
                        allow_agent=False
                    )
                    self.connected_port = self.fallback_port
                    self.warnings.append(f"포트 {self.port} 실패, 포트 {self.fallback_port}로 연결 성공")
                    return True
                except Exception as e2:
                    self.errors.append(f"SSH 연결 실패 (포트 {self.port}: {first_error}, 포트 {self.fallback_port}: {str(e2)})")
                    return False
            else:
                self.errors.append(f"SSH 연결 실패: {first_error}")
                return False
    
    def close(self):
        """SSH 연결 종료"""
        if self.ssh:
            try:
                self.ssh.close()
            except:
                pass
            self.ssh = None
    
    def exec_command(self, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        명령 실행 (기존 세션 재사용)
        
        Args:
            command: 실행할 명령
            timeout: 명령별 타임아웃 (None이면 기본값 사용)
        """
        if not self.ssh:
            return {
                'success': False,
                'error': 'SSH 연결이 없습니다',
                'stdout': '',
                'stderr': '',
                'exit_code': -1
            }
        
        try:
            cmd_timeout = timeout if timeout is not None else self.default_timeout
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=cmd_timeout)
            
            stdout_text = stdout.read().decode('utf-8', errors='ignore')
            stderr_text = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'success': exit_code == 0,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'exit_code': exit_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1
            }
    
    def check_system(self) -> Dict[str, Any]:
        """시스템 정보 체크"""
        result = {}
        commands = {
            'hostname': ('hostname', 5),
            'uptime': ('uptime', 5),
            'load_average': ('cat /proc/loadavg', 5),
        }
        
        for key, (cmd, timeout) in commands.items():
            res = self.exec_command(cmd, timeout)
            if res['success']:
                result[key] = res['stdout'].strip()
            else:
                result[key] = f"Error: {res.get('error', res['stderr'])}"
                self.warnings.append(f"시스템 정보({key}) 조회 실패")
        
        return result
    
    def check_storage(self) -> Dict[str, Any]:
        """스토리지 정보 체크"""
        result = {
            'raid_status': None,
            'raid_info': {},  # RAID 정보 요약 (디스크 개수, 용량 등)
            'disk_usage': None,
            'critical_issues': []
        }
        
        # RAID 상태 (중요 - 긴 타임아웃)
        raid = self.exec_command('cat /proc/mdstat', timeout=30)
        if raid['success']:
            result['raid_status'] = raid['stdout'].strip()
            
            # RAID 장애 검출 개선: [x/y] [UU_U] 패턴 정확히 파싱
            # 예: "md1 : active raid1 ... 2097088 blocks [4/3] [UUU_]"
            #     → [4/3]는 "4개 슬롯 중 3개 사용", [UUU_]는 3개 활성 + 1개 빈 슬롯
            #     → 실제 사용 디스크(3개)와 활성 디스크(U 3개)가 일치하면 정상
            
            # 각 md 디바이스별로 검사
            for line in raid['stdout'].splitlines():
                # RAID 상태 라인: "md0 : active raid1 ... blocks [4/3] [UUU_]"
                device_match = re.search(r'(md\d+)\s*:\s*active\s+(raid\d+)', line)
                if not device_match:
                    continue
                
                device_name = device_match.group(1)
                raid_level = device_match.group(2)  # raid1, raid5, raid6 등
                
                # 블록 수 추출 (총 용량 계산용)
                blocks_match = re.search(r'(\d+)\s+blocks', line)
                blocks = int(blocks_match.group(1)) if blocks_match else 0
                # 블록은 보통 1KB이므로 GB로 변환
                capacity_gb = blocks / 1024 / 1024 if blocks > 0 else 0
                
                # [x/y] 패턴: 전체 슬롯 수 / 실제 사용 디스크 수
                slot_match = re.search(r'\[(\d+)/(\d+)\]', line)
                # [U_] 패턴: 활성 상태
                state_match = re.search(r'\[([U_]+)\]', line)
                
                if slot_match and state_match:
                    total_slots = int(slot_match.group(1))
                    active_disks = int(slot_match.group(2))
                    raid_state = state_match.group(1)
                    
                    active_count = raid_state.count('U')
                    failed_count = raid_state.count('_')
                    
                    # RAID 정보 저장
                    result['raid_info'][device_name] = {
                        'level': raid_level,
                        'capacity_gb': capacity_gb,
                        'disk_count': active_disks,
                        'status': raid_state,
                        'active': active_count
                    }
                    
                    # 실제 장애 판단: 사용 중인 디스크 수와 활성(U) 개수가 다르면 장애
                    if active_count != active_disks:
                        issue = f"{device_name}: RAID 디스크 장애 - {active_disks}개 중 {active_count}개만 활성 [{raid_state}]"
                        result['critical_issues'].append(issue)
                        self.errors.append(issue)
                    # [UUU_]처럼 _ 있지만 실제로는 빈 슬롯일 뿐 (정상)
                    elif failed_count > 0 and active_count == active_disks:
                        # 정보성 메시지 (에러 아님)
                        pass
                elif state_match:
                    # [x/y] 패턴 없이 [UU_] 패턴만 있는 경우
                    raid_state = state_match.group(1)
                    if '_' in raid_state:
                        # 보수적으로 경고 처리
                        failed_count = raid_state.count('_')
                        total_count = len(raid_state)
                        warning = f"{device_name}: RAID 상태 확인 필요 [{raid_state}] (_{failed_count}/{total_count})"
                        result['critical_issues'].append(warning)
                        self.warnings.append(warning)
            
            # 추가: "FAILED" 키워드 명시적 체크
            if 'FAILED' in raid['stdout'].upper() or '(F)' in raid['stdout']:
                issue = "RAID 장애 상태 (FAILED)"
                if issue not in result['critical_issues']:
                    result['critical_issues'].append(issue)
                    self.errors.append(issue)
        else:
            result['raid_status'] = 'N/A (SW RAID 없음)'
        
        # 디스크 사용량 (중요 - 긴 타임아웃) - 견고한 파싱
        df = self.exec_command('df -h', timeout=30)
        if df['success']:
            result['disk_usage'] = df['stdout']
            
            # 정규식으로 % 추출 (로케일/BusyBox 호환)
            percent_pattern = re.compile(r'(\d{1,3})%')
            
            for line in df['stdout'].splitlines():
                if not line.strip():
                    continue
                
                # 헤더 스킵 (Filesystem, 파일시스템 등)
                if 'Filesystem' in line or '파일시스템' in line or line.startswith('Filesystem'):
                    continue
                
                # % 패턴 찾기
                percent_match = percent_pattern.search(line)
                if percent_match:
                    try:
                        use_percent = int(percent_match.group(1))
                        
                        # 마운트 포인트 추출 (마지막 공백으로 분리된 부분)
                        parts = line.split()
                        if len(parts) >= 2:
                            # 일반적으로 마지막 필드가 마운트 포인트
                            mountpoint = parts[-1]
                            
                            # 판정
                            if use_percent >= 90:
                                issue = f"{mountpoint} 디스크 사용량 {use_percent}% (위험)"
                                result['critical_issues'].append(issue)
                                self.errors.append(issue)
                            elif use_percent >= 80:
                                warning = f"{mountpoint} 디스크 사용량 {use_percent}% (경고)"
                                result['critical_issues'].append(warning)
                                self.warnings.append(warning)
                    except (ValueError, IndexError):
                        pass
        else:
            self.warnings.append("디스크 사용량 조회 실패")
        
        return result
    
    def check_ups(self) -> Dict[str, Any]:
        """
        UPS 상태 체크 (시놀로지 우선, 경로 fallback)
        
        참고: NAS가 원격 NUT 서버(엣지 PC 등)를 사용하는 경우,
        NAS 로컬에서 UPS 정보를 조회할 수 없는 것이 정상입니다.
        이 경우 NOT_AVAILABLE은 오류가 아닙니다.
        """
        result = {
            'status': 'UNKNOWN',
            'details': {},
            'issues': []
        }
        
        # 1순위: 시놀로지 UPS 명령 (경로 fallback)
        # PATH 검색 → 절대경로 fallback
        synoups_cmd = 'synoups --status 2>/dev/null || /usr/syno/sbin/synoups --status 2>/dev/null'
        synoups = self.exec_command(synoups_cmd, timeout=10)
        
        if synoups['success'] and synoups['stdout'].strip():
            result['status'] = 'AVAILABLE'
            result['details']['synoups'] = synoups['stdout'].strip()
            
            # UPS 배터리 체크 (다국어 대응 - 정규식 사용)
            # "Battery Charge: 85%", "배터리 충전: 85%" 등 모두 대응
            battery_pattern = re.compile(r'(\d{1,3})\s*%')
            
            for line in synoups['stdout'].splitlines():
                # 배터리 관련 라인 찾기 (키워드 다국어 대응)
                if any(keyword in line.lower() for keyword in ['battery', 'charge', '배터리', '충전']):
                    battery_match = battery_pattern.search(line)
                    if battery_match:
                        try:
                            charge = int(battery_match.group(1))
                            # 100 이하만 배터리로 판단 (잘못된 파싱 방지)
                            if charge <= 100:
                                if charge < 50:
                                    warning = f"UPS 배터리 충전량 낮음: {charge}%"
                                    result['issues'].append(warning)
                                    self.warnings.append(warning)
                                break  # 첫 배터리 정보만 사용
                        except:
                            pass
        else:
            # 2순위: NUT upsc 명령
            upsc = self.exec_command('upsc ups@localhost 2>/dev/null', timeout=10)
            if upsc['success'] and upsc['stdout'].strip() and len(upsc['stdout']) > 20:
                result['status'] = 'NUT_AVAILABLE'
                result['details']['nut'] = upsc['stdout'].strip()
                
                # NUT에서도 배터리 체크
                battery_pattern = re.compile(r'battery\.charge:\s*(\d{1,3})')
                battery_match = battery_pattern.search(upsc['stdout'])
                if battery_match:
                    try:
                        charge = int(battery_match.group(1))
                        if charge < 50:
                            warning = f"UPS 배터리 충전량 낮음: {charge}%"
                            result['issues'].append(warning)
                            self.warnings.append(warning)
                    except:
                        pass
            else:
                result['status'] = 'NOT_AVAILABLE'
                result['details']['message'] = 'UPS 정보 없음 (원격 NUT 서버 사용 중일 수 있음)'
        
        return result


def check_nas_status(nas_config: Dict[str, str]) -> Dict[str, Any]:
    """전체 NAS 점검 실행 (개선 버전 v2 - utils.ui 폴백 지원)"""
    
    # utils.ui import 시도 (실패 시 폴백)
    try:
        from utils.ui import (
            print_section, print_pass, print_fail, print_info,
            print_warning, print_key_value
        )
        UI_AVAILABLE = True
    except ImportError:
        # utils.ui 없을 때 폴백 함수
        UI_AVAILABLE = False
        
        def print_section(current, total, title):
            print(f"\n{'='*60}")
            print(f"[{current}/{total}] {title}")
            print('='*60)
        
        def print_pass(msg):
            print(f"✓ {msg}")
        
        def print_fail(msg):
            print(f"✗ {msg}")
        
        def print_info(msg):
            print(f"ℹ {msg}")
        
        def print_warning(msg):
            print(f"⚠ {msg}")
        
        def print_key_value(key, value, status):
            status_icon = "✓" if status == 'PASS' else "✗"
            print(f"  {status_icon} {key}: {value}")
    
    print_section(4, 4, "NAS 상태 점검")
    
    # 설정 정보 (포트 기본값 2222 - Synology 커스텀 SSH 포트)
    host = nas_config.get('ip', '192.168.10.30')
    username = nas_config.get('user', 'admin')
    password = nas_config.get('password', '')
    # 포트: .env에서 명시하지 않으면 2222 (커스텀), 명시하면 해당 값 사용
    port = int(nas_config.get('port', 2222))
    
    print_info(f"연결 정보: {username}@{host}:{port} (실패 시 포트 22로 재시도)")
    
    result = {
        'status': 'UNKNOWN',
        'connection': 'Not tested',
        'system': {},
        'storage': {},
        'ups': {},
        'errors': [],
        'warnings': []
    }
    
    # NASChecker 인스턴스 생성
    checker = NASChecker(
        host=host,
        username=username,
        password=password,
        port=port,
        timeout=30
    )
    
    try:
        # 1. SSH 연결 테스트
        print_info("SSH 연결 테스트 중...")
        
        if not checker.connect():
            print_fail(f"연결 실패: {checker.errors[0] if checker.errors else 'Unknown error'}")
            result['status'] = 'FAIL'
            result['connection'] = 'Failed'
            result['errors'] = checker.errors
            return result
        
        # 연결된 포트 정보 출력
        if checker.connected_port:
            print_pass(f"SSH 연결 성공 (포트 {checker.connected_port})")
        else:
            print_pass("SSH 연결 성공")
        result['connection'] = 'Success'
        result['connected_port'] = checker.connected_port
        
        # 2. 시스템 정보 수집
        print("")
        print_info("시스템 정보 수집 중...")
        system_info = checker.check_system()
        result['system'] = system_info
        
        for key, value in system_info.items():
            if value and not value.startswith("Error"):
                print_key_value(key, value[:60], 'PASS')
            else:
                print_key_value(key, value, 'FAIL')
        
        # 3. 스토리지 정보 확인
        print("")
        print_info("스토리지 정보 확인 중...")
        storage_info = checker.check_storage()
        result['storage'] = storage_info
        
        # 디스크 사용량 출력
        if storage_info.get('disk_usage'):
            print_pass("디스크 사용량 조회 성공")
            print("")
            print("  주요 볼륨:")
            lines = storage_info['disk_usage'].split('\n')
            for line in lines[:10]:
                if line.strip():
                    print(f"    {line}")
        else:
            print_warning("디스크 사용량 조회 실패")
        
        # RAID 상태 출력
        print("")
        print_info("RAID 상태 확인 중...")
        if storage_info.get('raid_status') and storage_info['raid_status'] != 'N/A (SW RAID 없음)':
            if any('RAID 디스크 실패' in issue for issue in storage_info.get('critical_issues', [])):
                print_fail("⚠️  RAID 디스크 실패 감지!")
            else:
                print_pass("RAID 상태 정상")
            
            # RAID 정보 요약 출력
            if storage_info.get('raid_info'):
                print("")
                print("  RAID 구성 정보:")
                for device, info in storage_info['raid_info'].items():
                    raid_level = info['level']
                    disk_count = info['disk_count']
                    capacity = info['capacity_gb']
                    
                    # RAID 레벨 한글 표시
                    level_map = {
                        'raid0': 'RAID 0 (스트라이핑)',
                        'raid1': 'RAID 1 (미러링)',
                        'raid5': 'RAID 5',
                        'raid6': 'RAID 6',
                        'raid10': 'RAID 10'
                    }
                    level_name = level_map.get(raid_level, raid_level.upper())
                    
                    if capacity >= 1000:
                        capacity_str = f"{capacity/1000:.1f}TB"
                    else:
                        capacity_str = f"{capacity:.1f}GB"
                    
                    print(f"    {device}: {level_name}")
                    print(f"      - 디스크 개수: {disk_count}개")
                    print(f"      - 총 용량: {capacity_str}")
                    print(f"      - 상태: {info['status']}")
            
            print("")
            print("  상세 RAID 상태:")
            lines = storage_info['raid_status'].split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"    {line}")
        else:
            print_warning("RAID 정보가 없습니다 (소프트웨어 RAID 미사용)")
        
        # 4. UPS 상태 확인
        print("")
        print_info("NAS UPS 상태 확인 중...")
        ups_info = checker.check_ups()
        result['ups'] = ups_info
        
        if ups_info['status'] == 'AVAILABLE':
            print_pass("NAS UPS 상태 (synoups)")
            if ups_info['details'].get('synoups'):
                output = ups_info['details']['synoups']
                print("")
                for line in output.split('\n')[:10]:
                    if line.strip():
                        print(f"    {line}")
        elif ups_info['status'] == 'NUT_AVAILABLE':
            print_pass("NAS UPS 상태 (NUT)")
            if ups_info['details'].get('nut'):
                output = ups_info['details']['nut']
                print("")
                for line in output.split('\n')[:10]:
                    if line.strip() and ':' in line:
                        print(f"    {line}")
        else:
            # NOT_AVAILABLE: 원격 NUT 서버를 사용하는 경우 정상
            print_info("NAS 로컬 UPS 정보 없음 (원격 NUT 서버 사용 중)")
            print_info("  → 엣지 PC의 NUT 서버에 연결된 경우 정상입니다.")
        
        # 5. 오류/경고 집계
        result['errors'] = checker.errors
        result['warnings'] = checker.warnings
        
        # 6. 최종 판정
        print("")
        if checker.errors:
            result['status'] = 'FAIL'
            print_fail(f"NAS 점검 결과: FAIL (오류 {len(checker.errors)}개)")
            for error in checker.errors:
                print_fail(f"  - {error}")
        elif checker.warnings:
            result['status'] = 'WARN'
            print_warning(f"NAS 점검 결과: WARN (경고 {len(checker.warnings)}개)")
            for warning in checker.warnings:
                print_warning(f"  - {warning}")
        else:
            result['status'] = 'PASS'
            print_pass("NAS 점검 결과: PASS")
    
    finally:
        # 연결 종료
        checker.close()
    
    return result
