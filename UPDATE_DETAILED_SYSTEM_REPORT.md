# 시스템 점검 상세 리포트 업데이트

## 📅 업데이트 날짜
2025-10-27

## 🎯 업데이트 목적
시스템 종합 점검 결과를 더 상세하게 표시하여, 각 서비스와 포트의 상태를 한눈에 파악할 수 있도록 개선했습니다.

## ✨ 주요 변경 사항

### 1. **리포트 파일 상세화** (`utils/reporter.py`)

#### 변경 전
```
[5/5] 시스템 종합 점검
상태: PASS
  
OS 설정:
  - timezone: ... (PASS)
  - locale: ... (PASS)

서비스 상태:
  - tomcat: active (PASS)
  - postgresql: active (PASS)
```

#### 변경 후
```
[5/5] 시스템 종합 점검
전체 상태: PASS

[OS 설정]
  ✓ TIMEZONE: Time zone: Etc/UTC (UTC, +0000) [PASS]
  ✓ LOCALE: LANG=ko_KR.UTF-8 [PASS]
  ✓ ENCODING: UTF-8 [PASS]

[서비스 상태]
  ✓ tomcat: active [PASS]
  ✓ postgresql: active [PASS]
  ✓ nut-server: active [PASS]
  ✓ nut-monitor: active [PASS]
  ✓ stream: active [PASS]

[포트 리스닝]
  ✓ HTTP (80): Listening [PASS]
    → LISTEN 0 511 *:80 *:* users:(("nginx",pid=1234,fd=7))
  ✓ PostgreSQL (5432): Listening [PASS]
  ✗ RTSP (554): Not listening [FAIL]
  ✓ NUT (3493): Listening [PASS]

[점검 통계]
  - PASS: 18개
  - FAIL: 1개
  - WARN: 1개
  - SKIP: 0개
```

### 2. **콘솔 최종 요약 테이블 추가** (`checker.py`)

프로그램 실행 마지막에 시스템 점검 상세 테이블이 추가됩니다:

```
╔══════════════════════════════════════════════════════════════╗
║                  시스템 점검 상세 결과                        ║
╠══════════════════════════════════════════════════════════════╣
║  서비스 상태          상태             판정                   ║
╠══════════════════════════════════════════════════════════════╣
║  tomcat              active          PASS                    ║
║  postgresql          active          PASS                    ║
║  nut-server          active          PASS                    ║
║  nut-monitor         active          PASS                    ║
║  stream              active          PASS                    ║
╠══════════════════════════════════════════════════════════════╣
║  포트 리스닝          상태             판정                   ║
╠══════════════════════════════════════════════════════════════╣
║  HTTP (80)           Listening       PASS                    ║
║  PostgreSQL (5432)   Listening       PASS                    ║
║  RTSP (554)          Not listening   FAIL                    ║
║  NUT (3493)          Listening       PASS                    ║
╠══════════════════════════════════════════════════════════════╣
║  점검 통계                                                    ║
║    PASS: 18, FAIL: 1, WARN: 1, SKIP: 0                      ║
╚══════════════════════════════════════════════════════════════╝
```

### 3. **통계 정보 추가** (`checks/system_check.py`)

시스템 점검 결과에 통계 정보가 추가됩니다:
- **PASS 개수**: 정상 통과한 항목 수
- **FAIL 개수**: 실패한 항목 수
- **WARN 개수**: 경고 항목 수
- **SKIP 개수**: 건너뛴 항목 수
- **전체 개수**: 총 점검 항목 수

콘솔 출력 예시:
```
✓ 시스템 종합 점검 결과: PASS (✓18 ⚠1 ◌0)
```

## 📋 상세 항목 목록

### OS 설정 (3개 항목)
- ✓ 타임존 (UTC 권장)
- ✓ 로케일 (ko_KR.UTF-8 권장)
- ✓ 인코딩 (UTF-8 권장)

### 서비스 상태 (5개 항목)
- ✓ Tomcat (웹 애플리케이션 서버)
- ✓ PostgreSQL (데이터베이스)
- ✓ NUT Server (UPS 서버)
- ✓ NUT Monitor (UPS 모니터)
- ✓ Stream (영상 스트리밍)

### 포트 리스닝 (4개 항목)
- ✓ HTTP (80) - 웹 서버
- ✓ PostgreSQL (5432) - 데이터베이스
- ⚠ RTSP (554) - 카메라 스트리밍
- ✓ NUT (3493) - UPS 통신

### Java 설정 (2개 항목)
- ✓ Java 버전 (17+ 권장)
- ✓ Heap 설정 (-Xms, -Xmx)

### 네트워크 (2개 항목)
- ✓ IP 주소 (활성 인터페이스)
- ✓ 활성 연결 (NetworkManager)

### 디스크 공간 (2개 항목)
- ✓ 루트 파티션 (80% 미만 권장)
- ⚠ PostgreSQL 디렉토리

### Cron 작업 (2개 항목)
- ✓ Crontab 작업 개수
- ✓ 일일 동기화 작업 (00:01 UTC)

**총 20개 항목**을 상세하게 점검합니다.

## 🔍 시각적 개선 사항

### 1. 상태 표시 기호
- `✓` - PASS (성공)
- `✗` - FAIL (실패)
- `⚠` - WARN (경고)
- `◌` - SKIP (건너뜀)

### 2. 계층 구조
- 대괄호 `[카테고리]`로 구분
- 들여쓰기로 항목 표시
- 화살표 `→`로 상세 정보 표시

