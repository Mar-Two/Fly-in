from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from typing import Optional
from enum import Enum


class NamePrefix(Enum):
    STARTHUB = 'start_hub'
    ENDHUB = 'end_hub'
    HUB = 'hub'


class TypeZone(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class NbDrone(BaseModel):
    nb_drones: int = Field(gt=0)


class ZoneModel(BaseModel):
    prefix: NamePrefix
    name: str = Field(min_lenght=1)
    positionx: int = Field(gt=-1)
    positiony: int = Field(gt=-1)
    zone: TypeZone = Field(default='normal')
    color: Optional[str | None] = Field(default=None)
    max_drones: Optional[int | None] = Field(default=1)

    @model_validator(mode='after')
    def check_name(self) -> Self:
        if '-' in self.name:
            raise ValueError(f"'-' is forbidden in zone name '{self.name}'")
        if (
             (self.prefix == NamePrefix.STARTHUB or
              self.prefix == NamePrefix.ENDHUB) and
             self.zone == TypeZone.BLOCKED):
            self.zone = 'normal'
        if not self.color:
            self.color = None
        if (
             self.prefix == NamePrefix.STARTHUB or
             self.prefix == NamePrefix.ENDHUB):
            self.max_drones = None
        return self
