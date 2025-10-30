#!/bin/bash

# Edge System Checker 실행 스크립트
echo "=========================================="
echo "    Edge System Checker 실행"
echo "=========================================="
echo

# 현재 디렉토리를 스크립트 위치로 변경
cd "$(dirname "$0")"

# Python이 설치되어 있는지 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    read -p "Press Enter to close..."
    exit 1
fi

# 필요한 패키지 확인 (실제 사용하는 패키지만)
python3 -c "import cv2, paramiko, psycopg2, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 필요한 패키지가 설치되지 않았습니다."
    echo "   다음 명령어로 설치해주세요:"
    echo "   ./INSTALL_PACKAGES.sh"
    echo "   또는"
    echo "   pip3 install -r requirements.txt"
    read -p "Press Enter to close..."
    exit 1
fi

echo "✅ 환경 확인 완료"
echo "🚀 Edge System Checker를 시작합니다..."
echo

# 프로그램 실행
python3 checker.py

echo
echo "=========================================="
echo "           프로그램 실행 완료"
echo "=========================================="
read -p "Press Enter to close..."
