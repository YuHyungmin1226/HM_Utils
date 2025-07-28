#!/usr/bin/env python3
"""
폴더 정리 스크립트

이 스크립트는 Python 프로젝트 폴더를 정리하기 위한 유틸리티입니다.
- __pycache__ 폴더 삭제
- .pyc 파일 삭제
- .DS_Store 파일 삭제
- 빌드 임시 파일 정리 (README.md 유지)
"""

import os
import shutil
import sys
from pathlib import Path

def print_with_color(message, color_code=36):
    """색상이 있는 메시지 출력"""
    print(f"\033[{color_code}m{message}\033[0m")

def cleanup_directory(root_dir="."):
    """지정된 디렉토리와 하위 디렉토리를 정리합니다."""
    
    root_path = Path(root_dir).resolve()
    print_with_color(f"시작 경로: {root_path}")
    print_with_color("정리 작업을 시작합니다...", 33)
    
    # 카운터 초기화
    deleted_count = {
        "pycache_dirs": 0,
        "pyc_files": 0,
        "ds_store_files": 0,
        "build_files": 0
    }
    
    # 1. __pycache__ 폴더 삭제
    for dirpath, dirnames, filenames in os.walk(root_path):
        # __pycache__ 폴더 제거
        for dirname in dirnames[:]:
            if dirname == "__pycache__":
                pycache_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(pycache_path)
                    deleted_count["pycache_dirs"] += 1
                    print(f"삭제됨: {pycache_path}")
                except Exception as e:
                    print(f"오류: {pycache_path} 삭제 실패 - {e}")
        
        # 2. .pyc 파일 삭제
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            # .pyc 파일 삭제
            if filename.endswith(".pyc"):
                try:
                    os.remove(filepath)
                    deleted_count["pyc_files"] += 1
                    print(f"삭제됨: {filepath}")
                except Exception as e:
                    print(f"오류: {filepath} 삭제 실패 - {e}")
            
            # 3. .DS_Store 파일 삭제
            elif filename == ".DS_Store":
                try:
                    os.remove(filepath)
                    deleted_count["ds_store_files"] += 1
                    print(f"삭제됨: {filepath}")
                except Exception as e:
                    print(f"오류: {filepath} 삭제 실패 - {e}")
    
    # 4. build 폴더 정리 (README.md 파일 유지)
    build_dir = os.path.join(root_path, "build")
    if os.path.exists(build_dir) and os.path.isdir(build_dir):
        readme_path = os.path.join(build_dir, "README.md")
        readme_exists = os.path.exists(readme_path)
        
        # README.md 파일 백업
        if readme_exists:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        # build 디렉토리 내 파일 및 하위 디렉토리 삭제
        for item in os.listdir(build_dir):
            item_path = os.path.join(build_dir, item)
            if item != "README.md":
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                    deleted_count["build_files"] += 1
                    print(f"삭제됨: {item_path}")
                except Exception as e:
                    print(f"오류: {item_path} 삭제 실패 - {e}")
        
        # README.md 파일 복원
        if readme_exists:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
    
    # 결과 출력
    print_with_color("\n정리 완료!", 32)
    print_with_color(f"삭제된 __pycache__ 폴더: {deleted_count['pycache_dirs']}", 36)
    print_with_color(f"삭제된 .pyc 파일: {deleted_count['pyc_files']}", 36)
    print_with_color(f"삭제된 .DS_Store 파일: {deleted_count['ds_store_files']}", 36)
    print_with_color(f"정리된 build 디렉토리 파일/폴더: {deleted_count['build_files']}", 36)

if __name__ == "__main__":
    # 인자가 없으면 현재 디렉토리를 정리
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # 사용자 확인
    print_with_color(f"'{target_dir}' 디렉토리와 모든 하위 디렉토리를 정리하시겠습니까?", 33)
    print_with_color("이 작업은 다음 파일들을 삭제합니다:", 33)
    print("  - 모든 __pycache__ 폴더")
    print("  - 모든 .pyc 파일")
    print("  - 모든 .DS_Store 파일")
    print("  - build 폴더 내 임시 파일 (README.md 제외)")
    
    confirm = input("\n계속하려면 'y'를 입력하세요: ")
    if confirm.lower() == 'y':
        cleanup_directory(target_dir)
    else:
        print_with_color("정리 작업이 취소되었습니다.", 31) 