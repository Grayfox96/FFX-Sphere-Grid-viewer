from dataclasses import dataclass
from math import atan2, degrees

from .node import Node
from .utils import add_bytes


@dataclass
class Link:
    node_1: Node
    node_2: Node
    centre_node: Node | None

    def __str__(self) -> str:
        string = f'Link {self.node_1} -> {self.node_2}'
        if self.centre_node is not None:
            string += f' (arc, centre {self.centre_node})'
        return string

    def get_angle(self, node: Node) -> float:
        y = (node.y - self.centre_node.y) * -1
        x = node.x - self.centre_node.x
        return degrees(atan2(y, x))

    @property
    def angle_1(self) -> float:
        return self.get_angle(self.node_1)

    @property
    def angle_2(self) -> float:
        return self.get_angle(self.node_2)


def parse_link(data: list[int], nodes: list[Node]) -> Link:
    node_1 = nodes[add_bytes(*data[:2])]
    node_2 = nodes[add_bytes(*data[2:4])]
    anchor_node_index = add_bytes(*data[4:6])
    if anchor_node_index == 0xffff:
        anchor_node = None
    else:
        anchor_node = nodes[anchor_node_index]
    return Link(node_1, node_2, anchor_node)


LINK_LENGTH = 8
