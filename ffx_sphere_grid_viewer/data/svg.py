import xml.etree.ElementTree as ET
from logging import getLogger

from .utils import get_resource_path, open_cp1252

type Polygon = tuple[tuple[float, float]]


def load_polygon(file_path: str) -> Polygon:
    absolute_file_path = get_resource_path(file_path)
    try:
        with open_cp1252(absolute_file_path) as file_object:
            tree = ET.parse(file_object)
    except FileNotFoundError:
        getLogger(__name__).error(f'File "{absolute_file_path}" was not found')
        return tuple()
    paths = [p for p in tree.iter('{http://www.w3.org/2000/svg}path')]
    if not paths:
        getLogger(__name__).error(
            f'No "path" elements found in "{absolute_file_path}"')
        return tuple()
    points_string = paths[0].attrib['d'].strip('MZz ').split(' L ')
    try:
        points = tuple(tuple(float(c) for c in point_string.split())
                       for point_string in points_string)
    except ValueError:
        getLogger(__name__).error(
            f'Couldn\'t parse attribute "d" of "path" item with id '
            f'"{paths[0].attrib['id']}" in file "{absolute_file_path}"')
        return tuple()
    return points


APPEARANCES = [
    load_polygon('data_files/icons/l_3_lock.svg'),
    [],  # no graphic for empty node
    load_polygon('data_files/icons/strength.svg'),
    load_polygon('data_files/icons/magic.svg'),
    load_polygon('data_files/icons/defense.svg'),
    load_polygon('data_files/icons/magic_defense.svg'),
    load_polygon('data_files/icons/accuracy.svg'),
    load_polygon('data_files/icons/evasion.svg'),
    load_polygon('data_files/icons/luck.svg'),
    load_polygon('data_files/icons/agility.svg'),
    load_polygon('data_files/icons/hp.svg'),
    load_polygon('data_files/icons/mp.svg'),
    load_polygon('data_files/icons/white_magic.svg'),
    load_polygon('data_files/icons/black_magic.svg'),
    load_polygon('data_files/icons/skill.svg'),
    load_polygon('data_files/icons/special.svg'),
    load_polygon('data_files/icons/l_4_lock.svg'),
    load_polygon('data_files/icons/l_2_lock.svg'),
    load_polygon('data_files/icons/l_1_lock.svg'),
]
