import time
import logging
import os


class Logger:
    """
    Automatically create folder structure such as logs/01 08 2023 some_group/some_script_log_1.log
    """

    def __init__(self, name_file: str, group_name: str = None) -> None:
        self.__set_logger(group_name, name_file)

    def __create_if_not_exist(self, path) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def __set_logger(self, group_name, name_file: str = None):
        path = f"logs/"
        if group_name:
            path += f"{time.strftime('%d-%m-%Y')} {group_name}/"

        self.__create_if_not_exist(path)
        path += f"{name_file}_{len([name for name in os.listdir(path)]) + 1}.log"

        print(f"logger setup to: {path}")
        logging.basicConfig(
            filename=path,
            encoding="utf-8",
            level=logging.DEBUG,
        )

    def log_message_info(self, message: str) -> None:
        log_message = f"{time.ctime()} {message}"
        logging.info(log_message)

    def log_message_error(self, message: str, exception=None) -> None:
        log_message = f"{time.ctime()} {message}."
        if exception:
            log_message += f" Exception: {exception}"
        logging.error(log_message)

    def log_message_warning(self, message: str) -> None:
        log_message = f"{time.ctime()} {message}."
        logging.warning(log_message)
