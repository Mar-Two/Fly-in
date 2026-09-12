from models import TypeZone, PrefixZone


class Drone():
    """
    A drone with its current position, assigned path and transit state.
    """
    def __init__(self, name: str, id: int) -> None:
        """
        Construct drone.

        Args:
            name: name of drone
            id: id of drone
        """
        self.name = name
        self.id = id
        self.state: None | str = ""
        self.transit: str | None = None
        self.nbturn = 0
        self.action = False
        self.path: dict[str, str] = {}


class Path():
    """
    A path from start_hub to end_hub with its cost,
    throughput and assigned drones.
    """
    def __init__(self, path: dict[str, str]) -> None:
        """
        Construct path.

        Args:
            path: dict of zones in path.
        """
        self.path = path
        self.id = 0
        self.cost = 0
        self.throughput: float = 0
        self.drones: list[Drone] = []


class Zone():
    """
    A zone in graph with zone type, capacity and neighbors.
    """
    def __init__(self, prefix: PrefixZone, name: str,
                 positionx: int, positiony: int,
                 color: str | None = None, zone: TypeZone = TypeZone.NORMAL,
                 max_drones: int | None = 1) -> None:
        """
        Construct Zone.

        Args:
            prefix: PrefixZone.starthub, PrefixZone.endhub or PrefixZone.hub.
            name: name of zone
            positionx: x coordinate from the map file
            positiony: y coordinate from the map file
            color: display zone with color in terminal
            zone: TypeZone.(NORMAL, RESTRICTED, BLOCKED, PRIORITY)
            max_drones: capacity of zone
        """
        self.prefix = prefix
        self.name = name
        self.positionx = positionx
        self.positiony = positiony
        self.color = color
        self.zone_type = zone
        self.max_drones = max_drones
        self.neighbors: list[str] = []
        self.accumulator = 0


class Connection():
    """
    Connection between two zones.
    """
    def __init__(self, name_zone1: str, name_zone2: str,
                 max_link_capacity: int = 1) -> None:
        """
        Construct connection.

        Args:
            name_zone1 : the name of the first connected zone.
            name_zone2 : the name of the second connected zone.
            max_link_capacity : max drones crossing this link per turn.
        """
        self.name_zone1 = name_zone1
        self.name_zone2 = name_zone2
        self.max_link_capacity = max_link_capacity
        self.accumulator = 0
