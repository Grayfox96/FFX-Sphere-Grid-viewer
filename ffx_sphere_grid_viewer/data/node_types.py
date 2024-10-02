from dataclasses import dataclass
from enum import IntEnum
from typing import Self

from .svg import APPEARANCES, Polygon
from .text_characters import bytes_to_string
from .utils import add_bytes, get_resource_path, open_cp1252


class AppearanceType(IntEnum):
    L_3_LOCK = 0
    EMPTY_NODE = 1
    STRENGTH = 2
    MAGIC = 3
    DEFENSE = 4
    MAGIC_DEFENSE = 5
    ACCURACY = 6
    EVASION = 7
    LUCK = 8
    AGILITY = 9
    HP = 10
    MP = 11
    WHITE_MAGIC = 12
    BLACK_MAGIC = 13
    SKILL = 14
    SPECIAL = 15
    L_4_LOCK = 16
    L_2_LOCK = 17
    L_1_LOCK = 18


@dataclass(frozen=True)
class NodeType:
    node_effect_bit_field: int
    learned_move: int
    increase_amount: int
    appearance_type: AppearanceType
    name: str
    dash: str
    description: str
    other_text: str
    display_name: str
    color: str
    appearance: Polygon

    def __str__(self) -> str:
        return f'{self.name}'

    def __deepcopy__(self, memo) -> Self:
        return self


def parse_node_type(data: list[int], string_data: list[int]) -> NodeType:
    name_offset = add_bytes(*data[:2])
    dash_offset = add_bytes(*data[4:6])
    description_offset = add_bytes(*data[8:10])
    other_text_offset = add_bytes(*data[12:14])
    node_effect_bit_field = add_bytes(*data[16:18])
    learned_move = add_bytes(*data[18:20])
    increase_amount = add_bytes(*data[20:22])
    appearance_index = add_bytes(*data[22:24])
    name = bytes_to_string(string_data, name_offset)
    dash = bytes_to_string(string_data, dash_offset)
    description = bytes_to_string(string_data, description_offset)
    other_text = bytes_to_string(string_data, other_text_offset)
    appearance_type = AppearanceType(appearance_index)
    appearance = APPEARANCES[appearance_type]
    match appearance_index:
        case 0 | 1 | 16 | 17 | 18:
            display_name = ''
        case 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
            display_name = f'+{increase_amount}'
        case 10:
            display_name = f'+{increase_amount * 50}'
        case 11:
            display_name = f'+{increase_amount * 5}'
        case _:
            display_name = name
    color = NODETYPE_COLORS[appearance_index]
    node_type = NodeType(
        node_effect_bit_field, learned_move, increase_amount, appearance_type,
        name, dash, description, other_text, display_name, color, appearance)
    return node_type


def parse_panel(node_type_datas: list[list[int]],
                string_data: list[int],
                ) -> list[NodeType]:
    node_types = []
    for node_type_data in node_type_datas:
        node_types.append(parse_node_type(node_type_data, string_data))
    return node_types


def parse_panel_bin(file_path: str) -> list[NodeType]:
    with open(get_resource_path(file_path), mode='rb') as file_object:
        data = list(file_object.read())

    min_index = add_bytes(*data[8:10])
    max_index = add_bytes(*data[10:12])
    node_type_length = add_bytes(*data[12:14])
    total_length = add_bytes(*data[14:16])
    data_bytes = data[20:20+total_length]
    string_data = data[20+total_length:]
    node_type_datas = []
    start = 0
    for _ in range(max_index + 1 - min_index):
        node_type_data = data_bytes[start:start + node_type_length]
        node_type_datas.append(node_type_data)
        start += node_type_length
    return parse_panel(node_type_datas, string_data)


def parse_panel_csv(file_path: str) -> list[NodeType]:
    absolute_file_path = get_resource_path(file_path)
    with open_cp1252(absolute_file_path) as file_object:
        data = file_object.read()
    node_type_datas = [[int(b, 16) for b in line.split(',')]
                       for line in data.splitlines()]
    string_data = node_type_datas.pop()
    return parse_panel(node_type_datas, string_data)


NODETYPE_COLORS = {
    AppearanceType.HP: '#008100',
    AppearanceType.MP: '#006630',
    AppearanceType.STRENGTH: '#ff0000',
    AppearanceType.DEFENSE: '#0266cc',
    AppearanceType.MAGIC: '#ff0380',
    AppearanceType.MAGIC_DEFENSE: '#0000ff',
    AppearanceType.AGILITY: '#acad5b',
    AppearanceType.LUCK: '#726a21',
    AppearanceType.EVASION: '#dcde61',
    AppearanceType.ACCURACY: '#d5d99d',
    AppearanceType.WHITE_MAGIC: '#9a00cd',
    AppearanceType.BLACK_MAGIC: '#9a00cd',
    AppearanceType.SKILL: '#9a00cd',
    AppearanceType.SPECIAL: '#9a00cd',
    AppearanceType.EMPTY_NODE: '#888889',
    AppearanceType.L_1_LOCK: '#4b4b4b',
    AppearanceType.L_2_LOCK: '#4b4b4b',
    AppearanceType.L_3_LOCK: '#4b4b4b',
    AppearanceType.L_4_LOCK: '#4b4b4b',
}

try:
    NODE_TYPES = parse_panel_bin('data_files/panel.bin')
except FileNotFoundError:
    NODE_TYPES = parse_panel_csv('data_files/panel.csv')
