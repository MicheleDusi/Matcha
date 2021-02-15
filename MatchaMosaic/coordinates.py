import numpy as np
from abc import ABC, abstractmethod

ZERO_THRESHOLD: float = 1e-10


class Operator(ABC):
    """
    Inner class of "Coordinator".
    Abstract class for all the operators which compute the coordinates.
    """

    def __init__(self, weight: float = 1.0):
        # Checks if the weight is near zero
        if abs(weight) < ZERO_THRESHOLD:
            raise Warning("The weight is almost zero: the operator will have no effect")
        # Checks if the weight is negative
        elif weight < 0:
            raise Warning("The weight is negative: this can work, but it's usually not recommended")
        self.__weight = weight

    @abstractmethod
    def compute(self, img) -> np.ndarray:
        """
        Given an image, it computes the vector of coordinates based on the strategy it implements.
        The vector has to be flatten at the end && it has to be weighted according to the operator's weight.
        :param img: The input image
        :return: The vector of coordinates
        """
        pass

    @property
    def weight(self):
        return self.__weight


class AverageSamplerOperator(Operator):

    DEFAULT_SAMPLING_GRID = (1, 1)

    def __init__(self, grid: (int, int) = DEFAULT_SAMPLING_GRID, weight: float = 1):
        super().__init__(weight)
        if grid[0] <= 0 or grid[1] <= 0:
            raise Exception(f"Illegal grid values: {grid}. Please use only positive values.")
        self.__grid = grid

    @staticmethod
    def sample_color(img_cut):
        """
        This function samples the average color of an image.
        :param img_cut: The portion of the image (a numpy array)
        :return: The average value, for each channel of the original image
        """
        if img_cut is None:
            raise Exception("Impossible to compute the average color of a null image")
        avg_color_per_row = np.average(img_cut, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return avg_color

    def compute(self, img_cut):
        (height, width, channels) = img_cut.shape
        cell_h = height // self.__grid[0]
        cell_w = width // self.__grid[1]
        if cell_h == 0 or cell_w == 0:
            raise Exception("Found sub-image with a 0 dimension")

        colors = np.zeros(shape=(self.__grid[0], self.__grid[1], channels))

        for i in range(self.__grid[0]):
            for j in range(self.__grid[1]):
                verti_slice = slice(i * cell_h, (i + 1) * cell_h)
                horiz_slice = slice(j * cell_w, (j + 1) * cell_w)
                img_cell = img_cut[verti_slice, horiz_slice, :]
                colors[i, j] = self.sample_color(img_cell)

        return colors.flatten() * self.weight


class Coordinator:
    """
    A Coordinator is an object used to compute coordinates.
    It's composed by different operators, meaning that it can be defined dynamically according to what it's needed.
    Every operator can work in different ways and can use different parameters; the resulting coordinates array for
    one single image will be the concatenation of the single arrays
    """

    def __init__(self):
        self.__finalized = False
        self.__operators = []

    def add_operator(self, operator: Operator) -> None:
        """
        Adds an operator to the list of the strategies used to compute the vector of coordinates.
        :param operator: The new strategy to be used
        :return: None
        """
        if not operator:
            raise Exception("Cannot use a null operator into the coordinator")
        elif self.__finalized:
            raise Exception("Cannot add new operators: the coordinator has already been finalized")
        self.__operators.append(operator)

    def finalize(self) -> bool:
        """
        Finalizes the coordinator.
        This means it stops the creation process, allowing the instance to be used.
        The method also returns the previus value of finalization:
            - If it returns True, the coordinator was already finalized.
            - If it returns False, the coordinator has just been finalized for the first time.
        :return: The previous value of finalization.
        """
        aux = self.__finalized
        self.__finalized = True
        return aux

    def compute(self, img) -> np.ndarray:
        """
        Given an image, this method computes a vector of coordinates (i.e. of features that will place the image in the
        features space), according to the operator list defined before.
        :param img: The image whose coordinates we want to compute, as a numpy array
        :return: An array of coordinates, as a numpy array with <float> data type
        """
        if not self.__finalized:
            raise Exception("Cannot use a coordinator until it's been finalized")
        coords = []
        for op in self.__operators:
            coords.extend(op.compute(img))
        return np.array(coords)
