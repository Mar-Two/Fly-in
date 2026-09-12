from map_parser import MapParser, ParseError
from simulation import Simulation, NoPathFound
from visual import Visual
import sys

if __name__ == "__main__":
    visual = Visual()
    simulation = Simulation(visual)

    try:
        parser = MapParser('map.txt', simulation)
        parser.parse_input_file(parser.read_mapfile())
    except ParseError as e:
        print(e)
        sys.exit(1)

    try:
        simulation.simulation()
    except NoPathFound as e:
        print(e)
        sys.exit(1)
