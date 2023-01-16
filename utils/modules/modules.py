from pathlib import Path

from pydantic import BaseModel
from toml import load


class ModuleInfo(BaseModel):
    name: str
    description: str
    enabled: bool
    priority: int


class Module(BaseModel):
    path: Path
    spec: str
    info: ModuleInfo

    @classmethod
    def create(cls, path):
        info_file = path.with_suffix(".toml")
        if not info_file.exists():
            raise FileNotFoundError(f'Could not find a information file for the module "{path.name}"')
        info = load(info_file)
        return cls(path=path, spec=".".join(path.with_suffix("").parts), info=info)
