from tiles import TileFactory
from mosaic import Mosaic
from math import sqrt

TILES_DIRECTORY = "tiles/"
TILES_INFO = "tiles/tiles_info.csv"

IMAGE_FILE: str = "image/shrek3.jpg"

IMAGE_ROWS: int = 14 * 3
IMAGE_COLS: int = 19 * 3
# IMAGE_ROWS: int = 1
# IMAGE_COLS: int = 2

# Main
if __name__ == '__main__':
    print('Creating tiles... ')
    tiles = TileFactory.create_from_file(TILES_INFO, TILES_DIRECTORY)
    print('Done')

    total = TileFactory.count_quantity(tiles_list=tiles)
    print(f"Based on the tiles quantity ({total}), the average side lenght of the mosaic is: {sqrt(total)}")

    # t = tiles[0]
    # print("--------")
    # print(t.name)
    # print(t.image.shape)
    # t.print_coords()

    print("Creating mosaic...")
    mos = Mosaic(IMAGE_FILE, tiles=tiles, grid=(IMAGE_ROWS, IMAGE_COLS), reinsertion=True)
    print('Done')

    print("Composing mosaic...")
    mos.assign_tiles()
    cells = mos.cells
    print("Done")

    # print("Results:")
    # for cell in cells:
    #     print(f"Cell in position {cell.position} : {cell.assigned_tile.name}")

    mos.show_preview()
