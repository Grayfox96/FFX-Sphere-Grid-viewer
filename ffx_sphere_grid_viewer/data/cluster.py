from dataclasses import dataclass

from .utils import add_bytes, s16


@dataclass
class Cluster:
    x: int
    y: int
    maybe_type: int

    def __str__(self) -> str:
        return f'Cluster @ ({self.x},{self.y})'


def parse_cluster(data: list[int]) -> Cluster:
    x = s16(add_bytes(*data[:2]))  # signed
    y = s16(add_bytes(*data[2:4]))  # signed
    maybe_type = add_bytes(*data[6:8])
    return Cluster(x, y, maybe_type)


CLUSTER_LENGTH = 16
