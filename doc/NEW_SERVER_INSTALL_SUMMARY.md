# 새 서버 설치 요약 가이드

## 📋 개요
다른 서버에 Edge System Checker를 처음부터 설치하는 방법 요약

---

## 🚀 최단 경로 설치 (3가지 방법)

### 방법 1: 완전 자동 (권장) ⭐

```bash
# 1. 파일 전송
scp -r edge-system-checker user@new-server:~

# 2. SSH 접속
ssh user@new-server

# 3. 자동 설치 실행
cd edge-system-checker
chmod +x complete_install.sh
./complete_install.sh

# 4. 환경 설정
nano .env

# 5. 실행
python3 checker.py
```

### 방법 2: 압축 파일 전송

```bash
# 로컬에서 압축
cd edge-system-checker
tar -czf ../edge-system-checker.tar.gz .

# 전송
scp ../edge-system-checker.tar.gz user@new-server:~

# 서버에서 설치
ssh user@new-server
tar -xzf edge-system-checker.tar.gz
cd edge-system-checker
./complete_install.sh
nano .env
python3 checker.py
```

### 방법 3: Git 클론 (개발용)

```bash
# 서버에서 직접
ssh user@new-server
git clone <repository-url> edge-system-checker
cd edge-system-checker
./complete_install.sh
nano .env
python3 checker.py
```

---

## 📦 필수 준비물

### 로컬 (전송용)
```
edge-system-checker/
├── checks/          ⭐ 필수
├── utils/           ⭐ 필수
├── checker.py       ⭐ 필수
├── env.example      ⭐ 필수
├── complete_install.sh  (자동 설치용)
├── INSTALL_PACKAGES.sh  (패키지 설치용)
├── check_packages.py    (확인용)
└── *.md (문서)
```

### 서버 (대상 환경)
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+
- sudo 권한
- 인터넷 연결 (패키지 설치용)

---

## 🔧 설치 단계별 상세

### 1단계: 파일 전송 (1분)

**옵션 A: 전체 디렉토리**
```bash
scp -r edge-system-checker user@server:~
```

**옵션 B: 압축 파일**
```bash
tar -czf edge-system-checker.tar.gz edge-system-checker/
scp edge-system-checker.tar.gz user@server:~
ssh user@server "tar -xzf edge-system-checker.tar.gz"
```

### 2단계: 패키지 설치 (2-3분)

```bash
ssh user@server
cd edge-system-checker

# 자동 설치
./complete_install.sh

# 또는 수동 설치
sudo apt update
sudo apt install -y \
  python3-opencv \
  python3-numpy \
  python3-paramiko \
  python3-psycopg2 \
  python3-dotenv \
  python3-colorama
```

### 3단계: 환경 설정 (1분)

```bash
# .env 파일 생성
cp env.example .env

# 편집
nano .env
```

**필수 설정:**
```bash
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Your_Password"
NAS_PORT=2222

PG_HOST=localhost
PG_DB=blackbox
PG_USER=postgres
PG_PASS=password
```

### 4단계: 테스트 (1분)

```bash
# 패키지 확인
python3 check_packages.py

# NAS 테스트
python3 test_nas_only.py

# 전체 시스템 체크
python3 checker.py
```

---

## 📝 설정 파일 템플릿

### .env 파일 최소 설정

```bash
# PostgreSQL 설정
PG_HOST=localhost
PG_PORT=5432
PG_DB=blackbox
PG_USER=postgres
PG_PASS=yourpassword

# NUT/UPS 설정
NUT_UPS_NAME=ups

# NAS 설정 (⭐ 반드시 수정)
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Edge4IUU#Nas"  # 특수문자는 따옴표 필수!
NAS_PORT=2222  # 실패 시 22로 자동 재시도

# 카메라 설정
CAMERA_BASE_IP=192.168.1
CAMERA_START_IP=101
CAMERA_USER=root
CAMERA_PASS=root
CAMERA_RTSP_PATH=cam0_0
CAMERA_RTSP_PORT=554
CAMERA_MEDIAMTX_BASE_PORT=1111
```

