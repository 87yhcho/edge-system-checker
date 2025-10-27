#!/usr/bin/env python3
"""시스템 점검 모듈 테스트"""

print("모듈 import 테스트 시작...")

try:
    from checks.system_check import check_system_status
    print("✓ system_check 모듈 import 성공")
except Exception as e:
    print(f"✗ system_check 모듈 import 실패: {e}")
    exit(1)

try:
    from checks.ups_check import check_ups_status
    print("✓ ups_check 모듈 import 성공")
except Exception as e:
    print(f"✗ ups_check 모듈 import 실패: {e}")

try:
    from checks.camera_check import check_cameras
    print("✓ camera_check 모듈 import 성공")
except Exception as e:
    print(f"✗ camera_check 모듈 import 실패: {e}")

try:
    from checks.pg_check import check_postgresql
    print("✓ pg_check 모듈 import 성공")
except Exception as e:
    print(f"✗ pg_check 모듈 import 실패: {e}")

try:
    from checks.nas_check import check_nas_status
    print("✓ nas_check 모듈 import 성공")
except Exception as e:
    print(f"✗ nas_check 모듈 import 실패: {e}")

print("\n모든 모듈 import 완료!")
print("\n간단한 기능 테스트...")

# 시스템 명령어 테스트
from checks.system_check import run_command

# 간단한 명령어 테스트
result = run_command("echo 'test'")
if result['success']:
    print("✓ run_command 함수 정상 작동")
else:
    print("✗ run_command 함수 오류")

# OS 설정 확인 테스트
from checks.system_check import check_os_settings
print("\nOS 설정 확인 테스트...")
os_result = check_os_settings()
print(f"  - 타임존: {os_result.get('timezone', {}).get('status', 'UNKNOWN')}")
print(f"  - 로케일: {os_result.get('locale', {}).get('status', 'UNKNOWN')}")
print(f"  - 인코딩: {os_result.get('encoding', {}).get('status', 'UNKNOWN')}")

# 서비스 상태 확인 테스트
from checks.system_check import check_services
print("\n서비스 상태 확인 테스트...")
service_result = check_services()
for service, info in service_result.items():
    print(f"  - {service}: {info.get('state', 'unknown')}")

print("\n✓ 모든 테스트 완료!")

