from pydantic import BaseModel
from typing import Union


class Traineeship(BaseModel):
    id: int
    position: Union[str, None]
    link: str
    city: Union[str, None]
    specialization: Union[str, None]
    company: Union[str, None]
    salary: Union[str, int]
    source: str
    date: str
    tag: Union[str, None]