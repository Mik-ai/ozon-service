from sqlalchemy import create_engine
import time
# COPY AND RENAME TO config.py
OZON_CREDENTIALS = {
    "Host": "api-seller.ozon.ru",
    "Client-Id": "some_id",
    "Api-Key": "some_key",
    "Content-Type": "application/json",
}

OZON_BASE_URL = "https://api-seller.ozon.ru"
TESSERACT_PATH = r"D:\Program Files\tesseractOCR\tesseract.exe"


DB_LOGIN = "login"
DB_PASSWORD = "password"
DB_IP = "141.101.204.99:5432"
DB_NAME = "rusexpress"


def do_retry_on_fail(func):
    def wrapper(*args, **kwargs):
        reconnct_tries = 5
        for try_index in range(reconnct_tries):
            try:
                print(try_index, reconnct_tries)
                return func(*args, **kwargs)
            except:
                print(f"Unable to execute: {func.__name__}")
                time.sleep(1)

    return wrapper


engine = create_engine(
    f"postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_IP}/{DB_NAME}",
)
