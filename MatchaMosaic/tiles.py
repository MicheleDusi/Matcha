import os

import numpy as np

from coordinates import Coordinator
from utilities import show_image, load_image
import csv

# Margins for the preprocessing of a tile image
MARGIN_TOP = 100
MARGIN_BOTTOM = 50
MARGIN_LEFT = 50
MARGIN_RIGHT = MARGIN_LEFT

CSV_COL_NAME = "name"
CSV_COL_FILENAME = "filename"
CSV_COL_QUANTITY = "quantity"


class Tile:
    """
    Tile class. A tile represents one usable asset in the final mosaic image.
    """

    def __init__(self, name: str, img: np.ndarray, coordinator: Coordinator, quantity: int = 1):
        """
        Constructor.
        :param name: The name used to univocally identify the tile
        :param img: The image the tile represent, as a numpy array with 3 channels
        :param quantity: The available quantity of the tile
        """
        self.name = name
        if img is None:
            raise Exception(f'No image found in creating tile "{name}"')

        cropped_img = self.preprocess_tile_image(img)
        self.__tile_image = cropped_img
        self.coords = coordinator.compute(cropped_img)

        if quantity < 1:
            raise Exception("No tile can have zero quantity available. Please set a positive number")
        self.__qty = quantity

    @property
    def image(self):
        return self.__tile_image

    def is_available(self) -> bool:
        return self.__qty > 0

    def use(self, quantity: int = 1) -> None:
        if self.__qty < quantity:
            raise Exception(f"Impossible to use the requested quantity ({quantity}) of this tile: "
                            f"only {self.__qty} available")
        self.__qty -= quantity

    def print_coords(self) -> None:
        print(self.coords)

    @property
    def quantity(self):
        return self.__qty

    def show_preview(self):
        show_image(self.__tile_image)

    @classmethod
    def preprocess_tile_image(cls, img):
        """
        Preparing the image of a tile for the coordinates extraction.
        That includes:
         - Cropping the image to a predetermined size, by cutting lateral margins
        :param img: The original image
        :return: the preprocessed image
        """
        (height, width, channels) = img.shape

        if channels < 3:
            channels_slice = slice(0, channels)
        else:
            channels_slice = slice(0, 3)

        img_cut = img[
                  MARGIN_TOP:(height - MARGIN_BOTTOM),
                  MARGIN_LEFT:(width - MARGIN_RIGHT),
                  channels_slice
                  ]
        return img_cut


class TileFactory:

    def __init__(self, coordinator: Coordinator):
        if not coordinator:
            raise Exception("Impossible to create tiles without a system to extract coordinates")
        self.__coordinator = coordinator

    def create_from_folder(self, tiles_folder: str) -> [Tile]:
        """
        Creates a tiles list from a folder. In the folder this method expects to find the images of the tiles.
        Every image file (with ".png" or ".jpg" extension!) is used as a tile.
        The name of the tile will be the name of the file. The default quantity is set to 1.

        :param tiles_folder: The name of the folder where the tiles images are
        :return: The tiles array
        """
        tiles_list = []
        directory = os.fsencode(tiles_folder)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".png") or filename.endswith(".jpg"):
                print(f"Found tile image <{filename}>")
                # Extracting the name by cutting the file extension
                tilename = os.path.splitext(filename)[0]
                # Opening the image from the tiles folder, as a np array
                img = load_image(filename)
                # Creating the tile
                tiles_list.append(Tile(name=tilename, img=img, coordinator=self.__coordinator))
        return tiles_list

    def create_from_file(self, tiles_info: str, tiles_folder: str = "") -> [Tile]:
        """
        Creates a tiles list from a specific CSV file indicating:
        - The identification name for each tile     (Column name: name)
        - The path for the image file               (Column name: filename)
        - The available quantity for that tile      (Column name: quantity)
        Optionally, a folder name for the tiles can be expressed. If so, every path will have it as prefix.

        :param tiles_info: The CSV file guiding the creation of the tiles
        :param tiles_folder: An optional folder path where the images are stored
        :return: The tiles array
        """
        # Handling tiles_folder parameter
        if not tiles_folder:
            # Assuming the reference folder is the current one OR the whole path is contined in the csv
            tiles_folder = ""
        # Eventually adding the "/" to the name
        if not tiles_folder.endswith("/"):
            tiles_folder += "/"

        # Init tiles list
        tiles_list = []

        # Checking csv file
        if not tiles_info.endswith(".csv"):
            raise Exception("The information file is not in CSV format. A CSV file is required")

        # Reading CSV file
        with open(tiles_info, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                filename = row[CSV_COL_FILENAME]
                quantity = int(row[CSV_COL_QUANTITY])
                print(f'Tile "{row[CSV_COL_NAME]}", file: <{filename}>, quantity: {quantity}')
                # Opening the image from the tiles folder, as a np array
                img = load_image(tiles_folder + filename)
                # Creating the tile
                tile = Tile(name=row[CSV_COL_NAME], img=img, coordinator=self.__coordinator, quantity=quantity)
                tiles_list.append(tile)

        print(f"{len(tiles_list)} tiles correctly created")
        return tiles_list

    @classmethod
    def count_quantity(cls, tiles_list: [Tile]):
        count: int = 0
        for t in tiles_list:
            count += t.quantity
        return count
