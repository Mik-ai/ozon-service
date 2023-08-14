from config import TESSERACT_PATH

from PIL import Image
import pytesseract
import requests
import re


class PyTesseractOCR:
    """class for extracting text out of image"""

    __image_text: str

    def __init__(self) -> None:
        """tesseract must be installed locally, with rus language package for it"""
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    def __image_to_text(self, image) -> str:
        """getting text from image

        Args:
            image : image to process

        Returns:
            str: text extracted from image
        """
        some_str = pytesseract.image_to_string(
            image=image,
            lang="rus",
        )
        some_str.replace("\n", " ")
        some_str = re.sub("[^А-яёA-z]+", " ", some_str)
        self.__image_text = some_str.lower().strip()

    def check_text_on_image(self, check_list: list[str]) -> bool:
        """Check if text presents on image.
        Intentionally aggressive, it's better to check for an image that doesn't contain a problem, rather than skipping an image that does.

        Args:
            check_list (list[str]): str list to check each

        Returns:
            bool: if all str from check_list True
        """
        return all([x in self.__image_text for x in check_list])

    def open_and_process_image(self, image):
        """endpoint for processing image

        Args:
            image (_type_): image path to open
        """
        image = Image.open(image)
        self.__image_to_text(image)

    def download_and_process_image(self, url: str):
        """endpoint for processing image

        Args:
            url (str): image url to download
        """
        image = Image.open(requests.get(url, stream=True).raw)
        self.__image_to_text(image)

    def is_have_communication_issue(self, image):
        """Endpoint for checking image containing communication issue.

        Args:
            image (str): originally str path to image, can be changed in future

        Returns:
            bool: if issue is present True, else False
        """
        image = Image.open(image)
        self.__image_to_text(image)
        result = self.check_text_on_image(["наш", "сайт"])
        return result


def start_test():
    ocr_inst = PyTesseractOCR()
    ocr_result = ocr_inst.is_have_communication_issue("tesseract.png")
    print(ocr_result)
