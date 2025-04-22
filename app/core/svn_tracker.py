from datetime import datetime
from .path_manager import PathManager


class SvnTracker:
    def __init__(self, project: tuple[str, any]) -> None:
        self.project_name = project[0]
        self.local: str = project[1]['local']
        self.remote: str = project[1]['remote']
        self.ftp: list[str] = project[1]['ftp']

        # 경로 초기화 (이전, 이후)
        self.workdir = PathManager.get_workdir(project[0])
        now = datetime.now().strftime("%Y%m%d_%H%M")

        if not (self.workdir / now / "before").exists():
            PathManager.mkdir(self.workdir / now / "before")
        
        if not (self.workdir / now / "after").exists():
            PathManager.mkdir(self.workdir / now / "after")


    def run(self) -> None:
        pass