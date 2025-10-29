# 전체 시스템 테스트 가이드

## 📋 현재 상태

### ✅ 설치된 패키지
- ✓ **paramiko** (v2.12.0) - NAS SSH 연결
- ✓ **python-dotenv** - 환경변수
- ✓ **colorama** (v0.4.6) - 색상 출력

### ❌ 누락된 패키지 (3개)
- ✗ **cv2** (python3-opencv) - 카메라 체크
- ✗ **numpy** (python3-numpy) - 카메라 체크
- ✗ **psycopg2** (python3-psycopg2) - PostgreSQL

---

## 🔍 현재 가능한 테스트

### ✅ NAS Check만 테스트 가능
```bash
cd /home/koast-user/edge-system-checker
python3 test_nas_only.py
```

**NAS Check 기능:**
- ✓ SSH 연결 (포트 2222 → 22 fallback)
- ✓ 시스템 정보 수집
- ✓ 디스크 사용량 체크
- ✓ RAID 상태 확인
- ✓ UPS 상태 확인

---

## 🚀 전체 시스템 테스트 활성화

### 방법 1: 자동 설치 스크립트 (권장)

```bash
# 1. 스크립트 실행 권한 부여
chmod +x INSTALL_PACKAGES.sh

# 2. 패키지 설치 (sudo 권한 필요)
./INSTALL_PACKAGES.sh

# 3. 설치 확인
python3 check_packages.py

# 4. 전체 시스템 체크 실행
python3 checker.py
```

### 방법 2: 수동 설치

```bash
# 누락된 패키지만 설치
sudo apt install -y python3-opencv python3-numpy python3-psycopg2

# 설치 확인
python3 check_packages.py

# 전체 시스템 체크 실행
python3 checker.py
```

---

## 📊 전체 시스템 체크 포함 항목

### 1. 시스템 정보
- IP 주소 체크 (`192.168.1.10/24`, `192.168.10.20/24`)
- 디스크 사용량
- 메모리 사용량
- CPU 정보

### 2. UPS/NUT 상태
- UPS 배터리 상태
- 전원 상태
- NUT 서비스 상태

### 3. 카메라 체크 (opencv 필요)
- 카메라 스트림 연결
- 프레임 읽기
- 화질 체크

### 4. PostgreSQL (psycopg2 필요)
- 데이터베이스 연결
- 데이터 수신 확인
- 테이블 상태

### 5. NAS 체크 (✅ 이미 가능)
- SSH 연결 (포트 fallback)
- 디스크/RAID 상태
- UPS 정보

---

## 🎯 설치 우선순위

### 필수 (전체 시스템 체크)
1. **python3-opencv** - 카메라 체크용
2. **python3-numpy** - OpenCV 의존성
3. **python3-psycopg2** - PostgreSQL 연결

### 선택 (NAS만 테스트)
- 이미 설치됨! `test_nas_only.py` 실행 가능

---

## 📝 설치 명령 요약

```bash
# SSH 접속
ssh koast-user@10.1.10.157

# 디렉토리 이동
cd edge-system-checker

# 패키지 확인
python3 check_packages.py

# 패키지 설치 (옵션 선택)
# 옵션 1: 자동 설치
chmod +x INSTALL_PACKAGES.sh && ./INSTALL_PACKAGES.sh

# 옵션 2: 수동 설치
sudo apt install -y python3-opencv python3-numpy python3-psycopg2

# 설치 확인
python3 check_packages.py

# 테스트 실행
# NAS만:
python3 test_nas_only.py

# 전체 시스템:
python3 checker.py
```

---

## ⚠️ 주의사항

### sudo 권한 필요
- 시스템 패키지 설치 시 sudo 권한 필요
- 직접 SSH 접속하여 설치해야 함

### OpenCV 설치 시간
- python3-opencv 패키지가 크므로 설치에 1-2분 소요
- 인터넷 연결 필요

### 디스크 공간
- 추가 필요 공간: 약 500MB
- `df -h`로 확인 권장

---

## 🎉 설치 후 기대 효과

### 전체 시스템 체크 가능
```
================================================
Edge 시스템 점검 도구
================================================

[1/5] 시스템 상태 점검
  ✓ IP 주소: 192.168.1.10/24
  ✓ IP 주소: 192.168.10.20/24
  ✓ 디스크: 60% 사용

[2/5] UPS/NUT 상태 점검
  ✓ UPS 연결됨
  ✓ 배터리: 95%

[3/5] 카메라 상태 점검
  ✓ Camera 1: 연결 성공
  ✓ Camera 2: 연결 성공

[4/5] PostgreSQL 상태 점검
  ✓ 데이터베이스 연결 성공
  ✓ 데이터 수신 정상

[5/5] NAS 상태 점검 (v2.1)
  ✓ SSH 연결 성공 (포트 2222)
  ✓ RAID 정상
  ✓ 디스크 사용량 정상
```

---

## 📚 관련 파일

- `check_packages.py` - 패키지 확인 스크립트
- `INSTALL_PACKAGES.sh` - 자동 설치 스크립트
- `test_nas_only.py` - NAS 전용 테스트
- `checker.py` - 전체 시스템 체크

---

*전체 시스템 테스트를 위해서는 3개의 누락 패키지 설치가 필요합니다.*

