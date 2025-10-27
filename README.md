# Edge 시스템 종합 점검 도구

Edge 시스템(UPS, 카메라, NAS, 시스템)을 자동으로 점검하는 Python CLI 도구입니다.

## 🎯 주요 기능

### 1. UPS/NUT 상태 점검
- NUT 서비스 상태 확인 (nut-driver, nut-server, nut-monitor)
- 3493 포트 리스닝 확인
- UPS 상태 정보 조회 (배터리, 전압, 부하 등)
- NAS의 UPS 연결 상태 확인

### 2. 카메라 RTSP 연결 점검
- **GUI 모드**: 영상을 보면서 수동으로 판정
- **Auto 모드**: SSH 원격 실행, 자동으로 스트림 상태 검증
- 원본 카메라 영상 확인
- 블러 처리된 MediaMTX 스트리밍 확인
- 카메라 로그 파일 자동 분석
- 영상 파일 저장 상태 확인

### 3. NAS 상태 점검
- SSH 연결 확인
- 디스크 사용량 확인
- RAID 상태 확인
- 마운트 포인트 확인
- UPS 연결 상태 확인

### 4. 시스템 종합 점검
- OS 설정 (타임존, 로케일, 인코딩)
- 서비스 상태 (Tomcat, PostgreSQL, NUT 등)
- 포트 리스닝 (80, 5432, 3493)
- Java 설정 (버전, Heap 설정)
- 네트워크 설정 (IP 주소, 활성 연결)
- 디스크 공간 확인
- Cron 작업 확인

## 📦 설치 방법

### 필수 요구사항
- Python 3.11 이상
- pip
- venv

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/edge-system-checker.git
cd edge-system-checker
```

### 2. 가상 환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 열어서 실제 값으로 수정
```

## 🚀 사용 방법

### 기본 실행
```bash
python checker.py
```

### 카메라 점검 모드 선택
- **GUI 모드 (1)**: 장비에서 직접 실행, 영상 확인
- **Auto 모드 (2)**: SSH 원격 실행, 자동 검증 (기본값)

### 점검 흐름
1. 카메라 개수 입력
2. [1/4] UPS/NUT 상태 점검
3. [2/4] 카메라 RTSP 연결 점검
4. [3/4] NAS 상태 점검
5. [4/4] 시스템 종합 점검
6. 최종 리포트 생성 (`report_YYYY-MM-DD_HH-MM-SS.txt`)

## 📊 출력 예시

```
════════════════════════════════════════════════════════════════════════════════
  전체 요약
════════════════════════════════════════════════════════════════════════════════
  UPS/NUT              : ✓ PASS
  카메라                : ✓ PASS
  NAS                  : ✓ PASS
  시스템                : ✓ PASS
════════════════════════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════════════════════════
  카메라 상세 결과
════════════════════════════════════════════════════════════════════════════════
  카메라       IP                원본       블러       로그      
  카메라 1     192.168.1.101     PASS       PASS       PASS      
  카메라 2     192.168.1.102     PASS       PASS       PASS      
  카메라 3     192.168.1.103     PASS       PASS       PASS      
  카메라 4     192.168.1.104     PASS       PASS       PASS      
════════════════════════════════════════════════════════════════════════════════
```

## 📁 프로젝트 구조

```
edge-system-checker/
├── checker.py              # 메인 실행 파일
├── requirements.txt        # Python 의존성
├── env.example            # 환경 변수 템플릿
├── checks/                # 점검 모듈
│   ├── __init__.py
│   ├── ups_check.py       # UPS/NUT 점검
│   ├── camera_check.py    # 카메라 점검
│   ├── nas_check.py       # NAS 점검
│   └── system_check.py    # 시스템 점검
└── utils/                 # 유틸리티
    ├── __init__.py
    ├── ui.py             # CLI UI (색상, 출력)
    └── reporter.py       # 리포트 생성
```

## ⚙️ 환경 변수

`.env` 파일 설정 예시:

```env
# NUT/UPS
NUT_UPS_NAME=ups

# NAS
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD=your_password
NAS_PORT=2222

# 카메라
CAMERA_BASE_IP=192.168.1
CAMERA_START_IP=101
CAMERA_USER=root
CAMERA_PASS=root
CAMERA_RTSP_PATH=cam0_0
CAMERA_RTSP_PORT=554
CAMERA_MEDIAMTX_BASE_PORT=1111
```

## 🔧 주요 기능 상세

### IP 주소 필수 체크
- `192.168.1.10/24`와 `192.168.10.20/24` 필수
- 두 개 모두 있어야 PASS
- 하나라도 누락 시 FAIL 및 상세 정보 표시

### 카메라 로그 분석
- 로그 파일 자동 검색 (최근 10일)
- 프레임 수: 4400~4600 체크
- 영상 길이: 280~310초 체크
- 타임스탬프: 10분 이내 체크

### 영상 파일 존재 확인
- 시간대별 폴더 자동 검색
- 최근 10분 이내 파일 확인
- 모든 카메라 파일 존재 여부 확인

### 한글 문자 정렬
- 터미널에서 한글 문자 너비(2칸) 정확히 계산
- ANSI 색상 코드 고려한 정렬
- 모든 테이블 완벽한 정렬

## 🐛 트러블슈팅

### NumPy 호환성 문제
```bash
pip install "numpy<2.0"
```

### OpenCV 비디오 에러 메시지
- H.264, HEVC 디코딩 경고는 정상 현상
- 이미 로그 레벨 설정으로 숨겨져 있음

### SSH 연결 실패
- NAS IP, 포트, 계정 정보 확인
- 방화벽 설정 확인

## 📝 라이센스

MIT License

## 👤 작성자

- 프로젝트 생성일: 2025-10-27
- Python 3.11+
- 대상 시스템: Edge 장비 (Ubuntu/Debian)

## 🎉 업데이트 내역

- **2025-10-27**: 초기 릴리스
  - UPS/NUT 점검
  - 카메라 RTSP 점검 (GUI/Auto 모드)
  - NAS 점검
  - 시스템 종합 점검
  - 한글 문자 정렬 지원
  - IP 주소 필수 체크
  - 비디오 에러 메시지 완전 숨김
