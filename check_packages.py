#!/usr/bin/env python3
"""
필수 패키지 설치 확인 스크립트
"""

def check_packages():
    """필수 패키지가 모두 설치되었는지 확인"""
    packages = {
        'cv2': 'OpenCV (카메라 체크)',
        'numpy': 'NumPy (카메라 체크)',
        'paramiko': 'Paramiko (NAS SSH 연결)',
        'psycopg2': 'psycopg2 (PostgreSQL)',
        'dotenv': 'python-dotenv (환경변수)',
        'colorama': 'Colorama (색상 출력)'
    }
    
    print("="*60)
    print("필수 패키지 확인")
    print("="*60)
    print()
    
    missing = []
    installed = []
    
    for package, description in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            installed.append((package, description, version))
            print(f"✓ {package:15} - {description:30} (v{version})")
        except ImportError:
            missing.append((package, description))
            print(f"✗ {package:15} - {description:30} [누락]")
    
    print()
    print("="*60)
    
    if missing:
        print(f"⚠️  누락된 패키지: {len(missing)}개")
        print()
        print("설치 방법:")
        print("  sudo apt install -y \\")
        for pkg, desc in missing:
            if pkg == 'cv2':
                print(f"    python3-opencv \\  # {desc}")
            elif pkg == 'psycopg2':
                print(f"    python3-psycopg2 \\  # {desc}")
            elif pkg == 'dotenv':
                print(f"    python3-dotenv \\  # {desc}")
            else:
                print(f"    python3-{pkg} \\  # {desc}")
        print()
        print("또는 전체 설치:")
        print("  chmod +x INSTALL_PACKAGES.sh")
        print("  ./INSTALL_PACKAGES.sh")
        print()
        return False
    else:
        print(f"✅ 모든 패키지 설치됨! ({len(installed)}개)")
        print()
        print("전체 시스템 체크 실행 가능:")
        print("  python3 checker.py")
        print()
        return True

if __name__ == '__main__':
    import sys
    success = check_packages()
    sys.exit(0 if success else 1)

