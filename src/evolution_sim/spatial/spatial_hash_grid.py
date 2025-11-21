"""
SpatialHashGrid for neighbor and collision queries.

File location: src/evolution_sim/spatial/spatial_hash_grid.py

This is a lightweight grid that partitions the world into fixed-size cells.
It supports toroidal wrapping for the world coordinates and provides
fast neighborhood and local-cell queries used by creatures and the
environment for collision checks and sensing.
"""
import math
from collections import defaultdict


class SpatialHashGrid:
    """
    Grid partitions the world into cells for fast neighbor queries.
    Each cell stores: {'plant': [], 'herbivore': [], 'carnivore': []}.
    """

    def __init__(self, world_width, world_height, cell_size):
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        self.cols = math.ceil(world_width / cell_size)
        self.rows = math.ceil(world_height / cell_size)
        # cells: dict[(col,row)] -> {'plant': [...], 'herbivore': [...], 'carnivore': [...]}
        self.cells = {}

    def clear(self):
        self.cells = {}

    def _hash(self, x, y):
        # Toroidal wrap
        col = int(x // self.cell_size) % self.cols
        row = int(y // self.cell_size) % self.rows
        return (col, row)

    def insert(self, entity, x, y, entity_type: str):
        key = self._hash(x, y)
        if key not in self.cells:
            # Dict for types
            self.cells[key] = {'plant': [], 'herbivore': [], 'carnivore': []}
        # Defensive: ensure the type exists
        if entity_type not in self.cells[key]:
            self.cells[key][entity_type] = []
        self.cells[key][entity_type].append(entity)

    def _neighbor_keys(self, x, y):
        home_col, home_row = self._hash(x, y)
        for dcol in (-1, 0, 1):
            for drow in (-1, 0, 1):
                col = (home_col + dcol) % self.cols
                row = (home_row + drow) % self.rows
                yield (col, row)

    def query_neighborhood(self, x, y, entity_type: str = None):
        """Return list of entities in 3x3 neighborhood around (x,y).

        If entity_type is provided, only that type is returned.
        """
        results = []
        for key in self._neighbor_keys(x, y):
            if key in self.cells:
                if entity_type:
                    results.extend(self.cells[key].get(entity_type, []))
                else:
                    for lst in self.cells[key].values():
                        results.extend(lst)
        return results

    def query_local_cell(self, x, y, entity_type: str = None):
        """Return entities in the same cell as (x,y)."""
        key = self._hash(x, y)
        if key not in self.cells:
            return []
        if entity_type:
            return list(self.cells[key].get(entity_type, []))
        results = []
        for lst in self.cells[key].values():
            results.extend(lst)
        return results
