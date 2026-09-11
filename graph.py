from models import TypeZone, PrefixZone
import heapq as hp
import math


class NotPath(Exception):
    pass


class Drone():
    def __init__(self, name: str, id: int) -> None:
        self.name = name
        self.id = id
        self.state: None | str = ""
        self.transit: str | None = None
        self.nbturn = 0
        self.action = False
        self.path: dict[str, str] = {}


class Path():
    def __init__(self, path: dict[str, str]) -> None:
        self.path = path
        self.id = 0
        self.nbturn = 0
        self.throughput: float = 0
        self.drones: list[Drone] = []


class Zone():
    def __init__(self, prefix: PrefixZone, name: str,
                 positionx: int, positiony: int,
                 color: str | None = None, zone: TypeZone = TypeZone.NORMAL,
                 max_drones: int | None = 1) -> None:
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
    def __init__(self, name_zone1: str, name_zone2: str,
                 max_link_capacity: int = 1) -> None:
        self.name_zone1 = name_zone1
        self.name_zone2 = name_zone2
        self.max_link_capacity = max_link_capacity
        self.accumulator = 0


class Visual():
    def __init__(self) -> None:
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
        list_zones = []
        for d, v in path.items():
            if d not in list_zones:
                list_zones.append(d)
            if v not in list_zones:
                list_zones.append(v)
        return list_zones[::-1]

    def diplay_paths(self, path: list, zones: dict[str, Zone],
                     drones: list[Drone]) -> str:
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
            print(f"Path {p.id} (cost {p.nbturn}, throughput {p.throughput})")
            listzone = self.listzonepath(p.path)
            print(" ", self.diplay_paths(listzone, zones, drones))
        print()


