import os
from pathlib import Path

class CmdUtil:
    # 폴더 생성 유틸 함수
    @staticmethod
    def mkdir(path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        
        # 파일인 경우 예외 발생 (확장자가 있으면 파일로 간주)
        if path.suffix: 
            raise ValueError(f"❌ Cannot create a folder because the given path looks like a file: {path}")

        path.mkdir(parents=True, exist_ok=True)
    
    # 유저 입력 대기 (종료 전)
    @staticmethod
    def press_input() -> None:
        print()
        input("Press Enter to exit...")
        print()

    # 커맨드 창 클리어
    @staticmethod
    def clear_cmd() -> None:
        os.system("cls" if os.name == 'nt' else 'clear')