### 3. 상태 라벨
- `[PASS]`, `[FAIL]`, `[WARN]`, `[SKIP]` 태그로 명확한 상태 표시

## 📊 실제 사용 예시

### 콘솔 출력
```bash
$ python checker.py

...점검 진행...

[5/5] 시스템 종합 점검
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ OS 설정 확인 중...
✓ timezone: Time zone: Etc/UTC (UTC, +0000)
✓ locale: LANG=ko_KR.UTF-8
✓ encoding: UTF-8

ℹ 주요 서비스 상태 확인 중...
✓ tomcat: active
✓ postgresql: active
✓ nut-server: active
✓ nut-monitor: active
✓ stream: active

ℹ 주요 포트 리스닝 확인 중...
✓ HTTP (80): Listening
✓ PostgreSQL (5432): Listening
✗ RTSP (554): Not listening
✓ NUT (3493): Listening

...생략...

✓ 시스템 종합 점검 결과: PASS (✓18 ⚠1 ◌0)

╔══════════════════════════════════════════════════════════════╗
║                  시스템 점검 상세 결과                        ║
╠══════════════════════════════════════════════════════════════╣
║  서비스 상태          상태             판정                   ║
╠══════════════════════════════════════════════════════════════╣
║  tomcat              active          PASS                    ║
║  postgresql          active          PASS                    ║
...
╚══════════════════════════════════════════════════════════════╝

✓ 리포트가 저장되었습니다: report_2025-10-27_15-30-45.txt
```

### 리포트 파일 확인
```bash
$ cat report_2025-10-27_15-30-45.txt

[5/5] 시스템 종합 점검
--------------------------------------------------------------------------------
전체 상태: PASS

[OS 설정]
  ✓ TIMEZONE: Time zone: Etc/UTC (UTC, +0000) [PASS]
  ✓ LOCALE: LANG=ko_KR.UTF-8 [PASS]
  ✓ ENCODING: UTF-8 [PASS]

[서비스 상태]
  ✓ tomcat: active [PASS]
  ✓ postgresql: active [PASS]
  ✓ nut-server: active [PASS]
  ✓ nut-monitor: active [PASS]
  ✓ stream: active [PASS]

...생략...

[점검 통계]
  - PASS: 18개
  - FAIL: 1개
  - WARN: 1개
  - SKIP: 0개
```

## 🚀 사용 방법

### 1. 프로그램 실행
```bash
ssh koast-user@10.1.10.128
cd ~/edge-system-checker
source venv/bin/activate
python checker.py
```

### 2. 점검 진행
- 카메라 개수 입력
- 각 단계 진행
- 최종 요약 테이블 확인

### 3. 리포트 확인
```bash
# 최신 리포트 확인
ls -lt report_*.txt | head -1

# 리포트 내용 확인
cat report_2025-10-27_15-30-45.txt

# 시스템 점검 부분만 확인
cat report_2025-10-27_15-30-45.txt | grep -A 100 "시스템 종합 점검"
```

## 📁 수정된 파일 목록

1. **`checks/system_check.py`**
   - 통계 정보 수집 기능 추가
   - 결과 출력 시 통계 표시

2. **`utils/reporter.py`**
   - 시스템 점검 섹션 대폭 상세화
   - 카테고리별 구분 및 시각적 표시 개선

3. **`checker.py`**
   - 최종 요약 테이블에 시스템 상세 정보 추가
   - 서비스와 포트 상태를 테이블로 표시

## ✅ 테스트 결과

```bash
$ python test_system_module.py

✓ system_check 모듈 import 성공
✓ ups_check 모듈 import 성공
✓ camera_check 모듈 import 성공
✓ pg_check 모듈 import 성공
✓ nas_check 모듈 import 성공

OS 설정 확인 테스트...
  - 타임존: PASS
  - 로케일: PASS
  - 인코딩: PASS

서비스 상태 확인 테스트...
  - tomcat: active
  - postgresql: active
  - nut-server: active
  - nut-monitor: active
  - stream: active

✓ 모든 테스트 완료!
```

## 💡 추가 개선 제안

향후 추가 가능한 기능:
1. **서비스 재시작 이력**: `journalctl`로 최근 재시작 확인
2. **시스템 부하**: CPU, 메모리, 디스크 I/O 사용률
3. **네트워크 트래픽**: 인터페이스별 트래픽 통계
4. **로그 오류 검사**: 최근 시스템 로그에서 ERROR/CRITICAL 검색
5. **보안 업데이트**: 대기 중인 시스템 업데이트 확인

## 📞 문제 해결

### 권한 문제
일부 시스템 명령어는 권한이 필요할 수 있습니다. 권한이 없는 항목은 자동으로 SKIP 처리됩니다.

### 서비스 찾을 수 없음
서비스 이름이 시스템마다 다를 수 있습니다. 프로그램은 여러 이름을 시도하며, 찾을 수 없으면 SKIP 처리합니다.

### 포트 FAIL
RTSP (554) 포트가 로컬에서 리스닝하지 않는 것은 정상일 수 있습니다 (카메라가 원격에 있는 경우).

## 🎉 완료!

시스템 점검 리포트가 훨씬 더 상세하고 읽기 쉽게 개선되었습니다. 
각 서비스와 포트의 상태를 한눈에 파악할 수 있으며, 통계 정보로 전체 시스템 상태를 빠르게 확인할 수 있습니다.

