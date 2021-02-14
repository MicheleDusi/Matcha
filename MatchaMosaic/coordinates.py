import numpy as np

SAMPLES_ROWS: int = 3
SAMPLES_COLS: int = 3


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


def sample_colors(img_cut):
    (height, width, channels) = img_cut.shape
    (cell_h, cell_w) = height // SAMPLES_ROWS, width // SAMPLES_COLS
    if cell_h == 0 or cell_w == 0:
        raise Exception("Found sub-image with a 0 dimension")

    colors = np.zeros(shape=(SAMPLES_ROWS, SAMPLES_COLS, channels))

    # Iterating over the pixels
    # for i in range(height):
    #     row: int = i // cell_h
    #     if row >= SAMPLES_ROWS:
    #         break
    #
    #     for j in range(width):
    #         col: int = j // cell_w
    #         if col >= SAMPLES_COLS:
    #             break
    #
    #         # Accumulating the pixel values
    #         colors[row][col] += img_cut[i][j]
    #
    # colors /= (cell_h * cell_w)

    for i in range(SAMPLES_ROWS):
        for j in range(SAMPLES_COLS):
            verti_slice = slice(i * cell_h, (i + 1) * cell_h)
            horiz_slice = slice(j * cell_w, (j + 1) * cell_w)
            img_cell = img_cut[verti_slice, horiz_slice, :]
            colors[i, j] = sample_color(img_cell)

    return colors


def extract_coords(img):
    """
    Takes an image and returns a vector of coordinates, i.e. of features that will place the tile in the features space.
    This function is used to represent the important characteristics of a tile, based on which the mosaic will be composed.
    At the moment, the extracted coordinates are:
    - Sample colors as average colors of cells in a NxM grid
    :param img: An image as a numpy array, better if it's with 3 channels (RGB)
    :return: a vector of coordinates
    """
    colors = sample_colors(img)
    coords = colors.flatten()
    return coords
