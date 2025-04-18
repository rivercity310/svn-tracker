from pathlib import Path

# 폴더 생성 유틸 함수
def mkdir(path: str | Path):
    if isinstance(path, str):
        path = Path(path)
    
    # 파일인 경우 예외 발생 (확장자가 있으면 파일로 간주)
    if path.suffix: 
        raise ValueError(f"❌ Cannot create a folder because the given path looks like a file: {path}")

    path.mkdir(parents=True, exist_ok=True)

# SVN Status를 받아서 풀네임 반환
def svn_status_fullname(code: str) -> str:
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
