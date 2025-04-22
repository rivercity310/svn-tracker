import os
from pathlib import Path

class CmdUtil:

    
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