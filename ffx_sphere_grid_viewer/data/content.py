from .node_types import NODE_TYPES, NodeType
from .utils import get_resource_path, open_cp1252


def parse_node_contents(node_contents_data: list[int],
                        ) -> list[NodeType | None]:
    node_contents = []
    for i in node_contents_data:
        if i >= len(NODE_TYPES):
            node_contents.append(None)
        else:
            node_contents.append(NODE_TYPES[i])
    return node_contents


def parse_node_contents_dat(file_path: str) -> list[NodeType | None]:
    with open(get_resource_path(file_path), mode='rb') as file_object:
        data = list(file_object.read())
    return parse_node_contents(data[8:])


def parse_node_contents_csv(file_path: str) -> list[NodeType | None]:
    absolute_file_path = get_resource_path(file_path)
    with open_cp1252(absolute_file_path) as file_object:
        data = file_object.read()
    node_contents_data = [int(i, 16) for i in data.splitlines()]
    return parse_node_contents(node_contents_data)


try:
    NODE_CONTENTS_ORIGINAL = parse_node_contents_dat('data_files/dat09.dat')
except FileNotFoundError:
    NODE_CONTENTS_ORIGINAL = parse_node_contents_csv('data_files/dat09.csv')
try:
    NODE_CONTENTS_STANDARD = parse_node_contents_dat('data_files/dat10.dat')
except FileNotFoundError:
    NODE_CONTENTS_STANDARD = parse_node_contents_csv('data_files/dat10.csv')
try:
    NODE_CONTENTS_EXPERT = parse_node_contents_dat('data_files/dat11.dat')
except FileNotFoundError:
    NODE_CONTENTS_EXPERT = parse_node_contents_csv('data_files/dat11.csv')
