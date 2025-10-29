#!/bin/bash
# Edge System Checker 완전 자동 설치 스크립트
# Ubuntu/Debian 기반 시스템용

set -e  # 오류 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Edge System Checker 완전 자동 설치"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
if [ ! -f "checker.py" ]; then
    echo -e "${RED}❌ checker.py 파일이 없습니다.${NC}"
    echo "올바른 디렉토리에서 실행하세요."
    exit 1
fi

echo -e "${GREEN}✓${NC} 설치 디렉토리 확인 완료: $(pwd)"
echo ""

# 1. 시스템 정보 확인
echo "=========================================="
echo "1. 시스템 정보 확인"
echo "=========================================="
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Python: $(python3 --version)"
echo "User: $(whoami)"
echo ""

# 2. 패키지 설치
echo "=========================================="
echo "2. 필수 패키지 설치"
echo "=========================================="

if [ -f "INSTALL_PACKAGES.sh" ]; then
    chmod +x INSTALL_PACKAGES.sh
    echo "INSTALL_PACKAGES.sh 실행 중..."
    ./INSTALL_PACKAGES.sh
else
    echo -e "${YELLOW}⚠️  INSTALL_PACKAGES.sh 없음${NC}"
    echo "수동 설치 중..."
    
    # 시스템 업데이트
    echo "시스템 패키지 업데이트 중..."
    sudo apt update
    
    # 필수 패키지 설치
    echo "Python 기본 패키지 설치 중..."
    sudo apt install -y python3-pip python3-venv python3-dev
    
    echo "Edge Checker 필수 패키지 설치 중..."
    sudo apt install -y \
        python3-opencv \
        python3-numpy \
        python3-paramiko \
        python3-psycopg2 \
        python3-dotenv \
        python3-colorama
    
    echo -e "${GREEN}✓${NC} 패키지 설치 완료"
fi

echo ""

# 3. 환경 파일 생성
echo "=========================================="
echo "3. 환경 파일 설정"
echo "=========================================="

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✓${NC} .env 파일 생성됨 (env.example에서 복사)"
        echo ""
        echo -e "${YELLOW}⚠️  중요: .env 파일을 편집하여 환경변수를 설정하세요!${NC}"
        echo ""
        echo "편집 방법:"
        echo "  nano .env"
        echo "  또는"
        echo "  vi .env"
        echo ""
        echo "필수 설정 항목:"
        echo "  - NAS_IP: NAS 서버 IP 주소"
        echo "  - NAS_USER: NAS SSH 사용자명"
        echo "  - NAS_PASSWORD: NAS SSH 비밀번호 (특수문자 있으면 따옴표 필수!)"
        echo "  - PG_HOST, PG_USER, PG_PASS: PostgreSQL 설정"
        echo ""
    else
        echo -e "${RED}❌ env.example 파일이 없습니다.${NC}"
        echo ".env 파일을 수동으로 생성하세요."
    fi
else
    echo -e "${GREEN}✓${NC} .env 파일이 이미 존재합니다"
fi

echo ""

# 4. 파일 권한 설정
echo "=========================================="
echo "4. 파일 권한 설정"
echo "=========================================="

chmod +x checker.py 2>/dev/null || true
chmod +x run_edge_checker.sh 2>/dev/null || true
chmod +x INSTALL_PACKAGES.sh 2>/dev/null || true
chmod +x install_desktop_icon.sh 2>/dev/null || true
chmod +x test_nas_only.py 2>/dev/null || true
chmod +x check_packages.py 2>/dev/null || true
chmod +x complete_install.sh 2>/dev/null || true

echo -e "${GREEN}✓${NC} 실행 권한 설정 완료"
echo ""

# 5. 패키지 확인
echo "=========================================="
echo "5. 패키지 설치 확인"
echo "=========================================="

if [ -f "check_packages.py" ]; then
    python3 check_packages.py
    PACKAGE_CHECK=$?
else
    echo -e "${YELLOW}⚠️  check_packages.py 없음, 수동 확인 필요${NC}"
    PACKAGE_CHECK=0
fi

echo ""

# 6. 설치 완료
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""

if [ $PACKAGE_CHECK -eq 0 ]; then
    echo -e "${GREEN}모든 패키지가 정상적으로 설치되었습니다.${NC}"
    echo ""
    echo "📝 다음 단계:"
    echo ""
    echo "1. 환경 설정 파일 편집:"
    echo "   ${YELLOW}nano .env${NC}"
    echo ""
    echo "2. NAS 전용 테스트:"
    echo "   ${YELLOW}python3 test_nas_only.py${NC}"
    echo ""
    echo "3. 전체 시스템 체크:"
    echo "   ${YELLOW}python3 checker.py${NC}"
    echo ""
    echo "4. (선택) 데스크톱 아이콘 설치:"
    echo "   ${YELLOW}./install_desktop_icon.sh${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  일부 패키지가 누락되었습니다.${NC}"
    echo ""
    echo "누락된 패키지 설치 방법은 위 출력을 참조하세요."
    echo ""
    echo "NAS Check는 사용 가능합니다:"
    echo "   ${YELLOW}python3 test_nas_only.py${NC}"
    echo ""
fi

echo "=========================================="
echo "📚 도움말 문서:"
echo "  - README.md"
echo "  - FRESH_INSTALL_GUIDE.md"
echo "  - FULL_SYSTEM_TEST_GUIDE.md"
echo "=========================================="
echo ""

