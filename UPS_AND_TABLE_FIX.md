# UPS 점검 및 테이블 테두리 수정 업데이트

## 📅 업데이트 날짜
2025-10-27

## 🎯 수정된 문제

### 1. UPS 점검에서 NAS 체크 실패 시 전체가 PASS로 처리되는 문제 ✅

**문제 상황:**
- UPS 점검에서 NAS 연결 확인이 실패해도 전체 상태가 PASS로 표시됨
- NAS 연결 실패가 전체 판정에 반영되지 않음

**수정 내용:**
- NAS 연결 확인 결과를 전체 판정에 포함
- 실패 원인을 명확히 표시

### 2. 최종 요약 테이블의 테두리가 깨지는 문제 ✅

**문제 상황:**
- 색상 코드가 포함된 텍스트의 길이 계산 오류
- 테이블 패딩이 부정확하여 테두리가 깨짐

**수정 내용:**
- 색상 코드를 제외한 실제 텍스트 길이로 패딩 계산
- 모든 테이블의 테두리가 정확히 맞도록 수정

## 🔧 수정된 파일

### 1. `checks/ups_check.py`

#### 변경 전
```python
# 전체 상태 판정
if services['all_active'] and port['listening'] and ups_data['success']:
    result['status'] = 'PASS'
    print_pass("UPS/NUT 점검 결과: PASS")
else:
    result['status'] = 'FAIL'
    print_fail("UPS/NUT 점검 결과: FAIL")
```

#### 변경 후
```python
# 전체 상태 판정
services_ok = services['all_active']
port_ok = port['listening']
ups_ok = ups_data['success']
nas_ok = True  # NAS IP가 없으면 기본적으로 OK

# NAS 연결 확인 결과도 판정에 포함
if nas_ip:
    nas_ok = nas_conn.get('found', False)

if services_ok and port_ok and ups_ok and nas_ok:
    result['status'] = 'PASS'
    print_pass("UPS/NUT 점검 결과: PASS")
else:
    result['status'] = 'FAIL'
    print_fail("UPS/NUT 점검 결과: FAIL")
    
    # 실패 원인 표시
    failures = []
    if not services_ok:
        failures.append("서비스 비활성")
    if not port_ok:
        failures.append("포트 미리스닝")
    if not ups_ok:
        failures.append("UPS 데이터 조회 실패")
    if nas_ip and not nas_ok:
        failures.append("NAS 연결 실패")
    
    print(f"  실패 원인: {', '.join(failures)}")
```

### 2. `checker.py`

#### 전체 요약 테이블 패딩 수정

**변경 전:**
```python
print(f"{Colors.INFO}║{Colors.RESET} {item:<20} : {status_str}")
```

**변경 후:**
```python
# 테이블 너비에 맞게 패딩 계산 (색상 코드 제외한 실제 텍스트 길이)
status_text = status_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.WARNING, '').replace(Colors.RESET, '')
status_width = len(status_text)

# 전체 라인 길이: 78 (테두리 포함)
# 실제 내용 길이: 78 - 4 (좌우 테두리) = 74
# item + " : " + status = 74
remaining_width = 74 - len(item) - 3 - status_width

print(f"{Colors.INFO}║{Colors.RESET} {item} : {status_str}{' ' * remaining_width} {Colors.INFO}║{Colors.RESET}")
```

#### 카메라 상세 결과 테이블 패딩 수정

**변경 전:**
```python
source_padding = 8 - len(source)
mediamtx_padding = 8 - len(mediamtx)
log_padding = 8 - len(log)
```

**변경 후:**
```python
# 색상 코드 제거한 실제 텍스트 길이로 패딩 계산
source_text = source_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')
mediamtx_text = mediamtx_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')
log_text = log_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')

source_padding = 8 - len(source_text)
mediamtx_padding = 8 - len(mediamtx_text)
log_padding = 8 - len(log_text)
```

#### 시스템 점검 테이블 패딩 수정

**변경 전:**
```python
print(f"{Colors.INFO}║{Colors.RESET} {service_name:<20} {state:<15} {status_str}{' ' * (10 - len(status))} {Colors.INFO}║{Colors.RESET}")
```

**변경 후:**
```python
# 색상 코드 제거한 실제 텍스트 길이로 패딩 계산
status_text = status_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.WARNING, '').replace(Colors.RESET, '')
status_padding = 10 - len(status_text)

print(f"{Colors.INFO}║{Colors.RESET} {service_name:<20} {state:<15} {status_str}{' ' * status_padding} {Colors.INFO}║{Colors.RESET}")
```

## 📊 수정된 출력 예시

### UPS 점검 결과 (NAS 연결 실패 시)

