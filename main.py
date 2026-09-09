from parser import MapParser, ParseError
from graph import Graph, Visual


if __name__ == "__main__":
    visual = Visual()
    graph = Graph(visual)
    try:
        parser = MapParser('map.txt', graph)
        parser.parse_input_file(parser.read_mapfile())
    except ParseError as e:
        print(e)
    graph.motor()
