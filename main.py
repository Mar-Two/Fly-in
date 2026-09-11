from parser import MapParser, ParseError
from graph import Simulation, Visual, NotPath
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
    except NotPath as e:
        print(e)
        sys.exit(1)
