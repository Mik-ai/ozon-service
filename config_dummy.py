from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
import time
import asyncio


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


def batch_lengh_generator(step: int, data: list):
    return (data[x : x + step] for x in range(0, len(data), step))


def equal_split(list_to_split, n_parts):
    k, m = divmod(len(list_to_split), n_parts)
    return (
        list_to_split[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(n_parts)
    )


def do_retry_on_fail_async(func):
    async def wrapper(*args, **kwargs):
        reconnct_tries = 5
        for try_index in range(reconnct_tries):
            try:
                print(try_index, reconnct_tries)
                return await func(*args, **kwargs)
            except:
                print(f"Unable to execute: {func.__name__}")
                await asyncio.sleep(1)

    return wrapper


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

engine_async = create_async_engine(
    f"postgresql+asyncpg://{DB_LOGIN}:{DB_PASSWORD}@{DB_IP}/{DB_NAME}",
)
