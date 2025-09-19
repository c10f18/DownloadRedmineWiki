#!/usr/bin/env python3
"""
Redmine Wiki 다운로더 빌드 스크립트
PyInstaller를 사용하여 실행 파일을 생성합니다.
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """PyInstaller 설치"""
    print("PyInstaller 설치 중...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✓ PyInstaller 설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller 설치 실패: {e}")
        return False
    return True

def build_executable():
    """실행 파일 빌드"""
    print("\n실행 파일 생성 중...")

    # 아이콘 파일 확인
    icon_option = ""
    if os.path.exists("favicon.ico"):
        icon_option = "--icon=favicon.ico"
        print("✓ 아이콘 파일 발견: favicon.ico")
    else:
        print("! 아이콘 파일이 없습니다. 기본 아이콘을 사용합니다.")

    # PyInstaller 명령어 구성
    cmd = [
        'pyinstaller',
        '--onefile',           # 단일 실행 파일 생성
        '--windowed',          # 콘솔 창 숨기기 (GUI 앱용)
        '--name', 'RedmineWikiDownloader',  # 실행 파일명
    ]

    if icon_option:
        cmd.append(icon_option)

    cmd.append('main.py')

    try:
        subprocess.check_call(cmd)
        print("✓ 실행 파일 생성 완료!")
        print("📁 실행 파일 위치: dist/RedmineWikiDownloader.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 빌드 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 50)
    print("Redmine Wiki 다운로더 빌드 스크립트")
    print("=" * 50)

    # PyInstaller 설치
    if not install_pyinstaller():
        return

    # 실행 파일 빌드
    if build_executable():
        print("\n🎉 빌드가 성공적으로 완료되었습니다!")
        print("\n사용법:")
        print("1. dist 폴더의 RedmineWikiDownloader.exe 실행")
        print("2. 원하는 위치에 복사해서 사용")

        # 아이콘 파일이 있다면 함께 복사하라고 안내
        if os.path.exists("favicon.ico"):
            print("\n참고: 아이콘이 제대로 표시되려면 favicon.ico 파일을")
            print("     실행 파일과 같은 폴더에 두는 것이 좋습니다.")
    else:
        print("\n❌ 빌드에 실패했습니다.")

if __name__ == "__main__":
    main()