# Edge 시스템 점검 도구 - 빠른 참조

## 🚀 빠른 시작

```bash
# 1. SSH 접속
ssh koast-user@10.1.10.128

# 2. 프로그램 실행
cd ~/edge-system-checker
source venv/bin/activate
python checker.py
```

## 📋 점검 순서

```
[1/5] UPS/NUT 상태 점검
  └─ 서비스, 포트, UPS 데이터, NAS 연결

[2/5] 카메라 RTSP 점검
  └─ 원본 스트림 + 블러 스트림 + 로그 + 영상 파일

[3/5] PostgreSQL 데이터 점검
  └─ 연결, 데이터 조회

[4/5] NAS 상태 점검
  └─ SSH 연결, 디스크, RAID, 마운트

[5/5] 시스템 종합 점검 ⭐ 상세화됨!
  └─ OS, 서비스, 포트, Java, 네트워크, 디스크, Cron
```

## 🆕 최신 업데이트 (2025-10-27)

### 시스템 점검 상세 리포트
- ✅ **서비스별 상태**: tomcat, postgresql, nut-server, nut-monitor, stream
- ✅ **포트별 상태**: HTTP(80), PostgreSQL(5432), RTSP(554), NUT(3493)
- ✅ **통계 정보**: PASS/FAIL/WARN/SKIP 개수 표시
- ✅ **시각적 개선**: ✓/✗/⚠ 기호, 계층 구조, 상세 정보

## 📊 시스템 점검 항목 (20개)

### OS 설정 (3)
- Timezone (UTC)
- Locale (ko_KR.UTF-8)
- Encoding (UTF-8)

### 서비스 (5)
- Tomcat
- PostgreSQL
- NUT Server
- NUT Monitor
- Stream

### 포트 (4)
- HTTP (80)
- PostgreSQL (5432)
- RTSP (554)
- NUT (3493)

### 기타 (8)
- Java 버전/Heap
- IP 주소/연결
- 디스크 공간
- Cron 작업

## 📄 리포트 예시

### 콘솔 출력
```
✓ 시스템 종합 점검 결과: PASS (✓18 ⚠1 ◌0)

╔══════════════════════════════════════════╗
║       시스템 점검 상세 결과               ║
╠══════════════════════════════════════════╣
║  서비스          상태        판정        ║
╠══════════════════════════════════════════╣
║  tomcat         active      PASS        ║
║  postgresql     active      PASS        ║
║  nut-server     active      PASS        ║
║  nut-monitor    active      PASS        ║
║  stream         active      PASS        ║
╠══════════════════════════════════════════╣
║  포트            상태        판정        ║
╠══════════════════════════════════════════╣
║  HTTP (80)      Listening   PASS        ║
║  PostgreSQL     Listening   PASS        ║
║  RTSP (554)     Not listen  FAIL        ║
║  NUT (3493)     Listening   PASS        ║
╚══════════════════════════════════════════╝
```

### 파일 리포트
```
[5/5] 시스템 종합 점검
전체 상태: PASS

[OS 설정]
  ✓ TIMEZONE: UTC [PASS]
  ✓ LOCALE: ko_KR.UTF-8 [PASS]
  ✓ ENCODING: UTF-8 [PASS]

[서비스 상태]
  ✓ tomcat: active [PASS]
  ✓ postgresql: active [PASS]
  ✓ nut-server: active [PASS]
  ✓ nut-monitor: active [PASS]
  ✓ stream: active [PASS]

[포트 리스닝]
  ✓ HTTP (80): Listening [PASS]
    → LISTEN *:80 users:(("nginx",pid=1234))
  ✓ PostgreSQL (5432): Listening [PASS]
  ✗ RTSP (554): Not listening [FAIL]
  ✓ NUT (3493): Listening [PASS]

[점검 통계]
  - PASS: 18개
  - FAIL: 1개
  - WARN: 1개
  - SKIP: 0개
```

## 🔧 테스트 명령어

```bash
# 모듈 테스트
python test_system_module.py

# 최신 리포트 확인
ls -lt report_*.txt | head -1

# 리포트 읽기
cat report_2025-10-27_15-30-45.txt

# 시스템 점검 부분만 보기
cat report_*.txt | grep -A 50 "시스템 종합 점검"
```

## 📚 문서 목록

- **README.md**: 전체 사용 설명서
- **SYSTEM_CHECK_UPDATE.md**: 시스템 점검 기능 추가 설명
- **DETAILED_REPORT_EXAMPLE.md**: 상세 리포트 예시
- **UPDATE_DETAILED_SYSTEM_REPORT.md**: 상세화 업데이트 설명
- **QUICK_REFERENCE.md**: 이 문서 (빠른 참조)

## ⚠️ 주의사항

1. **대화형 실행 필요**: SSH 터미널에서 직접 실행
2. **카메라 입력**: 카메라 개수 입력 (기본값: 4)
3. **테이블명 입력**: PostgreSQL 테이블명 (기본값: blackbox_log)
4. **단계별 확인**: 각 단계 완료 후 컨펌 필요

## 💾 환경 변수 (.env)

```env
# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DB=blackbox
PG_USER=postgres
PG_PASS=yourpassword

# NAS
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD=Edge4IUU#Nas
NAS_PORT=2222

# 카메라
CAMERA_BASE_IP=192.168.1
CAMERA_START_IP=101
CAMERA_USER=root
CAMERA_PASS=root
CAMERA_MEDIAMTX_BASE_PORT=1111
```

## 🎯 예상 결과

### 정상 시스템
```
UPS/NUT: ✓ PASS
카메라: ✓ PASS (4대)
PostgreSQL: ✓ PASS
NAS: ✓ PASS
시스템: ✓ PASS (✓18 ⚠0 ◌0)
```

### 일부 문제 발생 시
```
UPS/NUT: ✓ PASS
카메라: ✓ PASS (3/4, 1 FAIL)
PostgreSQL: ✓ PASS
NAS: ✓ PASS
시스템: ⚠ PASS (✓17 ✗1 ⚠1 ◌1)
```

## 🐛 문제 해결

### 모듈 import 오류
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 권한 부족
일부 항목이 SKIP으로 표시됩니다 (정상).

### 서비스 없음
설치되지 않은 서비스는 SKIP으로 표시됩니다.

### 포트 FAIL
카메라가 원격에 있으면 RTSP(554) FAIL은 정상입니다.

## ⏱️ 예상 소요 시간

- UPS 점검: ~10초
- 카메라 점검: ~2분 (카메라 4대 기준)
- PostgreSQL 점검: ~5초
- NAS 점검: ~15초
- 시스템 점검: ~20초

**총 소요 시간: 약 3-4분**

## 📞 도움말

자세한 내용은 다른 문서를 참조하세요:
- 전체 기능: `README.md`
- 시스템 점검: `SYSTEM_CHECK_UPDATE.md`
- 상세 리포트: `UPDATE_DETAILED_SYSTEM_REPORT.md`
- 리포트 예시: `DETAILED_REPORT_EXAMPLE.md`