---

## ✅ 설치 검증

### 1. 패키지 확인
```bash
python3 check_packages.py

# 예상 출력:
# ✓ cv2
# ✓ numpy
# ✓ paramiko
# ✓ psycopg2
# ✓ dotenv
# ✓ colorama
```

### 2. 파일 구조 확인
```bash
ls -la

# 필수 파일:
# checks/
# utils/
# checker.py
# .env
```

### 3. 실행 테스트
```bash
# NAS만
python3 test_nas_only.py

# 전체
python3 checker.py
```

---

## 🔄 다른 서버로 복사 (빠른 방법)

### 서버 A → 서버 B 직접 복사

```bash
# 서버 A에서
ssh userA@serverA
cd ~
tar -czf edge-system-checker.tar.gz edge-system-checker/

# 서버 B로 직접 전송
scp edge-system-checker.tar.gz userB@serverB:~

# 서버 B에서
ssh userB@serverB
tar -xzf edge-system-checker.tar.gz
cd edge-system-checker
./complete_install.sh
nano .env
```

---

## 📚 문서 참조

| 문서 | 용도 |
|------|------|
| **QUICK_INSTALL.md** | 빠른 설치 (5분) |
| **FRESH_INSTALL_GUIDE.md** | 상세 설치 가이드 |
| **FULL_SYSTEM_TEST_GUIDE.md** | 시스템 테스트 |
| **README.md** | 사용 설명서 |
| **CHANGELOG.md** | 변경 이력 |

---

## 🆘 자주 발생하는 문제

### Q: "ModuleNotFoundError: No module named 'cv2'"
```bash
A: sudo apt install python3-opencv python3-numpy
```

### Q: "Permission denied"
```bash
A: chmod +x complete_install.sh
   chmod +x checker.py
```

### Q: ".env 파일이 로드되지 않음"
```bash
A: cp env.example .env
   nano .env
```

### Q: "NAS 연결 실패"
```bash
A: .env에서 NAS_IP, NAS_USER, NAS_PASSWORD, NAS_PORT 확인
   ssh -p 2222 user@192.168.10.30 (수동 테스트)
```

### Q: "sudo 권한이 없음"
```bash
A: sudo usermod -aG sudo $USER
   (로그아웃 후 다시 로그인)
```

---

## 🎯 핵심 명령어 요약

```bash
# 설치
scp -r edge-system-checker user@server:~
ssh user@server
cd edge-system-checker
./complete_install.sh

# 설정
nano .env

# 실행
python3 checker.py

# 확인
python3 check_packages.py
```

---

## 💡 팁

### 1. 여러 서버에 배포
```bash
# 서버 목록
SERVERS=(
  "user@10.1.10.128"
  "user@10.1.10.157"
  "user@10.1.10.200"
)

# 일괄 전송
for server in "${SERVERS[@]}"; do
  echo "Deploying to $server..."
  scp -r edge-system-checker $server:~
  ssh $server "cd edge-system-checker && ./complete_install.sh"
done
```

### 2. .env 파일 미리 준비
```bash
# 서버별 .env 파일 준비
.env.server128
.env.server157
.env.server200

# 전송 시 함께 복사
scp edge-system-checker/.env.server128 user@10.1.10.128:~/edge-system-checker/.env
```

### 3. 설치 후 자동 테스트
```bash
# complete_install.sh 실행 후
if python3 check_packages.py; then
    echo "설치 성공!"
    python3 test_nas_only.py
else
    echo "설치 실패 - 패키지 확인 필요"
fi
```

---

## ✅ 완료 체크리스트

```
□ 파일 전송 완료
□ ./complete_install.sh 실행 완료
□ python3 check_packages.py 성공 (모든 패키지 ✓)
□ .env 파일 생성 및 설정 완료
□ python3 test_nas_only.py 성공 (NAS 연결)
□ python3 checker.py 실행 가능 (전체 시스템)
```

---

*새 서버 설치는 5-10분 안에 완료됩니다.*
*상세한 내용은 FRESH_INSTALL_GUIDE.md를 참조하세요.*

