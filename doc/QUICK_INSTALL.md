# Edge System Checker 빠른 설치 가이드

## 🚀 5분 설치 (요약)

### 1️⃣ 파일 전송 (선택)

```bash
# 방법 A: Git 클론
git clone <repository-url> edge-system-checker

# 방법 B: 압축 파일 전송
scp edge-system-checker.tar.gz user@server:~
ssh user@server "tar -xzf edge-system-checker.tar.gz"

# 방법 C: 디렉토리 전송
scp -r edge-system-checker user@server:~
```

### 2️⃣ 설치 실행

```bash
# SSH 접속
ssh user@server

# 디렉토리 이동
cd edge-system-checker

# 완전 자동 설치
chmod +x complete_install.sh
./complete_install.sh
```

### 3️⃣ 환경 설정

```bash
# .env 파일 편집
nano .env

# 최소 필수 항목:
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Your_Password_Here"
NAS_PORT=2222
```

### 4️⃣ 실행

```bash
# 전체 시스템 체크
python3 checker.py

# 또는 NAS만 테스트
python3 test_nas_only.py
```

---

## 📋 수동 설치 (단계별)

### 1. 파일 준비
```bash
cd ~
mkdir -p edge-system-checker
cd edge-system-checker
# (파일 복사)
```

### 2. 패키지 설치
```bash
sudo apt update
sudo apt install -y \
  python3-opencv \
  python3-numpy \
  python3-paramiko \
  python3-psycopg2 \
  python3-dotenv \
  python3-colorama
```

### 3. 설정 파일
```bash
cp env.example .env
nano .env
```

### 4. 권한 설정
```bash
chmod +x *.py *.sh
```

### 5. 테스트
```bash
python3 check_packages.py  # 패키지 확인
python3 checker.py         # 실행
```

---

## ⚡ 원라이너 설치

```bash
# 전체 자동 설치 (한 줄)
cd edge-system-checker && chmod +x complete_install.sh && ./complete_install.sh
```

---

## 🔧 필수 설정 (.env)

```bash
# PostgreSQL
PG_HOST=localhost
PG_DB=blackbox
PG_USER=postgres
PG_PASS=yourpassword

# NAS (⭐ 중요)
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Pass#word123"  # 특수문자는 따옴표!
NAS_PORT=2222                # 실패 시 22로 자동 재시도
```

---

## 📊 설치 확인

```bash
# 패키지 확인
python3 check_packages.py

# 예상 출력:
# ✓ cv2
# ✓ numpy
# ✓ paramiko
# ✓ psycopg2
# ✓ dotenv
# ✓ colorama
```

---

## 🎯 사용 명령어

```bash
# NAS만 테스트
python3 test_nas_only.py

# 전체 시스템 체크
python3 checker.py

# 스크립트 실행
./run_edge_checker.sh

# 패키지 재확인
python3 check_packages.py
```

---

## 🆘 문제 해결

### "ModuleNotFoundError: No module named 'cv2'"
```bash
sudo apt install python3-opencv python3-numpy
```

### "Permission denied"
```bash
chmod +x complete_install.sh
chmod +x checker.py
```

### ".env 파일을 찾을 수 없음"
```bash
cp env.example .env
nano .env
```

### "sudo: a terminal is required"
```bash
# SSH로 직접 접속하여 설치 필요
ssh user@server
cd edge-system-checker
./complete_install.sh
```

---

## 📁 최소 필수 파일

```
edge-system-checker/
├── checks/              ⭐ 필수
│   ├── nas_check.py
│   ├── camera_check.py
│   ├── pg_check.py
│   ├── system_check.py
│   └── ups_check.py
├── utils/               ⭐ 필수
│   ├── ui.py
│   └── reporter.py
├── checker.py           ⭐ 필수
├── .env                 ⭐ 필수 (생성 필요)
├── env.example          ⭐ 필수
├── requirements.txt
└── complete_install.sh  (권장)
```

---

## ✅ 설치 체크리스트

```
□ 파일 전송 완료
□ complete_install.sh 실행
□ 모든 패키지 설치 확인 (python3 check_packages.py)
□ .env 파일 생성 및 편집
□ NAS 연결 테스트 성공
□ 전체 시스템 체크 실행 가능
```

---

## 🔗 상세 가이드

더 자세한 내용은:
- **FRESH_INSTALL_GUIDE.md** - 완전한 설치 가이드
- **FULL_SYSTEM_TEST_GUIDE.md** - 시스템 테스트 가이드
- **README.md** - 사용 설명서

---

*빠른 설치 가이드 - 자세한 내용은 FRESH_INSTALL_GUIDE.md 참조*

