*This project has been created as part of the 42 curriculum by mben-mer.*

# Fly-in 

## Description

Fly-in simulates a fleet of drones travelling across multiple paths under zone and link capacity constraints. The goal is to move every drone from a start hub to an end hub in as few simulation turns as possible.

Zones and links have limited capacity, some zones cost two turns to cross, and others are inaccessible. Drones move simultaneously, so they must be spread across several paths while avoiding conflicts.

The project is built around a parser validating the map format, a weighted Dijkstra pathfinder, a multi-path extraction step, a turn-by-turn simulation engine, and a colored terminal renderer.

## Instructions

Requirements: Python 3.10+ and uv.
```
make install
```
By default the project reads map.txt at the root of the repository.
```
make run
```
A different map can be passed with the MAP variable:
```
make run MAP=maps/hard/01_maze_nightmare.txt
```
The colored visualization is printed to the terminal, and the turn-by-turn output follows the required format in log.txt.

Check flake8 and mypy
```
make lint
```
Clean all pycache and log.txt
```
make clean
```
Run with pdb 
```
make debug
```

## Resources
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Code Ansi](https://www.ditig.com/256-colors-cheat-sheet)

### AI usage

Claude (Anthropic) was used in the following ways:

- Explain Dijkstra's algorithm.
- Review and translate the docstrings into English.
- Help with the formatting and English translation of this README.

## Algorithm

### Pathfinding
- Paths are extracted with a weighted Dijkstra, where the cost is carried by the destination zone rather than by the edge. One modification was added: when reaching a neighbour yields exactly the same cost as the one already recorded, the path crossing the most priority zones is kept.

### Multi-path extraction
- Dijkstra is then run repeatedly. Before each run, the non-critical zones of the paths already found are blocked, while the critical ones — those whose removal would make the end hub unreachable — remain available, so paths can overlap where needed. The loop stops when no path is found, or when the extracted path brings no new zone.

### Throughput
- Each path is then given a throughput: the minimum, along the whole path, of the origin zone capacity, the link capacity and the destination zone capacity. When the destination is a restricted zone, the link capacity is halved, since the link stays occupied for the two turns of the transit.


### Drone assignment
- For each drone, every path is evaluated with the formula: path cost plus the number of drones already assigned divided by the path throughput. The drone joins the path with the lowest estimated arrival turn.

### Simulation engine
- Each turn, every path is walked backwards, from the end hub to the start hub. Moving the most advanced drones first frees capacity for those behind them within the same turn.

### Caching
- Paths are computed once before the simulation and stored in a list. The graph does not change while the simulation runs — only the occupancy does, and it never modifies the paths — so there is no reason to recompute them at every turn.

### Known limitations
- The arrival estimate treats each path in isolation, whereas paths sharing a segment also share its capacity. On hard_3, this costs one turn: some drones are sent along the overflow route while the direct one would have been faster. A more accurate model would compute the throughput of the whole set of paths taken together, accounting for shared segments.

- Since each drone receives its path in advance, it cannot take an alternative route even when one is free. On a test map with two separate exits, drones queued in front of a busy exit while the other stayed empty, because it did not belong to their assigned path. Dynamic rerouting would solve this, at the cost of recomputing assignments during the simulation.

- When the shortest path directly connects start to end, the extraction process does not find an alternative path, since there are no intermediate zones to exclude.

## Visual representation
For each turn, the visualization shows the turn number, the number of drones moved and the number of drones delivered.

Each path is displayed with its cost and its throughput.

Every zone is printed in its own color, followed by its occupancy and the drones it currently holds. A drone in transit appears on the connection arrow rather than in a zone. A star next to a drone name means it did not move this turn.

This makes blocking situations immediately visible. On hard_1, at turn 8, a drone is marked as blocked in maze_c2 while bottleneck still has a free slot — showing that the limiting factor is the link capacity, not the zone. The required output format only lists movements, so this information cannot be read from it.

## Example

### Input map
```
# Easy Level 2: Simple fork with two paths
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```
### Terminal output
Colors are not rendered in this file; the actual terminal output is colored.
```
Turn: 1    Drones moved: 2    Drones delivered: 0/4
------------------------------------------------------
Path 1 (cost 3, throughput 1)
  start[2] -> junction[2/2]D3,D4 -> path_a[0/1] -> goal[0]
Path 2 (cost 3, throughput 1)
  start[2] -> junction[2/2]D3,D4 -> path_b[0/1] -> goal[0]

Turn: 2    Drones moved: 4    Drones delivered: 0/4
------------------------------------------------------
Path 1 (cost 3, throughput 1)
  start[0] -> junction[2/2]D1,D2 -> path_a[1/1]D3 -> goal[0]
Path 2 (cost 3, throughput 1)
  start[0] -> junction[2/2]D1,D2 -> path_b[1/1]D4 -> goal[0]

Turn: 3    Drones moved: 4    Drones delivered: 2/4
------------------------------------------------------
Path 1 (cost 3, throughput 1)
  start[0] -> junction[0/2] -> path_a[1/1]D1 -> goal[2]
Path 2 (cost 3, throughput 1)
  start[0] -> junction[0/2] -> path_b[1/1]D2 -> goal[2]

Turn: 4    Drones moved: 2    Drones delivered: 4/4
------------------------------------------------------
Path 1 (cost 3, throughput 1)
  start[0] -> junction[0/2] -> path_a[0/1] -> goal[4]
Path 2 (cost 3, throughput 1)
  start[0] -> junction[0/2] -> path_b[0/1] -> goal[4]
```

### Required output format (log.txt)
```
D3-junction D4-junction
D3-path_a D1-junction D4-path_b D2-junction
D3-goal D1-path_a D4-goal D2-path_b
D1-goal D2-goal
```
