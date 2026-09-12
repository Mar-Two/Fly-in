from models import TypeZone
from structures import Drone, Zone, Connection, Path
import heapq as hp
import math
from visual import Visual


class NoPathFound(Exception):
    """
    Path not found error.
    """


class Simulation():
    """
    Route a fleet of drones from start_hub to end_hub across multiple paths,
    under zone and link capacity constraints.
    """
    def __init__(self, visual: Visual) -> None:
        """
        Construct simulation.

        Args:
            visual: visual renderer for the simulation
        """
        self.zone: dict[str, Zone] = {}
        self.connections: dict[tuple, Connection] = {}
        self.name_start = ""
        self.name_end = ""
        self.drones: list[Drone] = []
        self.visual = visual

    def add_drone(self, drone: Drone) -> None:
        """
        Add a drone to the simulation.
        """
        self.drones.append(drone)

    def add_zone(self, zone: Zone, name_zone: str) -> None:
        """
        Add a zone to the simulation and build its colored name.

        Args:
            zone: object zone
            name_zone: name of zone
        """
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
        """
        Add a connection between two zones to the simulation.

        Args:
            connection: object connection
        """
        self.zone[connection.name_zone1].neighbors.append(
            connection.name_zone2)
        self.zone[connection.name_zone2].neighbors.append(
            connection.name_zone1)
        lstzone = [connection.name_zone1, connection.name_zone2]
        name_sort = sorted(lstzone)
        self.connections[tuple(name_sort)] = connection

    def assign_zone_start(self) -> None:
        """Init all drones at start zone."""
        for drone in self.drones:
            drone.state = self.name_start

    @staticmethod
    def movement_cost(typezone: TypeZone) -> int:
        """
        Return the movement cost of a zone type.

        Returns:
            cost of the zone type; -1 means the zone is inaccessible.
        """
        if typezone == TypeZone.NORMAL:
            return 1
        if typezone == TypeZone.PRIORITY:
            return 1
        if typezone == TypeZone.RESTRICTED:
            return 2
        if typezone == TypeZone.BLOCKED:
            return -1

    def shortest_path(self) -> tuple:
        """
        Compute the minimum cost to every zone using Dijkstra.

        Ties are broken in favour of paths crossing more priority zones.

        Returns:
            previous: contains the predecessors
            dist: the minimum cost to reach each zone
        """
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
        """
        Check whether every drone has reached the end hub.

        Returns:
            True if all drones arrived at end hub.
        """
        for drone in self.drones:
            if drone.state != self.name_end:
                return False
        return True

    def init_transit_counters(self, paths: list[Path]) -> dict:
        """
        Initialise the transit progress counter for every drone and zone.

        Args:
            paths: list of each path object

        Returns:
            a dict mapping (drone name, zone) to 0.
        """
        result = {}
        for path in paths:
            for drone in path.drones:
                for destination, origin in path.path.items():
                    result[(drone.name, destination)] = 0
                    result[(drone.name, origin)] = 0
        return result

    def extract_paths(self) -> list[Path]:
        """
        Extract the possible paths to the end hub,
        restarting the pathfinding
        while excluding non-critical zones
        and keeping the critical ones that allow access to the end hub.

        Stop when a path brings no new zone.

        Returns:
            a list of valid paths.
        """
        paths = []
        visited_zones: list[str] = []
        original_types = {}
        idpath = 1
        while True:
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
                path.cost = dist[self.name_end]
                paths.append(path)
                idpath += 1
            else:
                break
        for k, v in original_types.items():
            self.zone[k].zone_type = v
        return paths

    def assign_throughput(self, paths: list[Path]) -> None:
        """
        Assign the throughput for the various paths by proceeding zone by zone,
        and taking the minimum value between the link capacity at the origin
        and the capacity at the destination.
        When the destination zone is restricted, the link capacity is halved.

        Args:
            paths: list of object path
        """
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
        """
        Assign each drone to the path with the earliest estimated arrival.

        The estimated arrival turn is path cost plus
        the queue already assigned, divided by the throughput.

        Args:
            paths: list of object path
        """
        for drone in self.drones:
            estimates = []
            for path in paths:
                estimates.append((path, math.ceil(
                    path.cost + (len(path.drones) / path.throughput))))
            best_path, turn = min(estimates, key=lambda x: x[1])
            drone.nbturn = turn
            best_path.drones.append(drone)

    def assign_paths_to_drones(self, paths: list) -> None:
        """
        Store the assigned path on each drone.

        Args:
            paths: list of object path
        """
        for path in paths:
            for drone in path.drones:
                drone.path = path.path

    def zone_isfree(self, destination: str) -> bool:
        """
        Check whether the destination zone has free capacity.

        Args:
            destination: name of the destination zone

        Returns:
            True if the zone can accept another drone.
        """
        capacity = self.zone[destination].max_drones
        if capacity is None:
            return True
        if (self.zone[destination].accumulator < capacity):
            return True
        return False

    def connection_isfree(self, connection: tuple) -> bool:
        """
        Check whether the link has free capacity.

        Args:
            connection: connection between origin and destination

        Returns:
            True if the link can accept another drone.
        """
        if (self.connections[connection].accumulator <
                self.connections[connection].max_link_capacity):
            return True
        return False

    def simulation(self) -> None:
        """
        Prepare the simulation by extracting paths and assigning drones,
        run the rounds until delivery
        is complete while respecting capacity constraints,
        and write the turn-by-turn log to log.txt.
        """
        self.assign_zone_start()

        paths = self.extract_paths()

        if not paths:
            raise NoPathFound("Error: no path found from start_hub "
                              "to end_hub.")

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
