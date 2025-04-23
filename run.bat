@echo off
setlocal

:: 1. 가상환경 없으면 생성
if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

:: 2. 가상환경 활성화
call ./\.venv\Scripts\activate

:: 3. 의존성 설치
call pip install -r requirements.txt

:: 6. 메인 프로그램 실행
call python main.py

endlocal