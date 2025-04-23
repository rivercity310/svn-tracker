import subprocess
import shutil
from openpyxl import Workbook, load_workbook
from datetime import datetime
from pathlib import Path
from core.path_manager import PathManager
from utils.cmd_util import CmdUtil


class SvnTracker:
    def __init__(self, project: tuple[str, any]) -> None:
        self.project_name = project[0]
        self.local: str = project[1]['local']
        self.remote: str = project[1]['remote']
        self.ftp: list[str] = project[1]['ftp']

        # 경로 초기화 (이전, 이후)
        self.now = datetime.now().strftime("%Y%m%d_%H%M")
        self.workdir = PathManager.get_workdir(project[0])
        self.workdir_before = self.workdir / self.now / "before"
        self.workdir_after = self.workdir / self.now / "after"

        if not self.workdir_before.exists():
            PathManager.mkdir(self.workdir_before)

        if not self.workdir_after.exists():
            PathManager.mkdir(self.workdir_after)


    def run(self) -> None:
        print("=" * 110)
        print("\n\n[ SVN STATUS ]") 
        print(f"👌 Local Repository Path: {self.workdir / self.now}")
        print(f"📁 Remote Repository Path: {self.remote}")

        print("\n🔍 Checking for changes...")
        status_output = self._get_svn_status()
        print(status_output)

        change_files = self._parse_svn_status(status_output)
        print("\n")

        if not change_files:
            print("✅ 변경된 파일이 없습니다.")
            print("프로그램을 종료합니다.")
            CmdUtil.press_input()
            return

        # 커밋 대상 파일 선정
        commit_list = []
        print("[ 커밋할 대상 파일을 선택해주세요. ]")

        for type, file_path in change_files:
            ans = input(f"({type}) {file_path} (Y/N): ")
            if ans.upper() == "Y":
                commit_list.append({"type": type, "path": file_path})

        if len(commit_list) == 0:
            print("✅ 선택된 커밋 대상 파일이 없습니다.")
            print("프로그램을 종료합니다.")
            CmdUtil.press_input()
            return

        print("\n\n[ 선택된 커밋 대상 파일 ]")
        for commit in commit_list:
            print(f"- ({commit['type']}) {commit['path']}")

        rst = input("\n\커밋을 진행할까요? (Y/N): ")

        if rst.upper() != "Y":
            print("프로그램을 종료합니다.")
            CmdUtil.press_input()
            return

        while True:
            commit_message = input("커밋 메시지를 입력해주세요: ")
            if len(commit_message) > 0:
                break
            else:
                print("[경고] 커밋 메시지는 최소 1글자 이상 입력해야 합니다.")

        print("\n\n[ Remote 서버의 파일을 백업합니다. ]")
        success_list, fail_list = self._export_existing_files(commit_list)
        
        for success in success_list:
            print(f"\t- 👌 {success['status']}: {success['path']}")

        for fail in fail_list:
            print(f"\t- 😭 {fail['status']}: {fail['path']}")

        print("\n\n[ 커밋을 진행합니다... ]")
        self._svn_commit(commit_list, commit_message)
        print(f"- 🚀 {len(commit_list)}개의 파일이 성공적으로 커밋되었습니다.")

        print("\n[ 파일을 복사합니다... ]") 
        self._copy_changed_files(commit_list)
        print(f"📦 {len(commit_list)}개의 파일을 '{self.workdir_after}'에 성공적으로 복사하였습니다.\n")

        res = input("변경 파일을 개발 서버에 반영할까요? (Y/N): ")

        if res == 'N':
            print("프로그램을 종료합니다.")
            CmdUtil.press_input()
            return
        
        print("\n[ FTP 서버에 로그인합니다... ]") 
        username = input("FTP Username: ")
        password = input("FTP password: ")

        # for host in self.ftp:
            # transfer_committed_files(host, username, password)

        history = input("나중에 이 백업을 기억하기 위한 짧은 설명을 작성해주세요: ")

        with open(self.workdir / "history.txt", "w", encoding="UTF-8") as f:
            f.writelines(f"설명: {history}\n")
            f.writelines(f"커밋 메시지: {commit_message}\n")
            f.writelines(f"커밋 일시: {self.now}\n\n")
            
            # 커밋 리스트 기록
            f.writelines(f"[커밋 목록 {len(commit_list)}건]\n")
            for type, file_path in commit_list:
                f.writelines(f"({type}) - {file_path}\n")

            # 백업 성공 목록 기록 
            f.writelines(f"\n[백업 성공 목록 {len(success_list)}건\n")
            for success in success_list:
                f.writelines(f"({success['type']}) - {success['path']}\n")

            # 백업 실패 목록 기록 
            f.writelines(f"\n[백업 실패 목록 {len(fail_list)}건 - (SVN에 없는 파일)]\n")
            for fail in fail_list:
                f.writelines(f"({fail['type']}) - {fail['path']}\n")

        print("\n\n[ 엑셀 파일에 히스토리를 기록하고 있습니다... ]") 
        self._write_to_excel(commit_list)

        print("✅ Done!")


    def _get_svn_status(self) -> str:
        result = subprocess.run(["svn", "status"], cwd=self.local, capture_output=True, text=True)
        return result.stdout


    def _parse_svn_status(self, status_output: str):
        # A	추가됨 (Added)
        # C	충돌 (Conflicted)
        # D	삭제됨 (Deleted)
        # I	무시됨 (Ignored)
        # M	수정됨 (Modified)
        # R	교체됨 (Replaced)
        # X	외부 참조 (eXternals definition)
        # ?	버전 관리되지 않음 (Unversioned)
        # !	누락됨 (item missing, may be deleted)
        # ~	타입 변경됨 (Type changed)

        # 복합 상태가 나오는 경우
        # A +	(A: Added, +: with history)	파일을 추가했는데, 기존 파일 복사해서 만든 경우
        # R +	(R: Replaced, +: with history)	기존 파일 삭제 후 새 파일을 추가한 경우, 히스토리 있음
        # R C	(R: Replaced, C: Conflict)	파일을 교체했는데 충돌도 남
        # M C	(M: Modified, C: Conflict)	수정 중 충돌 발생
        # A C	(A: Added, C: Conflict)	추가한 파일에 충돌 발생 (드물지만 가능)
        BASE_STATUS = ['A', 'C', 'D', 'I', 'M', 'R', 'X', '?', '!', '~', 'A']
        changes = []

        for line in status_output.splitlines():
            if not line.strip():
                continue

            status_code = line[:7].strip()
            path = line[7:].strip()

            # 기본 상태인 경우
            if status_code in BASE_STATUS:
                # 충돌 파일 제외
                if status_code == 'C':
                    print("- [Exclude] 충돌 파일 제외")
                    print(line)
                    print()
                    continue

                # Unversioned file 제외
                if status_code == '?':
                    print(f"- [Exclude] {path}  --  Unversioned File")
                    continue
                
                print(f"- [Include] {path}")
                path = path.replace("\\", "/")
                status_code = self._get_full_status(status_code)
                changes.append((status_code, path))

        return changes


    # SVN Status를 받아서 풀네임 반환
    def _get_full_status(self, code: str) -> str:
        status_mapping = {
            'A': 'Added',
            'C': 'Conflicted',
            'D': 'Deleted',
            'I': 'Ignored',
            'M': 'Modified',
            'R': 'Replaced',
            'X': 'External',
            '?': 'Unversioned',
            '!': 'Missing',
            '~': 'Obstructed',
        }

        return status_mapping.get(code.upper(), 'Unknown')


    # 기존 파일 다운로드 (백업)
    def _export_existing_files(self, commit_list: list[str]):
        success_list = []
        fail_list = []

        for commit in commit_list:
            file_path = commit['path']
            remote_file_path: Path = self.remote + "/" + file_path
            local_save_path: Path = self.workdir_before + "/" + file_path

            try:
                PathManager.mkdir(local_save_path.parent)
                subprocess.run(["svn", "export", remote_file_path, local_save_path], check=True)
                success_list.append({"status": self._get_full_status(type), "path": file_path})
            except subprocess.CalledProcessError as e:
                print("😭😭 {remote_file_path} 파일 다운로드 실패")
                print(e)
                fail_list.append({"status": self._get_full_status(type), "path": file_path})
        
        return success_list, fail_list
    
    def _svn_commit(self, commit_list: list, commit_message: str):
        try:
            commit_cmd = ["svn", "commit", "-m", commit_message]

            for commit in commit_list:
                commit_cmd.append(commit['path'])

            subprocess.run(commit_cmd, cwd=self.local, check=True)
        except subprocess.CalledProcessError as e:
            print("SVN 커밋에 실패하였습니다.")
            print(e)
            exit(1)


    def _copy_changed_files(self, commit_list: list):
        for commit in commit_list:
            file_path = commit['path']
            full_src_path: Path = self.local / file_path
            full_dest_path: Path = self.workdir_after / file_path
            PathManager.mkdir(full_dest_path.parent)

            if full_src_path.is_file:
                shutil.copy2(full_src_path, full_dest_path)
                print(f"- {full_src_path} ===> {full_dest_path}")


    def _write_to_excel(self, commit_list):
        excel_file_path: Path = self.workdir / "commit_history.xlsx"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 파일이 없으면 새로 생성
        if not excel_file_path.exists():
            wb = Workbook()
            ws = wb.active
            ws.append(["Timestamp", "Author", "Change Type", "File Path"])
        else:
            wb = load_workbook(excel_file_path)
            ws = wb.active

        for commit in commit_list:
            file_path = commit['path']
            author = self._get_last_author(file_path)
            ws.append([timestamp, author, commit['type'], file_path])

        wb.save(excel_file_path)


    def _get_last_author(self, file_path):
        try:
            result = subprocess.run(["svn", "log", "-l", "1", file_path], cwd=self.local, capture_output=True, text=True)
            lines = result.stdout.splitlines()
            if len(lines) >= 2:
                parts = lines[1].split('|')
                if len(parts) >= 2:
                    return parts[1].strip()
        except Exception:
            pass
        return "Unknown"
