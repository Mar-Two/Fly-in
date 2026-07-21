from models import NbDrone, ZoneModel
from pydantic import ValidationError
import sys


class Zone():
    def __init__(self, name: str, x: int, y: int, color=None,
                 zone='normal', max_drones=1) -> None:
        pass


class MapParser():
    def __init__(self, name_file):
        self.name_file = name_file

    def read_mapfile(self) -> list:
        result = []
        with open(self.name_file, 'r') as map_file:
            result = map_file.readlines()
        return result

    def clean_input(self, result: list) -> list:
        starthub = False
        endhub = False
        for i, res in enumerate(result):
            if "".join(res).startswith('#'):
                continue
            line = res.strip().split(':', 1)
            if len(line) == 1 and not line[0] and not i == 0:
                continue
            elif len(line) == 2:
                prefix = line[0].strip()
                value = line[1].strip()
            else:
                print(f"Error line {i + 1}: missing ':' separator (expected '<keyword>: <value>')", file=sys.stderr)
                sys.exit(1)

            if i == 0:
                if prefix == 'nb_drones':
                    try:
                        dict_nb_drones = {prefix: int(value)}
                        NbDrone(**dict_nb_drones)
                    except (ValueError, ValidationError):
                        print(f"Error line {i + 1}: 'nb_drones' must be written "
                              "as 'nb_drones: <number greater than 0>'",
                              file=sys.stderr)
                        sys.exit(1)
                else:
                    print(f"Error line {i + 1}: 'nb_drones' must be written "
                          "as 'nb_drones: <number greater than 0>'",
                          file=sys.stderr)
                    sys.exit(1)

            if len(line) == 2 and i != 0:
                if prefix == 'start_hub':
                    start_dict = {}
                    if starthub:
                        print('False')
                    else:
                        starthub = True

                    all_value = "".join(value).rsplit('[', 1)
                    print(all_value)
                    each_value = "".join(all_value[0]).split()
                    if len(each_value) == 3:
                        try:
                            start_dict.update({'prefix': prefix, 'name': each_value[0],
                                               'positionx': int(each_value[1]),
                                               'positiony': int(each_value[2])})
                        except ValueError:
                            print(f"Error line {i + 1}: '{prefix}' must be written "
                                  f"as '{prefix}: <name '-' is forbidden> <int(x)> <int(y)> [metadata]'",
                                  file=sys.stderr)
                            sys.exit(1)
                    else:
                        print(f"Error line {i + 1}: '{prefix}' must be written "
                              f"as '{prefix}: <name '-' is forbidden> <int(x)> <int(y)> [metadata]'",
                              file=sys.stderr)
                        sys.exit(1)

                    if len(all_value) == 2:
                        option_value = "".join(all_value[1]).rsplit(']', 1)
                        if len(option_value) == 2 and option_value[1]:
                            print(f"Error line {i + 1}: '{prefix}' must be written "
                                  f"as '{prefix}: <name '-' is forbidden> <int(x)> <int(y)> [metadata]'",
                                  file=sys.stderr)
                            sys.exit(1)
                        option_value = option_value[0].split()
                        for opt in option_value:
                            set_opt = {'zone', 'color'}
                            print(opt)
                            try:
                                key, value = opt.split('=')
                                if key not in set_opt:
                                    raise ValueError()
                                start_dict[key] = value
                            except (IndexError, ValueError, ValidationError):
                                print(f"Error line {i + 1}: metadata must be written as key=value.\nAllowed keys are 'zone', 'color' and 'max_drones'", file=sys.stderr)
                                sys.exit(1)
                    try:
                        zz = ZoneModel(**start_dict)
                        print(zz)
                    except (ValidationError):
                        print(f"Error line {i + 1}: '{prefix}' must be written "
                              f"as '{prefix}: <name '-' is forbidden> <int(x)> <int(y)> [metadata]'",
                              file=sys.stderr)
                        sys.exit(1)
                elif prefix == 'end_hub':
                    print('end_hub')
                elif prefix == 'hub':
                    print('hub')
                elif prefix == 'connection':
                    print('connection')
                else:
                    print(f"Error line {i + 1}: unknown prefix '{prefix}':"
                          " only 'nb_drones', 'start_hub', 'end_hub', "
                          "'hub' and 'connection' are allowed",
                          file=sys.stderr)
                    sys.exit(1)


obj = MapParser('map.txt')
result = obj.read_mapfile()
obj.clean_input(result)
