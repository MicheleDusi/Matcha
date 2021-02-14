from matplotlib import pyplot as plt
import cv2


def show_image(img) -> None:
    """
    Showing the image.
    :param img: The image to show
    """
    plt.imshow(img, interpolation='nearest')
    plt.show()


def load_image(filepath: str):
    """
    Loading an image from file.
    :param filepath: The path of the file image
    :return: An image, as a numpy array
    """
    img = cv2.imread(filepath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
