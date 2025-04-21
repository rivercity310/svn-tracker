from pathlib import Path
from utils import CmdUtil
from dataclasses import dataclass


@dataclass(frozen=True)
class AppPaths:
    USER_DIR: Path = Path.home()
    DESKTOP_DIR: Path = USER_DIR / "Desktop"
    DESKTOP_ONEDRIVE_DIR: Path = USER_DIR / "OneDrive" / "Desktop"
    APP_NAME: str = "SVN Tracker"

    @staticmethod
    def get_workdir(repo_name: str) -> Path:
        desktop_onedrive_dir = AppPaths.DESKTOP_ONEDRIVE_DIR
        desktop_dir = AppPaths.DESKTOP_DIR
        app_name = AppPaths.APP_NAME

        if desktop_onedrive_dir.exists():
            path = desktop_onedrive_dir / app_name / repo_name
        else:
            path = desktop_dir / app_name / repo_name
        
        CmdUtil.mkdir(path)
        return path
    

@dataclass(frozen=True)
class AppFiles:
    SETTING_FILE: Path = AppPaths.USER_DIR / "svn_tracker.yaml"
    