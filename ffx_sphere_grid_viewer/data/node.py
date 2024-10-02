from dataclasses import dataclass

from .cluster import Cluster
from .node_types import NODE_TYPES, NodeType
from .utils import add_bytes, s16


@dataclass
class Node:
    x: int
    y: int
    original_content: NodeType
    cluster: Cluster
    content: NodeType | None = None

    def __str__(self) -> str:
        return f'Node {self.content} @ ({self.x},{self.y})'


def parse_node(data: list[int], clusters: list[Cluster]) -> Node:
    x = s16(add_bytes(*data[:2]))
    y = s16(add_bytes(*data[2:4]))
    original_content_index = add_bytes(*data[6:8])
    if original_content_index >= len(NODE_TYPES):
        original_content = None
    else:
        original_content = NODE_TYPES[original_content_index]
    cluster = clusters[add_bytes(*data[8:10])]
    return Node(x, y, original_content, cluster)


NODE_LENGTH = 12