class Simulation():
    def __init__(self, visual: Visual) -> None:
        self.zone: dict[str, Zone] = {}
        self.connections: dict[tuple, Connection] = {}
        self.name_start = ""
        self.name_end = ""
        self.drones: list[Drone] = []
        self.visual = visual

    def add_drone(self, drone: Drone) -> None:
        self.drones.append(drone)

    def add_zone(self, zone: Zone, name_zone: str) -> None:
        self.zone[name_zone] = zone
        color = self.zone[name_zone].color
        if color is not None:
            if color in self.visual.color:
                zone_colored = ("\033[38;5;"f"{self.visual.color[color]}m"
                                f"{name_zone}\033[0m")
                self.visual.zonescolor[name_zone] = zone_colored
            else:
                self.visual.zonescolor[name_zone] = ("\033[38;5;188m"
                                                     f"{name_zone}\033[0m")
        else:
            self.visual.zonescolor[name_zone] = ("\033[38;5;188m"
                                                 f"{name_zone}\033[0m")

    def add_connection(self, connection: Connection) -> None:
        self.zone[connection.name_zone1].neighbors.append(
            connection.name_zone2)
        self.zone[connection.name_zone2].neighbors.append(
            connection.name_zone1)
        lstzone = [connection.name_zone1, connection.name_zone2]
        name_sort = sorted(lstzone)
        self.connections[tuple(name_sort)] = connection

    def assign_zone_start(self) -> None:
        for drone in self.drones:
            drone.state = self.name_start

    @staticmethod
    def movement_cost(typezone: TypeZone) -> int:
        if typezone == TypeZone.NORMAL:
            return 1
        if typezone == TypeZone.PRIORITY:
            return 1
        if typezone == TypeZone.RESTRICTED:
            return 2
        if typezone == TypeZone.BLOCKED:
            return -1

    def shortest_path(self) -> tuple:
        dist: dict[str, float] = {k: float('inf') for k in self.zone}
        nb_prio = {k: 0 for k in self.zone}
        dist[self.name_start] = 0
        heap: list[tuple[float, str]] = [(0, self.name_start)]
        visited = set()
        previous: dict[str, str] = {}
        while heap:
            (_, u) = hp.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            neighbors = self.zone[u].neighbors
            for neighbor in neighbors:
                value = self.movement_cost(self.zone[neighbor].zone_type)
                if value == -1:
                    continue
                if self.zone[neighbor].zone_type == TypeZone.PRIORITY:
                    nb_priority = nb_prio[u] + 1
                else:
                    nb_priority = nb_prio[u]
                candidat = dist[u] + value
                if candidat < dist[neighbor]:
                    dist[neighbor] = candidat
                    nb_prio[neighbor] = nb_priority
                    previous[neighbor] = u
                    hp.heappush(heap, (candidat, neighbor))
                elif candidat == dist[neighbor]:
                    if nb_priority > nb_prio[neighbor]:
                        previous[neighbor] = u
                        nb_prio[neighbor] = nb_priority
        return (previous, dist)

    def all_delivered(self) -> bool:
        for drone in self.drones:
            if drone.state != self.name_end:
                return False
        return True

    def init_transit_counters(self, paths: list) -> dict:
        result = {}
        for path in paths:
            for drone in path.drones:
                for destination, origin in path.path.items():
                    result[(drone.name, destination)] = 0
                    result[(drone.name, origin)] = 0
        return result

    def extract_paths(self) -> list[Path]:
        paths = []
        visited_zones: list[str] = []
        original_types = {}
        idpath = 1
        while True:
            # Construction des differents chemin
            critical = []
            non_critical = []

            for zone_name in visited_zones:
                if zone_name not in original_types:
                    original_types[zone_name] = self.zone[zone_name].zone_type
                saved_type = self.zone[zone_name].zone_type
                self.zone[zone_name].zone_type = TypeZone.BLOCKED

                previous, dist = self.shortest_path()

                if dist[self.name_end] == float('inf'):
                    critical.append(zone_name)
                else:
                    non_critical.append(zone_name)

                self.zone[zone_name].zone_type = saved_type

            for zone_name in non_critical:
                self.zone[zone_name].zone_type = TypeZone.BLOCKED

            previous, dist = self.shortest_path()

            if dist[self.name_end] != float('inf'):
                key = self.name_end
                new_path = {}
                while key != self.name_start:
                    new_path[key] = previous[key]
                    key = previous[key]
                no_new_zone = True
                for k, v in new_path.items():
                    if (k != self.name_start and
                            k != self.name_end and k not in visited_zones):
                        visited_zones.append(k)
                        no_new_zone = False
                    elif (v != self.name_start and
                          v != self.name_end and v not in visited_zones):
                        visited_zones.append(v)
                        no_new_zone = False
                if no_new_zone:
                    break
                path = Path(new_path)
                path.id = idpath
                path.nbturn = dist[self.name_end]
                paths.append(path)
                idpath += 1
            else:
                break
        for k, v in original_types.items():
            self.zone[k].zone_type = v
        return paths

    def assign_throughput(self, paths: list[Path]) -> None:
        for path in paths:
            throughput = float('inf')
            for destination, origin in path.path.items():
                edge_key = tuple(sorted([destination, origin]))
                link_capacity: float = (
                    self.connections[edge_key].max_link_capacity)
                if self.zone[destination].zone_type == TypeZone.RESTRICTED:
                    link_capacity /= 2
                max_drones = self.zone[origin].max_drones
                if max_drones is None:
                    origin_capacity: float = float('inf')
                else:
                    origin_capacity = max_drones
                max_drones = self.zone[destination].max_drones
                if max_drones is None:
                    destination_capacity: float = float('inf')
                else:
                    destination_capacity = max_drones
                segment_throughput = min([link_capacity, origin_capacity,
                                          destination_capacity])
                if throughput > segment_throughput:
                    throughput = segment_throughput
            path.throughput = throughput

    def assign_drones_to_paths(self, paths: list) -> None:
        for drone in self.drones:
            estimates = []
            for path in paths:
                estimates.append((path, math.ceil(
                    path.nbturn + (len(path.drones) / path.throughput))))
            best_path, turn = min(estimates, key=lambda x: x[1])
            drone.nbturn = turn
            best_path.drones.append(drone)

    def assign_paths_to_drones(self, paths: list) -> None:
        for path in paths:
            for drone in path.drones:
                drone.path = path.path

    def zone_isfree(self, destination: str) -> bool:
        capacity = self.zone[destination].max_drones
        if capacity is None:
            return True
        if (self.zone[destination].accumulator < capacity):
            return True
        return False

    def connection_isfree(self, connection: tuple) -> bool:
        if (self.connections[tuple(connection)].accumulator <
                self.connections[connection].max_link_capacity):
            return True
        return False

    def simulation(self) -> None:
        self.assign_zone_start()

        paths = self.extract_paths()

        if not paths:
            raise NotPath("Error: no path found from start_hub to end_hub.")

        self.assign_throughput(paths)

        self.assign_drones_to_paths(paths)

        self.assign_paths_to_drones(paths)

        tour = 1
        dict_moved = self.init_transit_counters(paths)
        simulationlog = []
        while not self.all_delivered():
            display = []

            for path in paths:
                for destination, origin in path.path.items():
                    result = []
                    edge_key = tuple(sorted([destination, origin]))

                    if (self.zone_isfree(destination) and
                            self.connection_isfree(edge_key)):
                        for drone in self.drones:
                            if destination in drone.path:
                                if drone.path[destination] == origin:
                                    if (drone.state == origin or
                                            drone.transit == destination):
                                        result.append(drone)

                    result = sorted(result, key=lambda x: x.nbturn,
                                    reverse=True)

                    while (result and self.zone_isfree(destination) and
                           self.connection_isfree(edge_key)):
                        drone = result.pop(0)
                        if not drone.action:
                            if (dict_moved[(drone.name, destination)] + 1 ==
                                self.movement_cost(
                                    self.zone[destination].zone_type)):
                                if (drone.transit is None and
                                        self.zone[origin].max_drones):
                                    self.zone[origin].accumulator -= 1
                                drone.state = destination
                                drone.transit = None
                                display.append(f"{drone.name}-{drone.state}")
                                self.zone[destination].accumulator += 1
                                self.connections[edge_key].accumulator += 1
                            else:
                                if self.zone[origin].max_drones:
                                    self.zone[origin].accumulator -= 1
                                display.append(
                                    f"{drone.name}-<"
                                    f"{drone.state}-{destination}>")
                                drone.state = None
                                drone.transit = destination
                                dict_moved[(drone.name, destination)] += 1
                                self.connections[edge_key].accumulator += 1
                            drone.action = True

            simulationlog.append(f"{" ".join(display)}\n")

            self.visual.display(tour, paths, self.zone, self.drones,
                                self.name_end)

            for path in paths:
                for destination, origin in path.path.items():
                    edge_key = tuple(sorted([destination, origin]))
                    self.connections[edge_key].accumulator = 0

            for drone in self.drones:
                drone.action = False

            tour += 1

        with open("log.txt", "w", encoding="utf-8") as f:
            f.writelines(simulationlog)
