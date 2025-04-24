import yaml
from utils.classes import AppFiles
from utils.cmd_util import CmdUtil
from core.svn_tracker import SvnTracker
from clients.ssh_client import SshClient


def main() -> None:
    # 프로그램 세팅 파일 로딩
    setting_path = AppFiles.SETTING_FILE
    print()

    if not setting_path.exists():
        print(f"[에러] 😅 설정 파일을 찾을 수 없습니다. ('{setting_path}')")
        print("[에러] 자세한 설정 방법은 README.md 파일을 참고해주세요.")
        CmdUtil.press_input()
        exit(0)
    
    with open(setting_path, "r") as f:
        data = yaml.safe_load(f)
    
    projects = []

    print("\n[프로젝트 목록]")
    print("=" * 110)
    for index, (key, value) in enumerate(data.items(), start=1):
        print(f"{index}. {key}")
        for k in value:
            print(f"\t- {k}: {value[k]}")
        print()
        projects.append((key, value))
    print("=" * 110)

    while True:
        select_num = int(input("작업할 프로젝트 번호를 입력해주세요: "))
        select_num -= 1

        if select_num < 0 or select_num >= len(projects):
            print("[경고] 잘못된 프로젝트 번호입니다. 다시 선택해주세요.")
        else:
            break
    
    project = projects[select_num]
 
    if not project:
        print("\n[에러] 선택한 프로젝트의 설정값을 확인해주세요.")

        if 'local' not in project:
            print("- [에러] Local 경로를 지정해주세요.")
        if 'remote' not in project:
            print("- [에러] Remote 경로를 지정해주세요.")
        if 'ftp' not in project:
            print("- [에러] FTP 경로를 지정해주세요.")

        CmdUtil.press_input()
        exit(0)

    # Run
    svn_tracker = SvnTracker(project)
    svn_tracker.run()

    CmdUtil.press_input()


if __name__ == "__main__":
    AUTHOR = "sshwang"
    VERSION = "v1.0.3"

    CmdUtil.clear_cmd()

    print(f"""
    _____  _   _  _   _   _____                     _                
   /  ___|| | | || \\ | | |_   _|                   | |               
   \\ `--. | | | ||  \\| |   | |   _ __   __ _   ___ | | __  ___  _ __ 
    `--. \\| | | || . ` |   | |  | '__| / _` | / __|| |/ / / _ \\| '__|
   /\\__/ /\\ \\_/ /| |\\  |   | |  | |   | (_| || (__ |   < |  __/| |   
   \\____/  \\___/ \\_| \\_/   \\_/  |_|    \\__,_| \\___||_|\\_\\ \\___||_|   

                                    - developed by {AUTHOR} ({VERSION})
    """)

    main()