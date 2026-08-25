from models import NbDrone, ZoneModel, ConnectionModel
from pydantic import ValidationError
import sys


class Drone():
    def _init_(self, name):
        self.name = name


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


class Connection():
    def __init__(self, name_zone1: str, name_zone2: str,
                 max_link_capacity=1) -> None:
        self.name_zone1 = name_zone1
        self.name_zone2 = name_zone2
        self.max_link_capacity = max_link_capacity


class Graph():
    def __init__(self):
        self.hub = []

    def add_zone(self, zone: Zone):
        self.hub.append(zone)


class ParseError(Exception):
    def __init__(self, line: int | None, cause: str) -> None:
        self.line = line
        self.cause = cause
        msg = f"Error line {line}: {cause}" if line else f"Error: {cause}"
        super().__init__(msg)


class MapParser():
    def __init__(self, name_file: str) -> None:
        self.name_file = name_file
        self.parse_input_file(self.read_mapfile())

    def read_mapfile(self) -> list:
        result = []
        try:
            with open(self.name_file, 'r') as map_file:
                result = map_file.readlines()
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            print(e)
            sys.exit(1)
        return result

    @staticmethod
    def parse_line_zone(value: list, prefix: str, i: int) -> dict:
        result = {}
        all_value = value.rsplit('[', 1)
        each_value = all_value[0].split()
        if len(each_value) == 3:
            result.update(
                {'prefix': prefix,
                 'name': each_value[0],
                 'positionx': each_value[1],
                 'positiony': each_value[2]})
        else:
            raise ParseError(
                i + 1,
                f"'{prefix}' must be written as "
                f"'{prefix}: <name '-' and ' ' is forbidden> <int(x)> <int(y)>"
                " metadata]'"
                )

        if len(all_value) == 2:
            option_value = "".join(all_value[1]).rsplit(']', 1)
            if len(option_value) != 2:
                raise ParseError(i + 1, ": metadata must be enclosed in "
                                 "brackets: [key=value ...]")
            if len(option_value) == 2 and option_value[1]:
                raise ParseError(
                    i + 1,
                    f"'{prefix}' must be written as "
                    f"'{prefix}: <name '-' and ' ' is forbidden> "
                    "<int(x)> <int(y)> [metadata]'"
                    )
            option_value = option_value[0].split()
            key_valid = {'zone', 'color', 'max_drones'}
            for opt in option_value:
                lst_opt = opt.split('=')
                if (len(lst_opt) != 2) or (not lst_opt[0] or not lst_opt[1]):
                    raise ParseError(i + 1, "metadata must be written as "
                                     "key=value")
                k, v = lst_opt
                if k not in key_valid:
                    raise ParseError(i + 1, f"unknown metadata key '{k}': "
                                     "allowed keys are 'zone', 'color' and "
                                     "'max_drones'")
                result[k] = v
        return result

    @staticmethod
    def parse_line_connection(value: str, prefix: str, i: int) -> dict:
        value_and_metadata = value.rsplit('[', 1)
        connection = value_and_metadata[0].split('-')
        dict_connection = {}
        if len(connection) == 2:
            zone1, zone2 = connection
            if not zone1:
                raise ParseError(i + 1, "connection requires two zone names "
                                 "separated by '-'")
            if not zone2:
                raise ParseError(i + 1, "connection requires two zone names "
                                 "separated by '-'")
            dict_connection = {'zone1': zone1.strip(), 'zone2': zone2.strip()}
        else:
            raise ParseError(i + 1, f"'{prefix}' must be written as "
                             f"'{prefix}: <name_zone1>-<name_zone2> "
                             "[metadata]'")
        if len(value_and_metadata) == 2:
            metadata_value = "".join(value_and_metadata[1]).rsplit(']', 1)
            if len(metadata_value) != 2:
                raise ParseError(i + 1, ": metadata must be enclosed in "
                                 "brackets: [key=value ...]")
            if len(metadata_value) == 2 and metadata_value[1]:
                raise ParseError(i + 1, f"'{prefix}' must be written as "
                                 f"'{prefix}: <name_zone1>-<name_zone2> "
                                 "[metadata]'")
            metadata = metadata_value[0].split()
            key_valid = {'max_link_capacity'}
            for data in metadata:
                lst_data = data.split('=')
                if ((len(lst_data) != 2) or
                   (not lst_data[0] or not lst_data[1])):
                    raise ParseError(i + 1, "metadata must be written as "
                                     "key=value")
                k, v = lst_data
                if k not in key_valid:
                    raise ParseError(i + 1, f"unknown metadata key '{k}': "
                                     "allowed key are 'max_link_capacity'")
                dict_connection[k] = v
        return dict_connection

    def parse_input_file(self, result: list) -> list:
        name_zones = set()
        starthub = False
        endhub = False
        nbdrone = False
        count_line = 0
        seen: set = set()

        for i, res in enumerate(result):
            if res.strip().startswith('#'):
                continue
            line = res.strip().split(':', 1)
            if len(line) == 1 and not line[0]:
                continue
            elif len(line) == 2:
                prefix = line[0].strip()
                value = line[1].strip()
                count_line += 1
            else:
                raise ParseError(i + 1, "missing ':' separator "
                                 "(expected '<keyword>: <value>')")

            if count_line == 1:
                if prefix == 'nb_drones':
                    try:
                        dict_nb_drones = {prefix: value}
                        NbDrone(**dict_nb_drones)
                        nbdrone = True
                    except ValidationError as e:
                        raise ParseError(i + 1, e.errors()[0]['msg'])
                else:
                    raise ParseError(i + 1, "the first line must be "
                                     "'nb_drones: <positive_integer>'")
            else:
                if prefix == 'start_hub':
                    if starthub:
                        raise ParseError(i + 1, ": duplicate 'start_hub':"
                                         "exactly one start_hub is allowed")
                    else:
                        starthub = True
                    result_line = self.parse_line_zone(value, prefix, i)
                    try:
                        starthub_model = ZoneModel(**result_line)
                        dict_zone = starthub_model.model_dump()
                        zone = Zone(**dict_zone)
                        if zone.name in name_zones:
                            raise ParseError(i + 1, "Error")
                        name_zones.add(zone.name)
                        Graph().add_zone(zone)
                    except ValidationError as e:
                        print(f"Error line {i + 1}:", e.errors()[0]['msg'])
                        sys.exit(1)

                elif prefix == 'end_hub':
                    if endhub:
                        raise ParseError(i + 1, ": duplicate 'end_hub': "
                                         "exactly one end_hub is allowed")
                    else:
                        endhub = True

                    result_line = self.parse_line_zone(value, prefix, i)
                    try:
                        endhub_model = ZoneModel(**result_line)
                        dict_zone = endhub_model.model_dump()
                        zone = Zone(**dict_zone)
                        if zone.name in name_zones:
                            raise ParseError(i + 1, "Error")
                        name_zones.add(zone.name)
                        Graph().add_zone(zone)
                    except ValidationError as e:
                        raise ParseError(i + 1, e.errors()[0]['msg'])

                elif prefix == 'hub':

                    result_line = self.parse_line_zone(value, prefix, i)
                    try:
                        hub_model = ZoneModel(**result_line)
                        dict_zone = hub_model.model_dump()
                        zone = Zone(**dict_zone)
                        if zone.name in name_zones:
                            raise ParseError(i + 1, "Error")
                        name_zones.add(zone.name)
                        Graph().add_zone(zone)
                    except ValidationError as e:
                        raise ParseError(i + 1, e.errors()[0]['msg'])

                elif prefix == 'connection':
                    result_line = self.parse_line_connection(value, prefix, i)
                    try:
                        if result_line['zone1'] not in name_zones:
                            raise ParseError(i + 1, "unknown zone "
                                             f"'{result_line['zone1']}': "
                                             "zones must be defined before "
                                             "being used in a connection")
                        elif result_line['zone2'] not in name_zones:
                            raise ParseError(i + 1, "unknown zone "
                                             f"'{result_line['zone2']}': "
                                             "zones must be defined before "
                                             "being used in a connection")
                        else:
                            if ((result_line['zone1'], result_line['zone2'])
                               in seen or (result_line['zone2'],
                                           result_line['zone1']) in seen):
                                raise ParseError(i + 1, "duplicate connection "
                                                 f"'{result_line['zone1']}-"
                                                 f"{result_line['zone2']}'")
                            seen.add((result_line['zone1'],
                                      result_line['zone2']))
                            connection_model = ConnectionModel(**result_line)
                    except ValidationError as e:
                        raise ParseError(i + 1, e.errors()[0]['msg'])
                else:
                    raise ParseError(i + 1, f"Error line {i + 1}: unknown "
                                     f"prefix '{prefix}':"
                                     " only 'nb_drones', 'start_hub', "
                                     "'end_hub', "
                                     "'hub' and 'connection' are allowed")
        if not nbdrone:
            raise ParseError(None, "the first line must be "
                             "'nb_drones: <positive_integer>'")
        if not starthub:
            raise ParseError(None, "missing 'start_hub': exactly one start_hub"
                             " is required")
        if not endhub:
            raise ParseError(None, "missing 'end_hub': exactly one end_hub"
                             " is required")


MapParser('map.txt')

