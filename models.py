from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing_extensions import Self
from enum import Enum


class PrefixZone(Enum):
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
    prefix: PrefixZone
    name: str = Field(min_length=1)
    positionx: int
    positiony: int
    zone: TypeZone = Field(default=TypeZone.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int | None = Field(default=1, gt=0)

    @model_validator(mode='after')
    def check_name(self) -> Self:
        if '-' in self.name:
            raise ValueError(f"'-' is forbidden in zone name '{self.name}'")
        return self

    @model_validator(mode='after')
    def check_prefix(self) -> Self:
        is_hub = self.prefix in (PrefixZone.STARTHUB, PrefixZone.ENDHUB)

        if is_hub:
            self.max_drones = None

        return self


class ConnectionModel(BaseModel):
    name_zone1: str
    name_zone2: str
    max_link_capacity: int = Field(gt=0, default=1)
