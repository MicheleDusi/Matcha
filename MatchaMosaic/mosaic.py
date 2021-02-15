import numpy as np
from cells import Cell
from coordinates import Coordinator
from tiles import Tile
from utilities import show_image, load_image
import cv2

DEFAULT_GRID_SHAPE = (10, 10)
DEFAULT_REINSERTION = False


class Mosaic:
    """
    A mosaic is the representation of an image throught the available tiles.
    """

    def __init__(self, targetpath: str,
                 coordinator: Coordinator,
                 tiles: [Tile],
                 grid: (int, int) = DEFAULT_GRID_SHAPE,
                 reinsertion: bool = DEFAULT_REINSERTION):

        if not targetpath:
            raise Exception("Cannot create a mosaic without the target image")
        self.__original = load_image(targetpath)

        if not coordinator:
            raise Exception("Cannot create a mosaic without specifying how to extract coordinates")
        self.__coordinator = coordinator

        if not tiles or len(tiles) == 0:
            raise Exception("Cannot create a mosaic without a tiles list")

        self.__grid = grid
        cell_h = int(self.original.shape[0] / grid[0])
        cell_w = int(self.original.shape[1] / grid[1])
        print(f"Set cells with dimension: vertical = {cell_h}, horizontal = {cell_w}")
        self.__scale = (cell_h, cell_w)
        self.cells = []
        for i in range(grid[0]):
            for j in range(grid[1]):
                self.cells.append(
                    Cell(
                        (i, j),
                        self.original[
                            slice(i * cell_h, (i + 1) * cell_h),
                            slice(j * cell_w, (j + 1) * cell_w),
                            :
                        ],
                        self.__coordinator,
                        tiles
                    )
                )

        self.__reinsertion = reinsertion

    def assign_tiles(self) -> None:
        """
        Core method.
        It takes the available tiles and it assign a tile to every cell.
        The strategy for the assignment can vary; the default one assignes the cell
        with the minimum distance to a tile, based on the coordinates computation.
        """
        unassigned_cells: [Cell] = self.cells.copy()
        # print("To-Be-Assigned cells list:")
        # for c in unassigned_cells:
        #     print(f" -> {c.position}")

        # Assigning all the cells to a tile
        while len(unassigned_cells) > 0:
            # print(f"{len(unassigned_cells)} unassigned cells left")
            # Sorting the cells depending on the distance
            unassigned_cells.sort(key=Cell.get_nearest_distance)
            # Extracting the fittest cell
            cell = unassigned_cells.pop(0)
            # The cell with the minimum distance get assigned
            # The usage of the tile is registered (decrease_availability = True)
            # iff the reinsertion is not used (self.__reinsertion = False)
            cell.assign_tile(decrease_availability=not self.__reinsertion)
            # print(f"Assigned cell {cell.position} to tile : {cell.assigned_tile.name}")

    @property
    def original(self):
        return self.__original

    def get_preview(self) -> []:
        (height, width) = (self.original.shape[0], self.original.shape[1])
        mosaic = np.zeros(shape=(height, width, 3), dtype=np.uint8)
        for cell in self.cells:
            (i, j) = cell.position
            # print(f"i = {i}, j = {j}")
            # print(f'Tile "{cell.assigned_tile.name}" has shape = {cell.assigned_tile.image.shape}')
            res_tile = cv2.resize(cell.assigned_tile.image, dsize=(self.__scale[1], self.__scale[0]), interpolation=cv2.INTER_CUBIC)
            # print(f'Tile image has been resized to shape = {res_tile.shape}, equal to scale = {self.__scale}')
            verti_slice = slice(i * self.__scale[0], (i + 1) * self.__scale[0])
            horiz_slice = slice(j * self.__scale[1], (j + 1) * self.__scale[1])
            # print(f'Vertical slice = {verti_slice}, horizontal slice = {horiz_slice}')
            mosaic[verti_slice, horiz_slice] = res_tile

        return mosaic

    def show_preview(self) -> None:
        show_image(self.get_preview())
