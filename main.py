from parser import MapParser, ParseError
from graph import Graph


def all_good(graph: Graph):
    for drone in graph.drones:
        if drone.state != graph.name_end:
            return False
    return True


if __name__ == "__main__":
    graph = Graph()
    try:
        parser = MapParser('map.txt', graph)
    except ParseError as e:
        print(e)
    previous, dist = graph.shortest_paths()
    graph.zone_de_depart()
    tour = 1
    rev_previous = {}
    while not all_good(graph):
        key = graph.name_end
        rev_previous = {}
        display = []
        # Boucle qui parcours les zones de bas en haut
        while key != graph.name_start:
            result = []
            lstzone = [key, previous[key]]
            name_sort = sorted(lstzone)
            # Verifiction la capité des zones et du max_link si des drones se trouve dans la zone precedente je les ajoute a une list
            if (not graph.zone[key].max_drones or (graph.zone[key].accumulator < graph.zone[key].max_drones)) and graph.connections[tuple(name_sort)].accumulator < graph.connections[tuple(name_sort)].max_link_capacity:
                for drone in graph.drones:
                    if drone.state == previous[key]:
                        result.append(drone)
            rev_previous[previous[key]] = key
            key = previous[key]
            # si result est pas vide et les conditions de la zone ou aller sont favorable je push le premier drone de la list j'incremente la capacité de la zone ou il vas je decrment la capacité de la zone ou il sort j'incremente la capacite du lien 
            while result and (not graph.zone[rev_previous[key]].max_drones or (graph.zone[rev_previous[key]].accumulator < graph.zone[rev_previous[key]].max_drones)) and (graph.connections[tuple(name_sort)].accumulator < graph.connections[tuple(name_sort)].max_link_capacity):
                drone = result.pop(0)
                if graph.zone[key].max_drones:
                    graph.zone[key].accumulator -= 1
                drone.state = rev_previous[key]
                display.append(f"{drone.name}-{drone.state}")
                graph.zone[rev_previous[key]].accumulator += 1
                graph.connections[tuple(name_sort)].accumulator += 1
        print(f"{tour}: {" ".join(display)}")
        """
        for d in graph.drones:
            print(f"{tour + 1}: {d.state}")
        """
        # Lien de toutes les connexions remis a zero
        while key != graph.name_end:
            lstzone = [key, rev_previous[key]]
            name_sort = sorted(lstzone)
            graph.connections[tuple(name_sort)].accumulator = 0
            key = rev_previous[key]
        tour += 1
    """
        total_tour = dist[res[graph.drones[0].state]]
        lstzone = [graph.drones[0].state, res[graph.drones[0].state]]
        lst_zonesort = sorted(lstzone)
        print(lst_zonesort)
        print(graph.connections[tuple(lst_zonesort)])
        print(res[graph.drones[0].state])
        print(graph.zone[res[graph.drones[0].state]].capacity)
        break
        print(f"{graph.drones[0].name}-{res[graph.drones[0].state]}")
        graph.drones[0].state = res[graph.drones[0].state]
        print(total_tour)
    """
    """
    res = 0
    l = 4
    z = 2
    if l <= z:
        res = l
    else:
        res = z
    print(res)
    """