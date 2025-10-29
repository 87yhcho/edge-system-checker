"""
리포트 생성 및 저장 모듈
점검 결과를 타임스탬프 포함 텍스트 파일로 저장
"""
import os
from datetime import datetime
from typing import Dict, Any


def generate_report(results: Dict[str, Any]) -> str:
    """점검 결과를 텍스트 리포트로 생성"""
    lines = []
    lines.append("=" * 80)
    lines.append("Edge 시스템 점검 리포트".center(80))
    lines.append("=" * 80)
    lines.append("")
    
    # 타임스탬프
    timestamp = results.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append(f"점검 시각: {timestamp}")
    lines.append("")
    
    # 전체 요약
    lines.append("-" * 80)
    lines.append("전체 요약")
    lines.append("-" * 80)
    summary = results.get('summary', {})
    for key, value in summary.items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    
    # UPS 점검 결과
    if 'ups' in results:
        lines.append("-" * 80)
        lines.append("[1/4] UPS/NUT 상태 점검")
        lines.append("-" * 80)
        ups = results['ups']
        lines.append(f"  상태: {ups.get('status', 'UNKNOWN')}")
        
        if 'services' in ups:
            lines.append("")
            lines.append("  NUT 서비스 상태:")
            for service, status in ups['services'].items():
                lines.append(f"    - {service}: {status}")
        
        if 'port' in ups:
            lines.append("")
            lines.append(f"  포트 리스닝: {ups['port']}")
        
        if 'ups_data' in ups:
            lines.append("")
            lines.append("  UPS 데이터:")
            for key, value in ups['ups_data'].items():
                lines.append(f"    - {key}: {value}")
        
        if 'nas_connection' in ups:
            lines.append("")
            lines.append(f"  NAS 연결: {ups['nas_connection']}")
        
        if 'error' in ups:
            lines.append("")
            lines.append(f"  오류: {ups['error']}")
        
        lines.append("")
    
    # 카메라 점검 결과
    if 'cameras' in results:
        lines.append("-" * 80)
        lines.append("[2/4] 카메라 RTSP 연결 점검")
        lines.append("-" * 80)
        cameras = results['cameras']
        lines.append(f"  점검 대수: {cameras.get('total', 0)}")
        lines.append(f"  PASS: {cameras.get('pass_count', 0)}")
        lines.append(f"  FAIL: {cameras.get('fail_count', 0)}")
        lines.append(f"  SKIP: {cameras.get('skip_count', 0)}")
        lines.append("")
        
        if 'details' in cameras:
            lines.append("  개별 카메라 상태:")
            lines.append(f"    {'카메라':<15} {'IP':<18} {'원본 영상':<12} {'블러 스트리밍':<12} {'로그':<12}")
            lines.append(f"    {'-' * 70}")
            for camera in cameras['details']:
                name = camera.get('name', 'Unknown')
                ip = camera.get('ip', 'N/A')
                source_status = camera.get('source_status', 'UNKNOWN')
                mediamtx_status = camera.get('mediamtx_status', 'UNKNOWN')
                log_status = camera.get('log_status', 'UNKNOWN')
                lines.append(f"    {name:<15} {ip:<18} {source_status:<12} {mediamtx_status:<12} {log_status:<12}")
                
                # 로그 상세 정보 추가
                if 'log_details' in camera and camera['log_details']:
                    log_details = camera['log_details']
                    if 'log_time' in log_details:
                        lines.append(f"      로그 시각: {log_details.get('log_time', 'N/A')}")
                    if 'frame_count' in log_details:
                        lines.append(f"      프레임 수: {log_details.get('frame_count', 'N/A')}")
                    if 'video_length' in log_details:
                        lines.append(f"      영상 길이: {log_details.get('video_length', 'N/A')}초")
                    if 'fail_reason' in log_details:
                        lines.append(f"      실패 원인: {log_details.get('fail_reason', 'N/A')}")
        
        # 영상 파일 확인 결과
        if 'video_files' in cameras:
            video_files = cameras['video_files']
            lines.append("")
            lines.append("  영상 파일 저장 확인:")
            lines.append(f"    상태: {video_files.get('status', 'UNKNOWN')}")
            
            if 'found_videos' in video_files and video_files['found_videos']:
                lines.append(f"    저장됨: 카메라 {video_files['found_videos']}")
            
            if 'missing_videos' in video_files and video_files['missing_videos']:
                lines.append(f"    누락됨: 카메라 {video_files['missing_videos']}")
        
        lines.append("")
    
    # PostgreSQL 점검 결과 (현재 비활성화)
    # if 'postgresql' in results:
    #     lines.append("-" * 80)
    #     lines.append("[3/4] PostgreSQL 데이터 수신 점검")
    #     lines.append("-" * 80)
    #     pg = results['postgresql']
    #     lines.append(f"  상태: {pg.get('status', 'UNKNOWN')}")
    #     lines.append(f"  연결: {pg.get('connection', 'Unknown')}")
    #     
    #     if 'table' in pg:
    #         lines.append(f"  테이블: {pg['table']}")
    #     
    #     if 'row_count' in pg:
    #         lines.append(f"  데이터 건수: {pg['row_count']}")
    #     
    #     if 'sample_data' in pg and pg['sample_data']:
    #         lines.append("")
    #         lines.append("  샘플 데이터 (최근 5건):")
    #         for i, row in enumerate(pg['sample_data'][:5], 1):
    #             lines.append(f"    {i}. {row}")
    #     
    #     if 'error' in pg:
    #         lines.append("")
    #         lines.append(f"  오류: {pg['error']}")
    #     
    #     lines.append("")
    
    # NAS 점검 결과
    if 'nas' in results:
        lines.append("-" * 80)
        lines.append("[3/4] NAS 상태 점검")
        lines.append("-" * 80)
        nas = results['nas']
        lines.append(f"  상태: {nas.get('status', 'UNKNOWN')}")
        lines.append(f"  연결: {nas.get('connection', 'Unknown')}")
        
        if 'system' in nas:
            lines.append("")
            lines.append("  시스템 정보:")
            for key, value in nas['system'].items():
                # 긴 출력은 줄바꿈
                if len(str(value)) > 60:
                    lines.append(f"    - {key}:")
                    lines.append(f"      {value}")
                else:
                    lines.append(f"    - {key}: {value}")
        
        if 'storage' in nas:
            lines.append("")
            lines.append("  스토리지 정보:")
            storage = nas['storage']
            if isinstance(storage, dict):
                for key, value in storage.items():
                    if len(str(value)) > 60:
                        lines.append(f"    - {key}:")
                        lines.append(f"      {value}")
                    else:
                        lines.append(f"    - {key}: {value}")
        
        if 'error' in nas:
            lines.append("")
            lines.append(f"  오류: {nas['error']}")
        
        lines.append("")
    
    # 시스템 종합 점검 결과
    if 'system' in results:
        lines.append("-" * 80)
        lines.append("[4/4] 시스템 종합 점검")
        lines.append("-" * 80)
        system = results['system']
        lines.append(f"  전체 상태: {system.get('status', 'UNKNOWN')}")
        lines.append("")
        
        # OS 설정 상세
        if 'os_settings' in system:
            lines.append("  [OS 설정]")
            for key, value in system['os_settings'].items():
                if isinstance(value, dict):
                    status_mark = "✓" if value.get('status') == 'PASS' else "✗" if value.get('status') == 'FAIL' else "⚠"
                    val = value.get('value', 'N/A')
                    status = value.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} {key.upper()}: {val} [{status}]")
                    if 'expected' in value and value.get('status') != 'PASS':
                        lines.append(f"      (권장: {value['expected']})")
            lines.append("")
        
        # 서비스 상태 상세
        if 'services' in system:
            lines.append("  [서비스 상태]")
            for service, info in system['services'].items():
                if isinstance(info, dict):
                    status_mark = "✓" if info.get('status') == 'PASS' else "✗" if info.get('status') == 'FAIL' else "⚠"
                    service_name = info.get('service', service)
                    state = info.get('state', 'unknown')
                    status = info.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} {service_name}: {state} [{status}]")
            lines.append("")
        
        # 포트 리스닝 상세
        if 'ports' in system:
            lines.append("  [포트 리스닝]")
            for port, info in system['ports'].items():
                if isinstance(info, dict):
                    status_mark = "✓" if info.get('listening') else "✗"
                    listening_status = "Listening" if info.get('listening') else "Not listening"
                    status = info.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} {port}: {listening_status} [{status}]")
                    if info.get('details') and info.get('listening'):
                        lines.append(f"      → {info['details'][:70]}")
            lines.append("")
        
        # Java 설정 상세
        if 'java' in system:
            lines.append("  [Java 설정]")
            for key, value in system['java'].items():
                if isinstance(value, dict):
                    status_mark = "✓" if value.get('status') == 'PASS' else "⚠" if value.get('status') == 'WARN' else "✗"
                    val = value.get('value', 'N/A')
                    status = value.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} {key.upper()}: {val} [{status}]")
                    if 'details' in value:
                        lines.append(f"      → {value['details'][:70]}")
            lines.append("")
        
        # 네트워크 상세
        if 'network' in system:
            lines.append("  [네트워크]")
            if 'ip_addresses' in system['network']:
                ip_info = system['network']['ip_addresses']
                status_mark = "✓" if ip_info.get('status') == 'PASS' else "✗"
                count = ip_info.get('count', 0)
                status = ip_info.get('status', 'UNKNOWN')
                lines.append(f"    {status_mark} IP 주소: {count}개 [{status}]")
                
                # 필수 IP 표시
                if 'required' in ip_info:
                    lines.append(f"      필수 IP:")
                    for req_ip in ip_info.get('required', []):
                        if req_ip in ip_info.get('found', []):
                            lines.append(f"        ✓ {req_ip} (확인됨)")
                        else:
                            lines.append(f"        ✗ {req_ip} (없음)")
                
                # 전체 IP 주소 목록
                lines.append(f"      감지된 IP:")
                for addr in ip_info.get('addresses', []):
                    lines.append(f"        → {addr}")
            
            if 'active_connections' in system['network']:
                conn_info = system['network']['active_connections']
                if conn_info.get('status') != 'SKIP':
                    status_mark = "✓" if conn_info.get('status') == 'PASS' else "✗"
                    count = conn_info.get('count', 0)
                    status = conn_info.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} 활성 연결: {count}개 [{status}]")
                    for name in conn_info.get('names', []):
                        lines.append(f"      → {name}")
            lines.append("")
        
        # 디스크 공간 상세
        if 'disk' in system:
            lines.append("  [디스크 공간]")
            if 'root' in system['disk']:
                root_info = system['disk']['root']
                status_mark = "✓" if root_info.get('status') == 'PASS' else "⚠" if root_info.get('status') == 'WARN' else "✗"
                usage = root_info.get('usage', 'N/A')
                avail = root_info.get('avail', 'N/A')
                size = root_info.get('size', 'N/A')
                status = root_info.get('status', 'UNKNOWN')
                lines.append(f"    {status_mark} 루트 파티션 (/): 사용률 {usage}, 여유 {avail}/{size} [{status}]")
            
            if 'postgresql' in system['disk']:
                pg_info = system['disk']['postgresql']
                if pg_info.get('status') != 'SKIP':
                    status_mark = "✓" if pg_info.get('status') == 'PASS' else "⚠"
                    usage = pg_info.get('usage', 'N/A')
                    avail = pg_info.get('avail', 'N/A')
                    status = pg_info.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} PostgreSQL: 사용률 {usage}, 여유 {avail} [{status}]")
            lines.append("")
        
        # Cron 작업 상세
        if 'cron' in system:
            lines.append("  [Cron 작업]")
            if 'crontab' in system['cron']:
                cron_info = system['cron']['crontab']
                if cron_info.get('status') != 'SKIP':
                    status_mark = "✓" if cron_info.get('status') == 'PASS' else "⚠"
                    count = cron_info.get('count', 0)
                    status = cron_info.get('status', 'UNKNOWN')
                    lines.append(f"    {status_mark} Crontab 작업: {count}개 [{status}]")
                    for job in cron_info.get('jobs', [])[:3]:
                        lines.append(f"      → {job[:70]}")
            
            if 'daily_sync' in system['cron']:
                sync_info = system['cron']['daily_sync']
                status_mark = "✓" if sync_info.get('status') == 'PASS' else "⚠"
                val = sync_info.get('value', 'N/A')
                status = sync_info.get('status', 'UNKNOWN')
                expected = sync_info.get('expected', '')
                lines.append(f"    {status_mark} 일일 동기화 (00:01 UTC): {val} [{status}]")
                if expected:
                    lines.append(f"      (기대값: {expected})")
            lines.append("")
        
        # 통계 요약
        if 'summary' in system:
            summary = system['summary']
            lines.append("  [점검 통계]")
            lines.append(f"    - PASS: {summary.get('pass_count', 0)}개")
            lines.append(f"    - FAIL: {summary.get('fail_count', 0)}개")
            lines.append(f"    - WARN: {summary.get('warn_count', 0)}개")
            lines.append(f"    - SKIP: {summary.get('skip_count', 0)}개")
            lines.append("")
        
        if 'error' in system:
            lines.append(f"  ⚠ 오류: {system['error']}")
            lines.append("")
    
    # 최종 결론
    lines.append("=" * 80)
    lines.append("점검 완료")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def save_report(results: Dict[str, Any], output_dir: str = ".") -> str:
    """리포트를 파일로 저장"""
    # reports 폴더 생성
    reports_dir = os.path.join(output_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{timestamp}.txt"
    filepath = os.path.join(reports_dir, filename)
    
    report_content = generate_report(results)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return filepath


def print_summary(results: Dict[str, Any]):
    """최종 요약을 콘솔에 출력"""
    from utils.ui import print_header, print_pass, print_fail, print_skip, print_info
    
    print_header("점검 완료")
    
    summary = results.get('summary', {})
    
    print_info("전체 요약:")
    for key, value in summary.items():
        # 카메라는 특별 처리 (상세 정보가 포함된 문자열)
        if key == "카메라":
            # "FAIL (PASS: 0, FAIL: 1, SKIP: 0)" 형태에서 상태만 추출
            status_only = str(value).split(' ')[0] if ' ' in str(value) else str(value)
            
            if status_only == 'PASS':
                print_pass(f"{key}: {value}")
            elif status_only == 'FAIL':
                print_fail(f"{key}: {value}")
            elif status_only == 'SKIP':
                print_skip(f"{key}: {value}")
            else:
                print(f"  {key}: {value}")
        else:
            # 다른 항목들
            if 'PASS' in str(value):
                print_pass(f"{key}: {value}")
            elif 'FAIL' in str(value):
                print_fail(f"{key}: {value}")
            elif 'SKIP' in str(value):
                print_skip(f"{key}: {value}")
            else:
                print(f"  {key}: {value}")
    
    print("")

