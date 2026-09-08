from models import TypeZone
import heapq as hp
import math


class Drone():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.state = ""
        self.nbtour = 0
        self.action = False
        self.path = {}


class Path():
    def __init__(self, path):
        self.path = path
        self.id = 0
        self.nbtours = 0
        self.debit = 0
        self.drones = []


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
        nb_prio = {k: 0 for k in self.zone}
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

    def all_delivered(self):
        for drone in self.drones:
            if drone.state != self.name_end:
                return False
        return True

    def arrived_in_zone(self, list_chemin) -> dict:
        result = {}
        for lst in list_chemin:
            for drone in lst.drones:
                for d, v in lst.path.items():
                    result[(drone.name, d)] = 0
                    result[(drone.name, v)] = 0
        return result

    def motor(self):
        self.zone_de_depart()
        list_chemin = []
        path1 = []
        critique = []
        noncritique = []
        d = {}
        idpath = 1
        while True:
            # Construction des differents chemin
            critique = []
            noncritique = []
            for p in path1:
                if p not in d:
                    d[p] = self.zone[p].zone_type
                zone_type = self.zone[p].zone_type
                self.zone[p].zone_type = TypeZone.BLOCKED
                previous, dist = self.shortest_paths()
                if dist[self.name_end] == float('inf'):
                    critique.append(p)
                else:
                    noncritique.append(p)
                self.zone[p].zone_type = zone_type
            for zone in noncritique:
                self.zone[zone].zone_type = TypeZone.BLOCKED
            previous, dist = self.shortest_paths()
            if dist[self.name_end] != float('inf'):
                key = self.name_end
                res = {}
                while key != self.name_start:
                    res[key] = previous[key]
                    key = previous[key]
                same = True
                for k, v in res.items():
                    if k != self.name_start and k != self.name_end and k not in path1:
                        path1.append(k)
                        same = False
                    elif v != self.name_start and v != self.name_end and v not in path1:
                        path1.append(v)
                        same = False
                if same:
                    break
                actual_path = Path(res)
                actual_path.id = idpath
                actual_path.nbtours = dist[self.name_end]
                list_chemin.append(actual_path)
                idpath += 1
            else:
                break

        for k, v in d.items():
            self.zone[k].zone_type = v

        # Debit du chemin
        for lst in list_chemin:
            debit_chemin = None
            for d, v in lst.path.items():
                lstzone = [d, v]
                trie = sorted(lstzone)
                # capacite du lien
                capacitelien = self.connections[tuple(trie)].max_link_capacity
                if self.zone[d].zone_type == TypeZone.RESTRICTED:
                    capacitelien /= 2
                # capacite de la zone1
                if not self.zone[v].max_drones:
                    capacitezone1 = float('inf')
                else:
                    capacitezone1 = self.zone[v].max_drones
                # capacite de la zone2
                if not self.zone[d].max_drones:
                    capacitezone2 = float('inf')
                else:
                    capacitezone2 = self.zone[d].max_drones
                mini = min([capacitelien, capacitezone1, capacitezone2])
                if not debit_chemin or debit_chemin > mini:
                    debit_chemin = mini
                lst.debit = debit_chemin

        for drone in self.drones:
            estimates = []
            for lst in list_chemin:
                estimates.append((lst, math.ceil(lst.nbtours + (len(lst.drones) / lst.debit))))
            best_path, tour = min(estimates, key=lambda x: x[1])
            drone.nbtour = tour
            best_path.drones.append(drone)

        for lst in list_chemin:
            for drone in lst.drones:
                drone.path = lst.path

        # Simulation
        tour = 1
        test = self.arrived_in_zone(list_chemin)
        while not self.all_delivered():
            display = []
            # Boucle qui parcours les zones de bas en haut
            for lst in list_chemin:
                for k, v in lst.path.items():
                    result = []
                    lstzone = [k, v]
                    name_sort = sorted(lstzone)
                    # Verifiction la capité des zones et du max_link si des drones se trouve dans la zone precedente je les ajoute a une list
                    if (not self.zone[k].max_drones or (self.zone[k].accumulator < self.zone[k].max_drones)) and self.connections[tuple(name_sort)].accumulator < self.connections[tuple(name_sort)].max_link_capacity:
                        for drone in self.drones:
                            if k in drone.path:
                                if drone.path[k] == v:
                                    if drone.state == v:
                                        result.append(drone)
                    result = sorted(result, key=lambda x: x.nbtour, reverse=True)

                    # si result est pas vide et les conditions de la zone ou aller sont favorable je push le premier drone de la list j'incremente la capacité de la zone ou il vas je decrment la capacité de la zone ou il sort j'incremente la capacite du lien
                    while result and (not self.zone[k].max_drones or (self.zone[k].accumulator < self.zone[k].max_drones)) and (self.connections[tuple(name_sort)].accumulator < self.connections[tuple(name_sort)].max_link_capacity):
                        drone = result.pop(0)
                        if not drone.action:
                            if test[(drone.name, k)] + 1 == self.movement_cost(self.zone[k].zone_type):
                                if self.zone[v].max_drones:
                                    self.zone[v].accumulator -= 1
                                drone.state = k
                                display.append(f"{drone.name}-{drone.state}")
                                self.zone[k].accumulator += 1
                                self.connections[tuple(name_sort)].accumulator += 1
                            else:
                                display.append(f"{drone.name}-<{drone.state}-{k}>")
                                test[(drone.name, k)] += 1
                                self.connections[tuple(name_sort)].accumulator += 1
                            drone.action = True
            print(f"{tour}: {" ".join(display)}")
            # Lien de toutes les connexions remis a zero
            for lst in list_chemin:
                for k, v in lst.path.items():
                    lstzone = [k, v]
                    name_sort = sorted(lstzone)
                    self.connections[tuple(name_sort)].accumulator = 0
            for drone in self.drones:
                drone.action = False
            tour += 1
