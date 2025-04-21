from pydantic import BaseModel

class ProjectConfig(BaseModel):
    local: str
    remote: str
    ftp: list[str]

class ProjectMap(BaseModel):
    projects = dict[str, ProjectConfig]