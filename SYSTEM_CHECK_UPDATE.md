# 시스템 종합 점검 기능 추가 업데이트

## 업데이트 날짜
2025-10-27

## 변경 사항

### 1. 새로운 시스템 종합 점검 모듈 추가

`check_edge_status.sh` 스크립트의 점검 항목들을 Python CLI 도구에 통합했습니다.

#### 추가된 파일
- `checks/system_check.py` - 시스템 종합 점검 모듈

#### 수정된 파일
- `checker.py` - 5단계 점검으로 확장 (시스템 종합 점검 추가)
- `utils/reporter.py` - 시스템 점검 결과 리포트에 포함

### 2. 점검 항목

#### 2.1 OS 설정
- **타임존**: UTC 설정 여부 확인
- **로케일**: ko_KR.UTF-8 설정 확인
- **인코딩**: UTF-8 사용 확인

#### 2.2 서비스 상태
자동으로 다음 서비스들의 상태를 확인합니다:
- **Tomcat**: 웹 애플리케이션 서버
- **PostgreSQL**: 데이터베이스 서버
- **NUT Server**: UPS 모니터링 서버
- **NUT Monitor**: UPS 모니터 클라이언트
- **Stream**: 영상 스트리밍 서비스

각 서비스의 활성화 여부와 실행 상태를 점검합니다.

#### 2.3 포트 리스닝
주요 네트워크 포트가 리스닝 중인지 확인:
- **HTTP (80)**: 웹 서버
- **PostgreSQL (5432)**: 데이터베이스
- **RTSP (554)**: 카메라 스트리밍
- **NUT (3493)**: UPS 통신

#### 2.4 Java 설정
- **Java 버전**: Java 17 이상 권장
- **Heap 설정**: -Xms, -Xmx 설정 확인

#### 2.5 네트워크
- **IP 주소**: 활성 네트워크 인터페이스 확인
- **활성 연결**: NetworkManager 연결 상태

#### 2.6 디스크 공간
- **루트 파티션**: 사용률 80% 미만 권장
- **PostgreSQL 데이터 디렉토리**: 별도 마운트 시 확인

#### 2.7 Cron 작업
- **Crontab 작업**: 등록된 작업 개수
- **일일 동기화**: 00:01 UTC 작업 존재 여부

## 점검 흐름

프로그램 실행 시 다음 순서로 점검이 진행됩니다:

```
[1/5] UPS/NUT 상태 점검
  ↓
[2/5] 카메라 RTSP 점검 (원본 + 블러 스트리밍 + 로그 + 영상 파일)
  ↓
[3/5] PostgreSQL 데이터 점검
  ↓
[4/5] NAS 상태 점검
  ↓
[5/5] 시스템 종합 점검 ← 새로 추가!
  ↓
최종 결과 요약 및 리포트 생성
```

## 테스트 결과

```bash
# 모듈 테스트 실행
python test_system_module.py
```

### 테스트 결과 예시
```
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
```

## 사용 방법

### 1. SSH로 서버 접속
```bash
ssh koast-user@10.1.10.128
```

### 2. 프로그램 실행
```bash
cd ~/edge-system-checker
source venv/bin/activate
python checker.py
```

### 3. 점검 진행
- 각 단계마다 결과를 확인하고 계속 진행할지 선택
- 카메라 개수 입력 (기본값: 4)
- PostgreSQL 테이블명 입력 (기본값: blackbox_log)
- 각 점검 단계 완료 후 컨펌

### 4. 결과 확인
- 콘솔에서 실시간 점검 결과 확인
- 최종 요약 테이블 출력
- 리포트 파일 자동 생성: `report_YYYY-MM-DD_HH-MM-SS.txt`

## 출력 예시

```
[5/5] 시스템 종합 점검
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

ℹ Java 설정 확인 중...
✓ Java version: Java 17
✓ Java heap: Configured

ℹ 네트워크 설정 확인 중...
✓ IP 주소: 2개
    enp1s0 10.1.10.128/24
    docker0 172.17.0.1/16

ℹ 디스크 공간 확인 중...
✓ 루트 파티션: 45% 사용 (여유: 104G)

ℹ Cron 작업 확인 중...
✓ Cron 작업: 3개
✓ 일일 동기화 작업: Found

✓ 시스템 종합 점검 결과: PASS
```

## 최종 요약 테이블

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                              전체 요약                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  항목              상태                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  UPS/NUT          ✓ PASS                                                     ║
║  카메라            ✓ PASS                                                     ║
║  PostgreSQL       ✓ PASS                                                     ║
║  NAS              ✓ PASS                                                     ║
║  시스템            ✓ PASS                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 리포트 파일

모든 점검이 완료되면 자동으로 리포트 파일이 생성됩니다:

```
~/edge-system-checker/report_2025-10-27_15-30-45.txt
```

리포트에는 다음 내용이 포함됩니다:
- 전체 점검 요약
- UPS/NUT 상세 상태
- 카메라별 점검 결과 (원본/블러/로그/파일)
- PostgreSQL 연결 및 데이터 상태
- NAS 시스템 정보
- **시스템 종합 점검 결과 (신규)**

## 주의 사항

1. **대화형 실행 필요**: 프로그램은 사용자 입력을 받아 진행되므로 반드시 SSH 터미널에서 직접 실행해야 합니다.

2. **권한**: 일부 시스템 정보를 확인하기 위해 적절한 권한이 필요할 수 있습니다.

3. **네트워크**: 카메라, NAS, PostgreSQL 등에 접근 가능한 네트워크 환경이어야 합니다.

4. **서비스 이름**: 시스템마다 서비스 이름이 다를 수 있으며, 자동으로 여러 이름을 시도합니다.

## 문제 해결

### 모듈 import 오류
```bash
# 가상환경 활성화 확인
source ~/edge-system-checker/venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
```

### 권한 문제
일부 시스템 명령어는 특정 권한이 필요할 수 있습니다. 권한이 없는 항목은 자동으로 SKIP 처리됩니다.

### 서비스 찾을 수 없음
서비스가 다른 이름으로 설치되어 있거나 설치되지 않은 경우 SKIP으로 표시됩니다.

## 다음 단계

시스템 종합 점검 기능이 정상적으로 추가되었습니다. 실제 환경에서 테스트하려면:

```bash
ssh koast-user@10.1.10.128
cd ~/edge-system-checker
source venv/bin/activate
python checker.py
```

문제가 발생하면 먼저 테스트 스크립트로 확인:
```bash
python test_system_module.py
```

