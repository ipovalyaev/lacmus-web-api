from pydantic import BaseModel
from fastapi_utils.enums import StrEnum
from typing import List
from enum import auto

class Pong(BaseModel):
    pong: str = "Lacmus web API, version X.Y.Z"

class Object(BaseModel):
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    label: str

class Result(BaseModel):
    objects: List[Object] = None