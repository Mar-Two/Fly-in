from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from enum import Enum


class PrefixZone(Enum):
    """
    Allowed zone prefixes in a map file.
    """
    STARTHUB = 'start_hub'
    ENDHUB = 'end_hub'
    HUB = 'hub'


class TypeZone(Enum):
    """
    Allowed zone types in a map file.
    """
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class NbDrone(BaseModel):
    """
    Validation model for the nb_drones line.
    """
    nb_drones: int = Field(gt=0)


class ZoneModel(BaseModel):
    """
    Validation model for the zone line.
    """
    prefix: PrefixZone
    name: str = Field(min_length=1)
    positionx: int
    positiony: int
    zone: TypeZone = Field(default=TypeZone.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int | None = Field(default=1, gt=0)

    @model_validator(mode='after')
    def check_name(self) -> Self:
        """
        Forbid '-' in zone names.
        """
        if '-' in self.name:
            raise ValueError(f"'-' is forbidden in zone name '{self.name}'")
        return self

    @model_validator(mode='after')
    def ignore_capacity_on_hubs(self) -> Self:
        """
        Ignore max_drones on the start and end hubs.
        """
        is_hub = self.prefix in (PrefixZone.STARTHUB, PrefixZone.ENDHUB)

        if is_hub:
            self.max_drones = None

        return self


class ConnectionModel(BaseModel):
    """
    Validation model for the connection line.
    """
    name_zone1: str
    name_zone2: str
    max_link_capacity: int = Field(gt=0, default=1)
