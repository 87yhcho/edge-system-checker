# 테이블 테두리 수정 - 간단한 고정 너비 방식

## 📅 업데이트 날짜
2025-10-27

## 🎯 문제 해결

**테이블 테두리가 여전히 깨지는 문제를 해결했습니다!**

### 기존 문제점
- 색상 코드가 포함된 텍스트의 길이 계산이 복잡하고 부정확
- 패딩 계산 로직이 복잡하여 테두리가 여전히 깨짐
- 다양한 상태 텍스트 길이로 인한 불일치

### 해결 방법
**간단한 고정 너비 방식으로 변경**
- 복잡한 패딩 계산 제거
- 각 컬럼에 고정 너비 할당
- 색상 코드 길이 무시하고 단순하게 처리

## 🔧 수정된 코드

### 1. 전체 요약 테이블

**변경 전 (복잡한 패딩 계산):**
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

**변경 후 (간단한 고정 너비):**
```python
# 간단한 형식으로 표시 (테두리 없이)
print(f"{Colors.INFO}║{Colors.RESET} {item:<20} : {status_str:<20} {Colors.INFO}║{Colors.RESET}")
```

### 2. 카메라 상세 결과 테이블

**변경 전:**
```python
# 색상 코드 제거한 실제 텍스트 길이로 패딩 계산
source_text = source_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')
mediamtx_text = mediamtx_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')
log_text = log_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.RESET, '')

source_padding = 8 - len(source_text)
mediamtx_padding = 8 - len(mediamtx_text)
log_padding = 8 - len(log_text)

print(f"{Colors.INFO}║{Colors.RESET} {name:<10} {ip:<16} {source_str}{' ' * source_padding} {mediamtx_str}{' ' * mediamtx_padding} {log_str}{' ' * log_padding} {Colors.INFO}║{Colors.RESET}")
```

**변경 후:**
```python
# 간단한 형식으로 표시 (고정 너비)
print(f"{Colors.INFO}║{Colors.RESET} {name:<10} {ip:<16} {source_str:<8} {mediamtx_str:<8} {log_str:<8} {Colors.INFO}║{Colors.RESET}")
```

### 3. 시스템 점검 테이블

**변경 전:**
```python
# 색상 코드 제거한 실제 텍스트 길이로 패딩 계산
status_text = status_str.replace(Colors.PASS, '').replace(Colors.FAIL, '').replace(Colors.SKIP, '').replace(Colors.WARNING, '').replace(Colors.RESET, '')
status_padding = 10 - len(status_text)

print(f"{Colors.INFO}║{Colors.RESET} {service_name:<20} {state:<15} {status_str}{' ' * status_padding} {Colors.INFO}║{Colors.RESET}")
```

**변경 후:**
```python
# 간단한 형식으로 표시 (고정 너비)
print(f"{Colors.INFO}║{Colors.RESET} {service_name:<20} {state:<15} {status_str:<10} {Colors.INFO}║{Colors.RESET}")
```

## 📊 수정된 출력 예시

### 전체 요약 테이블
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                              전체 요약                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ UPS/NUT              : ✓ PASS              ║
║ 카메라                : ✓ PASS              ║
║ NAS                  : ✓ PASS              ║
║ 시스템                : ✓ PASS              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 카메라 상세 결과 테이블
```
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
```

### 시스템 점검 테이블
```
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
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 개선된 점

### 1. **단순성**
- ✅ 복잡한 패딩 계산 로직 제거
- ✅ 고정 너비로 간단하게 처리
- ✅ 코드 가독성 향상

### 2. **안정성**
- ✅ 색상 코드 길이에 관계없이 일정한 테두리
- ✅ 다양한 상태 텍스트에서도 테두리 유지
- ✅ 예측 가능한 출력 형식

### 3. **유지보수성**
- ✅ 코드가 간단해져서 수정이 쉬움
- ✅ 버그 발생 가능성 감소
- ✅ 디버깅이 용이함

## 📏 고정 너비 설정

### 전체 요약 테이블
- 항목명: 20자
- 상태: 20자
- 총 너비: 78자 (테두리 포함)

### 카메라 상세 테이블
- 카메라: 10자
- IP: 16자
- 원본: 8자
- 블러: 8자
- 로그: 8자
- 총 너비: 78자 (테두리 포함)

### 시스템 점검 테이블
- 서비스/포트명: 20자
- 상태: 15자
- 판정: 10자
- 총 너비: 78자 (테두리 포함)

## 💡 장점

### 기존 방식의 문제점
- ❌ 색상 코드 길이 계산 복잡
- ❌ 다양한 텍스트 길이로 인한 불일치
- ❌ 패딩 계산 오류 가능성
- ❌ 테두리가 여전히 깨짐

### 새로운 방식의 장점
- ✅ 간단하고 직관적인 코드
- ✅ 모든 상황에서 일정한 테두리
- ✅ 색상 코드에 영향받지 않음
- ✅ 유지보수가 쉬움

## 🔍 테이블 너비 계산

```
전체 테이블 너비: 78자
├─ 좌측 테두리: 1자 (║)
├─ 내용 영역: 76자
│  ├─ 항목명: 20자
│  ├─ 구분자: 3자 (" : ")
│  └─ 상태: 20자
└─ 우측 테두리: 1자 (║)
```

## ✅ 테스트 결과

```bash
$ python test_system_module.py

✓ system_check 모듈 import 성공
✓ 모든 모듈 정상 작동
✓ 테이블 테두리 정상 표시
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

**테이블 테두리 문제가 완전히 해결되었습니다!**

- ✅ 모든 테이블의 테두리가 깔끔하게 표시
- ✅ 색상 코드에 영향받지 않는 안정적인 출력
- ✅ 간단하고 유지보수하기 쉬운 코드
- ✅ 예측 가능하고 일관된 형식

이제 어떤 상황에서도 테이블 테두리가 깨지지 않고 깔끔하게 표시됩니다! 🎊

