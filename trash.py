 def validate_input(self, result: list):
        dict_nb_drone = {}
        final = []
        dict_start_hub = {}
        dict_end_hub = {}
        for i, res in enumerate(result):
            if i == 0:
                dict_nb_drone[res[0].strip()] = int(res[1].strip())
                nb_drone = NbDrone(**dict_nb_drone)
                final.append(nb_drone)
d_metadata = {'type': 'blue'}

d_value = {'name': 'hub', 'positionx': 0, 'positiony': 0}
data = NbDrone(nb_drones=1)
meta_data = MetaData(**d_metadata)
print(meta_data.max_drones)

class ValueHub(BaseModel):
    name: str = Field(min_lenght=1)
    positionx: int = Field(gt=-1)
    positiony: int = Field(gt=-1)
    zone: Optional[str] = Field(default='normal')
    color: Optional[str | None] = Field(default=None)
    max_drones: Optional[int] = Field(default=1)

    @model_validator(mode='after')
    def check_name(self) -> Self:
        if '-' in self.name:
            raise ValueError(f"'-' is forbidden in zone name '{self.name}'")
