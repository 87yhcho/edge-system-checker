#!/bin/bash
# Edge System Checker 필수 패키지 설치 스크립트
# 10.1.10.157 장비용

echo "=========================================="
echo "Edge System Checker 패키지 설치"
echo "=========================================="
echo ""

# 1. 시스템 패키지 업데이트
echo "1. 시스템 패키지 업데이트 중..."
sudo apt update

# 2. Python 기본 패키지
echo ""
echo "2. Python 기본 패키지 설치 중..."
sudo apt install -y python3-pip python3-venv python3-dev

# 3. OpenCV 의존성
echo ""
echo "3. OpenCV 의존성 설치 중..."
sudo apt install -y libopencv-dev python3-opencv

# 4. PostgreSQL 클라이언트
echo ""
echo "4. PostgreSQL 클라이언트 설치 중..."
sudo apt install -y python3-psycopg2

# 5. 기타 필수 패키지
echo ""
echo "5. 기타 Python 패키지 설치 중..."
sudo apt install -y python3-paramiko python3-dotenv python3-colorama python3-numpy

echo ""
echo "=========================================="
echo "✅ 모든 패키지 설치 완료!"
echo "=========================================="
echo ""
echo "설치된 패키지 확인:"
python3 -c "
import sys
packages = ['cv2', 'numpy', 'paramiko', 'psycopg2', 'dotenv', 'colorama']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✓ {pkg}')
    except ImportError:
        print(f'  ✗ {pkg} (누락)')
"

echo ""
echo "전체 시스템 체크 실행:"
echo "  cd edge-system-checker && python3 checker.py"

