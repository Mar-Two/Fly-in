from models import PrefixZone, TypeZone
import heapq as hp


class Drone():
    def _init_(self, name, id):
        self.name = name
        self.id = id
        self.state = ""


class Zone():
    def __init__(self, prefix: str, name: str,
                 positionx: int, positiony: int,
                 color=None, zone='normal', max_drones=1) -> None:
        self.prefix = prefix
        self.name = name
        self.positionx = positionx
        self.positiony = positiony
        self.color = color
        self.zone_type = zone
        self.max_drones = max_drones
        self.neighbors = []
        self.accumulator = 0


class Connection():
    def __init__(self, name_zone1: str, name_zone2: str,
                 max_link_capacity=1) -> None:
        self.name_zone1 = name_zone1
        self.name_zone2 = name_zone2
        self.max_link_capacity = max_link_capacity
        self.accumulator = 0


class Graph():
    def __init__(self):
        self.zone = {}
        self.connections = {}
        self.name_start = ""
        self.name_end = ""
        self.drones = []

    def add_drone(self, drone: Drone):
        self.drones.append(drone)

    def add_zone(self, zone: Zone, name_zone):
        self.zone[name_zone] = zone

    def add_connection(self, connection: Connection):
        self.zone[connection.name_zone1].neighbors.append(
            connection.name_zone2)
        self.zone[connection.name_zone2].neighbors.append(
            connection.name_zone1)
        lstzone = [connection.name_zone1, connection.name_zone2]
        name_sort = sorted(lstzone)
        self.connections[tuple(name_sort)] = connection

    def zone_de_depart(self):
        for drone in self.drones:
            drone.state = self.name_start

    @staticmethod
    def movement_cost(typezone: TypeZone) -> tuple:
        if typezone == TypeZone.NORMAL:
            return 1
        if typezone == TypeZone.PRIORITY:
            return 1
        if typezone == TypeZone.RESTRICTED:
            return 2
        if typezone == TypeZone.BLOCKED:
            return -1

    def shortest_paths(self) -> list:
        dist = {k: float('inf') for k in self.zone}
        dist[self.name_start] = 0
        heap = [(0, self.name_start)]
        visited = set()
        previous = {}
        while heap:
            (i, u) = hp.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            neighbors = self.zone[u].neighbors
            for neighbor in neighbors:
                value = self.movement_cost(self.zone[neighbor].zone_type)
                if value == -1:
                    continue
                candidat = dist[u] + value
                if candidat < dist[neighbor]:
                    dist[neighbor] = candidat
                    previous[neighbor] = u
                    hp.heappush(heap, (candidat, neighbor))
        return (previous, dist)
