#!/bin/bash

# Edge System Checker 데스크톱 아이콘 설치 스크립트

echo "=========================================="
echo "  Edge System Checker 데스크톱 아이콘 설치"
echo "=========================================="
echo

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$SCRIPT_DIR/edge-system-checker.desktop"

# 데스크톱 파일 존재 확인
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "❌ 데스크톱 파일을 찾을 수 없습니다: $DESKTOP_FILE"
    exit 1
fi

# 실행 권한 부여
echo "🔧 실행 권한 설정 중..."
chmod +x "$DESKTOP_FILE"

# 바탕화면에 복사
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    echo "📁 바탕화면에 복사 중..."
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/"
    chmod +x "$DESKTOP_DIR/edge-system-checker.desktop"
    echo "✅ 바탕화면에 아이콘이 생성되었습니다!"
else
    echo "⚠️  바탕화면 디렉토리를 찾을 수 없습니다: $DESKTOP_DIR"
    echo "   수동으로 복사해주세요:"
    echo "   cp $DESKTOP_FILE ~/Desktop/"
fi

# 애플리케이션 메뉴에도 등록 (선택사항)
echo
read -p "애플리케이션 메뉴에도 등록하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    APPLICATIONS_DIR="$HOME/.local/share/applications"
    mkdir -p "$APPLICATIONS_DIR"
    cp "$DESKTOP_FILE" "$APPLICATIONS_DIR/"
    echo "✅ 애플리케이션 메뉴에도 등록되었습니다!"
    echo "   새로고침을 위해 다음 명령어를 실행하세요:"
    echo "   update-desktop-database ~/.local/share/applications"
fi

echo
echo "=========================================="
echo "           설치 완료!"
echo "=========================================="
echo
echo "📋 사용 방법:"
echo "   1. 바탕화면의 'Edge System Checker' 아이콘을 더블클릭"
echo "   2. 터미널 창이 열리면서 프로그램이 실행됩니다"
echo
echo "🔧 문제 해결:"
echo "   - 아이콘이 보이지 않으면: 파일 관리자에서 새로고침 (F5)"
echo "   - 실행되지 않으면: 터미널에서 직접 실행해보세요"
echo "     cd $SCRIPT_DIR && python3 checker.py"
echo