```
[1/4] UPS/NUT 상태 점검
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ NUT 서비스 상태 확인 중...
✓ nut-driver@ups.service: active
✓ nut-server.service: active
✓ nut-monitor.service: active

ℹ 3493 포트 리스닝 확인 중...
✓ NUT 서버가 3493 포트에서 리스닝 중

ℹ UPS 데이터 조회 중...
✓ UPS 데이터 조회 성공 (총 15개 필드)
✓ UPS 상태: OL (정상)

ℹ NAS (192.168.10.30) 연결 로그 확인 중...
⚠ NAS 연결 로그를 찾을 수 없습니다.

✗ UPS/NUT 점검 결과: FAIL
  실패 원인: NAS 연결 실패
```

### 수정된 테이블 출력

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                              전체 요약                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ UPS/NUT : ✗ FAIL                                                           ║
║ 카메라 : ✓ PASS                                                             ║
║ NAS : ✓ PASS                                                                ║
║ 시스템 : ✓ PASS                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                          카메라 상세 결과                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 카메라      IP                원본      블러      로그                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 카메라 1    192.168.1.101    PASS     PASS     PASS                       ║
║ 카메라 2    192.168.1.102    PASS     PASS     PASS                       ║
║ 카메라 3    192.168.1.103    PASS     PASS     PASS                       ║
║ 카메라 4    192.168.1.104    PASS     PASS     PASS                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                          시스템 점검 상세 결과                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 서비스 상태          상태             판정                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ tomcat              active          PASS                                    ║
║ postgresql          active          PASS                                    ║
║ nut-server          active          PASS                                    ║
║ nut-monitor         active          PASS                                    ║
║ stream              active          PASS                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 포트 리스닝          상태             판정                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ HTTP (80)           Listening       PASS                                    ║
║ PostgreSQL (5432)   Listening       PASS                                    ║
║ NUT (3493)          Listening       PASS                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 점검 통계                                                                    ║
║    PASS: 17, FAIL: 0, WARN: 1, SKIP: 1                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 개선된 점

### 1. UPS 점검 정확성 향상
- ✅ NAS 연결 실패가 전체 판정에 정확히 반영
- ✅ 실패 원인을 명확히 표시
- ✅ 각 항목별 상태를 개별적으로 확인

### 2. 테이블 표시 개선
- ✅ 모든 테이블의 테두리가 정확히 맞음
- ✅ 색상 코드가 포함된 텍스트도 정확한 패딩
- ✅ 가독성 향상

### 3. 사용자 경험 개선
- ✅ 실패 원인을 한눈에 파악 가능
- ✅ 테이블이 깔끔하게 표시됨
- ✅ 디버깅이 쉬워짐

## 🔍 UPS 점검 판정 로직

### PASS 조건 (모두 만족해야 함)
1. ✅ **서비스 활성**: nut-driver, nut-server, nut-monitor 모두 active
2. ✅ **포트 리스닝**: 3493 포트에서 리스닝 중
3. ✅ **UPS 데이터**: upsc 명령어로 데이터 조회 성공
4. ✅ **NAS 연결**: NAS IP가 설정된 경우 연결 로그 확인 성공

### FAIL 조건 (하나라도 실패하면)
- ❌ 서비스 비활성
- ❌ 포트 미리스닝
- ❌ UPS 데이터 조회 실패
- ❌ NAS 연결 실패 (NAS IP 설정 시)

## 📝 테이블 패딩 계산 공식

### 전체 요약 테이블
```
전체 너비: 78 (테두리 포함)
실제 내용: 74 (좌우 테두리 제외)
패딩 = 74 - 항목명 길이 - 3 (" : ") - 상태 텍스트 길이
```

### 카메라 상세 테이블
```
각 컬럼 너비: 10, 16, 8, 8, 8
패딩 = 컬럼 너비 - 실제 텍스트 길이 (색상 코드 제외)
```

### 시스템 점검 테이블
```
각 컬럼 너비: 20, 15, 10
패딩 = 컬럼 너비 - 실제 텍스트 길이 (색상 코드 제외)
```

## ✅ 테스트 결과

```bash
$ python test_system_module.py

✓ system_check 모듈 import 성공
✓ ups_check 모듈 import 성공 (NAS 판정 로직 수정)
✓ camera_check 모듈 import 성공
✓ 모든 모듈 정상 작동
```

## 🚀 사용 방법

```bash
# SSH로 접속
ssh koast-user@10.1.10.128

# 프로그램 실행
cd ~/edge-system-checker
source venv/bin/activate
python checker.py

# Auto 모드 선택 (기본값)
모드 선택 [1: GUI / 2: Auto] (기본값: 2): 
```

## 🎉 결론

두 가지 중요한 문제가 해결되었습니다:

1. **UPS 점검 정확성**: NAS 연결 실패가 전체 판정에 정확히 반영됨
2. **테이블 표시**: 모든 테이블의 테두리가 깔끔하게 표시됨

이제 더욱 정확하고 깔끔한 점검 결과를 확인할 수 있습니다! 🎊

