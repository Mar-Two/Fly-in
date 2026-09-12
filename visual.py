from simulation import Drone, Zone, Path
from models import PrefixZone


class Visual():
    """
    Colored terminal rendering of the simulation state, turn by turn.
    """
    def __init__(self) -> None:
        """
        Construct visual.
        """
        self.color: dict[str, int] = {
            'green': 40,
            'white': 15,
            'yellow': 226,
            'red': 196,
            'blue': 21,
            'orange': 214,
            'gray': 249,
            'purple': 129,
            'black': 0,
            'brown': 52,
            'maroon': 1,
            'gold': 220,
            'cyan': 51,
            'magenta': 201,
            'crimson': 88,
            'violet': 177,
            'lime': 83,
            'darkred': 124
            }
        self.zonescolor: dict[str, str] = {}

    def listzonepath(self, path: dict[str, str]) -> list:
        """
        Transform path dict into a list.

        Args:
            path: dict of zone

        Return:
            A list of zones ordered from start_hub to end_hub.
        """
        list_zones = []
        for d, v in path.items():
            if d not in list_zones:
                list_zones.append(d)
            if v not in list_zones:
                list_zones.append(v)
        return list_zones[::-1]

    def diplay_paths(self, path: list, zones: dict[str, Zone],
                     drones: list[Drone]) -> str:
        """
        Build the display line of a path with zone occupancy and drones.

        Args:
            path: list of zone
            zones: dict of object zone
            drones: list of object drone

        Returns:
            A string of state zone and state drone in simulation

        """
        state_zones = []
        for zone in path:
            list_drones: list[str] = []
            list_transit: list[str] = []
            for drone in drones:
                if drone.state == zone and drone.transit is None:
                    if not drone.action:
                        list_drones.append(f"{drone.name}*")
                    else:
                        list_drones.append(drone.name)
                elif drone.transit == zone:
                    if not drone.action:
                        list_transit.append(f"{drone.name}*")
                    else:
                        list_transit.append(drone.name)

            if zones[zone].prefix == PrefixZone.STARTHUB:
                string = f"{self.zonescolor[zone]}[{zones[zone].accumulator}]"
            elif zones[zone].prefix == PrefixZone.ENDHUB:
                string = (f"-{",".join(list_transit)}> {self.zonescolor[zone]}"
                          f"[{zones[zone].accumulator}]")
            else:
                string = (f"-{",".join(list_transit)}> {self.zonescolor[zone]}"
                          f"[{zones[zone].accumulator}/"
                          f"{zones[zone].max_drones}]{",".join(list_drones)}")

            state_zones.append(string)
        return " ".join(state_zones)

    def display(self, tour: int, path: list[Path], zones: dict[str, Zone],
                drones: list[Drone], name_end: str) -> None:
        """
        Display every path with zone occupancy and drone positions.

        Also show the turn number, drones moved and drones delivered.

        Args:
            tour: tour number
            path: list of object path
            zones: dict of object zone
            drones: list of object drone
            name_end: name of endhub
        """
        counter = 0
        count = 0
        for drone in drones:
            if drone.state == name_end:
                count += 1
            if drone.action:
                counter += 1
        print(f"Turn: {tour}    Drones moved: {counter}    Drones delivered: "
              f"{count}/{len(drones)}")
        print("------------------------------------------------------")
        for p in path:
            print(f"Path {p.id} (cost {p.cost}, throughput {p.throughput})")
            listzone = self.listzonepath(p.path)
            print(" ", self.diplay_paths(listzone, zones, drones))
        print()
