import numpy as np

from coordinates import Coordinator
from tiles import Tile


class Cell:
    """
    Class representing a single cell of a mosaic.
    """

    def __init__(self, position: (int, int), img_cut: np.ndarray, coordinator: Coordinator, tiles: [Tile]):
        """
        Creates a cell from an image cut.
        :param position: The number of row and column identifying the cell (a tuple)
        :param img_cut: The numpy array representing the portion of image
        :param tiles: the referencing tiles
        """
        self.__pos = position
        self.coords = coordinator.compute(img_cut)
        # Order the tiles by increasing distances
        self.tiles = sorted(tiles, key=lambda x: self.measure_distance(x))
        self.assigned_tile = None
        # print("Cell creation completed")

    @property
    def position(self) -> (int, int):
        return self.__pos

    def get_nearest_available_tile_pair(self) -> (Tile, float):
        """
        Checks the mosaic tile in increasing distance order. The nearest one is returned, along with the distance.
        If a tile is no more available (i.e. it has non-positive quantity), then it's removed from the list.
        Note: the first available tile IS NOT removed. The deletion is done by another method.
        :return: The nearest tile and the distance
        """
        curr_tile = self.tiles[0]
        # Checks tile availability (quantity > 0)
        while not curr_tile.is_available():
            # Unavailable tiles are removed from the list
            self.tiles.pop(0)
            if not self.tiles:
                raise Exception("Available list is empty: cannot find an usable tile")
            curr_tile = self.tiles[0]
        # Returns the tile and the associated distance
        return curr_tile, self.measure_distance(curr_tile)

    def get_nearest_distance(self) -> float:
        """
        Checks the first mosaic tile available, then returns its distance (which is the minimum distance).
        If a tile is no more available (i.e. it has non-positive quantity), then it's removed from the list.
        :return: The minimum distance to the nearest tile
        """
        curr_tile: Tile = self.tiles[0]
        # Checks tile availability (quantity > 0)
        while not curr_tile.is_available():
            # Unavailable tiles are removed from the list
            self.tiles.pop(0)
            if not self.tiles:
                raise Exception("Available list is empty: cannot find an usable tile")
            curr_tile = self.tiles[0]
        # Returns the associated distance
        return self.measure_distance(curr_tile)

    def assign_tile(self, decrease_availability: bool = True):
        """
        Assign the cell to a tile.
        This method decreases the availability of the tile, calling the method "use" on it.
        """
        if not self.tiles[0].is_available():
            raise Exception("Impossible to assign an unavailable tile to this cell")
        self.assigned_tile = self.tiles[0]
        # If the usage has to be "registered"
        if decrease_availability:
            self.assigned_tile.use()

    def has_tile_assigned(self) -> bool:
        return self.assigned_tile is not None

    def measure_distance(self, tile: Tile) -> float:
        dist = np.linalg.norm(self.coords - tile.coords)
        return dist
