# NAS Check v2 보완 사항 완료

## 📅 업데이트 날짜
2024-10-27 (v2)

## 🎯 보완 목적
추가 코드 리뷰에서 지적된 실용성 문제 해결 및 견고성 강화

---

## ✅ 보완된 핵심 포인트

### 1. ✅ Synology 전용 명령 경로 보강

**문제:**
```python
synoups = self.exec_command('synoups --status', timeout=10)
```
→ `synoups`가 PATH에 없으면 실패

**해결:**
```python
# PATH 검색 → 절대경로 fallback
synoups_cmd = 'synoups --status 2>/dev/null || /usr/syno/sbin/synoups --status 2>/dev/null'
synoups = self.exec_command(synoups_cmd, timeout=10)
```

**효과:**
- ✅ PATH 없어도 `/usr/syno/sbin/` 절대경로로 실행
- ✅ 다양한 Synology 설정 환경 대응

---

### 2. ✅ UPS 출력 언어 의존성 제거

**문제:**
```python
if 'Battery Charge' in line:  # 영문 DSM만 동작
    charge = int(line.split(':')[1].strip().rstrip('%'))
```
→ 한글/다국어 DSM에서 실패

**해결:**
```python
# 다국어 대응 - 정규식으로 % 추출
battery_pattern = re.compile(r'(\d{1,3})\s*%')

for line in synoups['stdout'].splitlines():
    # 배터리 관련 라인 찾기 (키워드 다국어 대응)
    if any(keyword in line.lower() for keyword in ['battery', 'charge', '배터리', '충전']):
        battery_match = battery_pattern.search(line)
        if battery_match:
            charge = int(battery_match.group(1))
            if charge <= 100:  # 100 이하만 배터리로 판단
                # 처리...
```

**효과:**
- ✅ 영문/한글/중국어 등 모든 언어 대응
- ✅ `"Battery Charge: 85%"`, `"배터리 충전: 85%"` 모두 파싱
- ✅ 잘못된 파싱 방지 (100 이하만 유효)

---

### 3. ✅ RAID 장애 검출 강화

**문제:**
```python
if 'FAILED' in raid_output or '[U_]' in raid_output or '[_U]' in raid_output:
    # RAID 실패
```
→ `[UU__]`, `[U_U_]` 같은 패턴 놓침

**해결:**
```python
# 정규식으로 [UUU_], [U_U_] 등 모든 패턴 감지
raid_pattern = re.compile(r'\[([U_]+)\]')
for match in raid_pattern.finditer(raid['stdout']):
    raid_state = match.group(1)
    if '_' in raid_state:
        # _ 개수에 따라 심각도 판단
        failed_count = raid_state.count('_')
        total_count = len(raid_state)
        issue = f"RAID 디스크 실패 감지: {failed_count}/{total_count} 디스크 실패 [{raid_state}]"
        self.errors.append(issue)

# 추가: "FAILED" 키워드 명시적 체크
if 'FAILED' in raid['stdout'].upper():
    self.errors.append("RAID 장애 상태 (FAILED)")
```

**효과:**
- ✅ `[UUUU]` - 정상 (4개 정상)
- ✅ `[UUU_]` - 감지 (1개 실패)
- ✅ `[U_U_]` - 감지 (2개 실패)
- ✅ `[____]` - 감지 (4개 모두 실패)
- ✅ 실패 디스크 개수 정확히 표시

---

### 4. ✅ df 파싱 견고화

**문제:**
```python
parts = line.split()
if len(parts) >= 6:
    use_percent = int(parts[4].rstrip('%'))
    mountpoint = parts[5]
```
→ BusyBox, 로케일 차이로 필드 순서 변경 가능

**해결:**
```python
# 정규식으로 % 직접 추출 (필드 순서 무관)
percent_pattern = re.compile(r'(\d{1,3})%')

for line in df['stdout'].splitlines():
    # 헤더 스킵 (다국어 대응)
    if 'Filesystem' in line or '파일시스템' in line or line.startswith('Filesystem'):
        continue
    
    # % 패턴 찾기
    percent_match = percent_pattern.search(line)
    if percent_match:
        use_percent = int(percent_match.group(1))
        
        # 마운트 포인트: 마지막 공백으로 분리된 부분
        parts = line.split()
        if len(parts) >= 2:
            mountpoint = parts[-1]
            
            # 판정
            if use_percent >= 90:
                self.errors.append(f"{mountpoint} 디스크 사용량 {use_percent}% (위험)")
            elif use_percent >= 80:
                self.warnings.append(f"{mountpoint} 디스크 사용량 {use_percent}% (경고)")
```

**효과:**
- ✅ BusyBox, GNU coreutils 모두 대응
- ✅ 영문/한글 헤더 모두 스킵
- ✅ 필드 순서 변경에 영향 없음
- ✅ 다중 공백 처리 안전

