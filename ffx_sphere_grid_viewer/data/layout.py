from dataclasses import dataclass

from .cluster import CLUSTER_LENGTH, Cluster, parse_cluster
from .content import (NODE_CONTENTS_EXPERT, NODE_CONTENTS_ORIGINAL,
                      NODE_CONTENTS_STANDARD)
from .link import LINK_LENGTH, Link, parse_link
from .node import NODE_LENGTH, Node, parse_node
from .node_types import NodeType
from .utils import add_bytes, get_resource_path, open_cp1252


@dataclass
class Layout:
    clusters: list[Cluster]
    nodes: list[Node]
    links: list[Link]


def parse_layout(cluster_datas: list[list[int]],
                 node_datas: list[list[int]],
                 link_datas: list[list[int]],
                 node_contents: list[NodeType],
                 ) -> Layout:
    clusters = [parse_cluster(d) for d in cluster_datas]
    nodes = [parse_node(d, clusters) for d in node_datas]
    for node, content in zip(nodes, node_contents):
        node.content = content
    links = [parse_link(d, nodes) for d in link_datas]
    return Layout(clusters, nodes, links)


def parse_layout_dat(file_path: str, node_contents: list[NodeType]) -> Layout:
    with open(get_resource_path(file_path), mode='rb') as file_object:
        data = list(file_object.read())

    cluster_count = add_bytes(*data[2:4])
    node_count = add_bytes(*data[4:6])
    link_count = add_bytes(*data[6:8])

    start = 16
    clusters = []
    for _ in range(cluster_count):
        clusters.append(data[start:start + CLUSTER_LENGTH])
        start += CLUSTER_LENGTH

    nodes = []
    for _ in range(node_count):
        nodes.append(data[start:start + NODE_LENGTH])
        start += NODE_LENGTH

    links = []
    for _ in range(link_count):
        links.append(data[start:start + LINK_LENGTH])
        start += LINK_LENGTH
    return parse_layout(clusters, nodes, links, node_contents)


def parse_layout_csv(file_path: str, node_contents: list[NodeType]) -> Layout:
    absolute_file_path = get_resource_path(file_path.format('clusters'))
    with open_cp1252(absolute_file_path) as file_object:
        clusters_data = file_object.read()
    absolute_file_path = get_resource_path(file_path.format('nodes'))
    with open_cp1252(absolute_file_path) as file_object:
        nodes_data = file_object.read()
    absolute_file_path = get_resource_path(file_path.format('links'))
    with open_cp1252(absolute_file_path) as file_object:
        links_data = file_object.read()
    datas = [[[int(b, 16) for b in line.split(',')]
             for line in data.splitlines()]
             for data in (clusters_data, nodes_data, links_data)]
    return parse_layout(*datas, node_contents)


try:
    LAYOUT_ORIGINAL = parse_layout_dat(
        'data_files/dat01.dat', NODE_CONTENTS_ORIGINAL)
except FileNotFoundError:
    LAYOUT_ORIGINAL = parse_layout_csv(
        'data_files/{}_dat01.csv', NODE_CONTENTS_ORIGINAL)
try:
    LAYOUT_STANDARD = parse_layout_dat(
        'data_files/dat02.dat', NODE_CONTENTS_STANDARD)
except FileNotFoundError:
    LAYOUT_STANDARD = parse_layout_csv(
        'data_files/{}_dat02.csv', NODE_CONTENTS_STANDARD)
try:
    LAYOUT_EXPERT = parse_layout_dat(
        'data_files/dat03.dat', NODE_CONTENTS_EXPERT)
except FileNotFoundError:
    LAYOUT_EXPERT = parse_layout_csv(
        'data_files/{}_dat03.csv', NODE_CONTENTS_EXPERT)
