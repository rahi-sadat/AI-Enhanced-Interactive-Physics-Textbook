"""backend/circuits/topology/union_find.py

Disjoint Set Union (DSU) for electrical node clustering.
Groups connected wire endpoints, junctions, and component terminals into canonical electrical nodes.
"""
from __future__ import annotations

from typing import Dict, Generic, List, Set, TypeVar

T = TypeVar("T")


class UnionFind(Generic[T]):
    """Disjoint Set Union with path compression and union by rank."""

    def __init__(self) -> None:
        self.parent: Dict[T, T] = {}
        self.rank: Dict[T, int] = {}

    def add(self, item: T) -> None:
        """Add an item if not already in the structure."""
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item: T) -> T:
        """Find representative element with path compression."""
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
            return item

        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a: T, b: T) -> bool:
        """Union two sets. Returns True if sets were disjoint, False if already connected."""
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b
        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a
        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1

        return True

    def connected(self, a: T, b: T) -> bool:
        """Check if two elements belong to the same set."""
        return self.find(a) == self.find(b)

    def get_components(self) -> Dict[T, Set[T]]:
        """Return a mapping from canonical root to all elements in that set."""
        groups: Dict[T, Set[T]] = {}
        for item in self.parent:
            root = self.find(item)
            if root not in groups:
                groups[root] = set()
            groups[root].add(item)
        return groups