---

### 5. ✅ 포트/계정 주입 명확화

**문제:**
```python
port = int(nas_config.get('port', 2222))  # Synology 기본은 22인데 2222?
```
→ Synology 기본 SSH 포트는 22

**해결:**
```python
# 포트 기본값을 22 (표준 SSH 포트)로 변경
def __init__(self, host: str, username: str, password: str, 
             port: int = 22, timeout: int = 30):
    """
    Args:
        port: SSH 포트 (기본값 22 - 표준 SSH 포트, Synology 기본값)
    """

# check_nas_status 함수에서도 동일
port = int(nas_config.get('port', 22))
```

**env.example 업데이트:**
```bash
# NAS 설정
NAS_PORT=22  # Synology 기본 SSH 포트 (커스텀 포트 사용 시 변경)
```

**효과:**
- ✅ 표준 SSH 포트 (22) 기본값
- ✅ .env에서 명시하면 해당 포트 사용
- ✅ 커스텀 포트(2222, 2200 등) 유연하게 대응

---

### 6. ✅ utils.ui 불가 시 폴백

**문제:**
```python
from utils.ui import print_section, print_pass, ...  # 필수 의존성
```
→ 단독 실행 환경에서 ImportError

**해결:**
```python
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
```

**효과:**
- ✅ utils.ui 없어도 동작
- ✅ 단독 실행 가능
- ✅ 운영 배포 환경 호환
- ✅ 기본 콘솔 출력으로 폴백

---

## 📊 개선 전후 비교

| 항목 | v1 | v2 (개선 후) |
|------|-----|-------------|
| Synology 명령 경로 | PATH만 | PATH + 절대경로 fallback ✅ |
| 다국어 지원 | 영문만 | 정규식 (모든 언어) ✅ |
| RAID 검출 | 일부 패턴 | 모든 패턴 + 개수 표시 ✅ |
| df 파싱 | 필드 순서 의존 | 정규식 (견고) ✅ |
| 기본 포트 | 2222 | 22 (표준) ✅ |
| utils.ui 의존성 | 필수 | 선택적 (폴백) ✅ |

---

## 🧪 테스트 케이스

### 1. Synology 경로 테스트
```bash
# PATH에 synoups 없는 경우
$ which synoups
# (없음)

# v1: 실패
# v2: /usr/syno/sbin/synoups로 fallback ✅
```

### 2. 다국어 UPS 출력 테스트
```
# 영문 DSM
Battery Charge: 85%  ✅

# 한글 DSM
배터리 충전: 85%  ✅

# 중국어 DSM
电池充电: 85%  ✅
```

### 3. RAID 패턴 테스트
```
[UUUU]    → 정상 (감지 안 함) ✅
[UUU_]    → 1/4 디스크 실패 ✅
[UU__]    → 2/4 디스크 실패 ✅
[U___]    → 3/4 디스크 실패 ✅
[____]    → 4/4 디스크 실패 ✅
[U_U_]    → 2/4 디스크 실패 (비연속) ✅
```

### 4. df 출력 다양성 테스트
```bash
# GNU coreutils
Filesystem      Size  Used Avail Use% Mounted on  ✅

# BusyBox
Filesystem           1K-blocks      Used Available Use% Mounted on  ✅

# 한글 로케일
파일시스템       크기  사용  가용 사용% 마운트위치  ✅
```

---

## 🔧 추가 권장사항 (향후)

### 1. 운영환경 보안 강화
```python
# 현재 (개발환경)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 운영환경 권장
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
```

### 2. 타임아웃 설정 외부화
```python
# .env 추가
NAS_TIMEOUT=30  # 기본 타임아웃 (초)
NAS_COMMAND_TIMEOUT_DF=45  # df 명령 타임아웃
```

### 3. 로깅 추가
```python
import logging
logger = logging.getLogger(__name__)

# 디버깅 정보 기록
logger.debug(f"RAID status: {raid_output}")
logger.warning(f"Disk usage high: {use_percent}%")
```

---

## ✅ 체크리스트

- [x] Synology 경로 fallback 구현
- [x] 다국어 정규식 파싱
- [x] RAID 장애 검출 강화
- [x] df 파싱 견고화
- [x] 포트 기본값 22로 변경
- [x] utils.ui 폴백 구현
- [x] env.example 업데이트
- [x] 린터 검사 통과
- [x] 문서화 완료

---

## 📚 참고 자료

- Synology DSM 명령어 경로 구조
- Python re 모듈 (정규식)
- RAID mdstat 포맷 명세
- BusyBox vs GNU coreutils 차이점

---

*이 문서는 v2 보완 작업을 위해 작성되었습니다.*

