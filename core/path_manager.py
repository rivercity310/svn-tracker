from pathlib import Path


# 앱 실행시 필요한 경로 생성 / 삭제 / 찾기 등의 기능을 지원하는 클래스 
class PathManager:
    USER_DIR: Path = Path.home()

    # repo_name에 해당하는 작업 경로 반환
    @classmethod
    def get_workdir(cls, repo_name: str) -> Path:
        workdir = cls._select_workdir() / repo_name
        
        if not workdir.exists():
            cls.mkdir(workdir)

        return workdir
    
    # 사용자 환경에 따라 작업할 베이스 경로 반환
    @classmethod
    def _select_workdir(cls) -> Path:
        user_dir = cls.USER_DIR
        app_name = "SVN Tracker"

        if (user_dir / "OneDrive" / "바탕 화면").exists():
            return (user_dir / "OneDrive" / "바탕 화면" / app_name)
        
        if (user_dir / "OneDrive" / "Desktop").exists():
            return (user_dir / "OneDrive" / "Desktop" / app_name)
        
        if (user_dir / "Desktop").exists():
            return (user_dir / "Desktop" / app_name)

    # 경로에 대한 폴더 생성
    @classmethod
    def mkdir(cls, path: Path | str):
        if isinstance(path, str):
            path = Path(path)

        if path.suffix: 
            path = path.parent

        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"- 작업 폴더 생성: {path}")
        except Exception as e:
            print(f"폴더 생성 실패: {e}")
            raise e
