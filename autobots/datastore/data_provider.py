from typing import Callable, AsyncGenerator

from autobots.conn.tiktoken.tiktoken import get_tiktoken


class DataProvider:

    def __init__(self):
        pass

    @staticmethod
    async def read_file_line_by_line(filename: str) -> AsyncGenerator[str, None]:
        with open(filename, 'r', encoding='UTF-8') as file:
            while line := file.readline():
                yield line

    @staticmethod
    async def create_file_chunks(
            filename: str,
            chunk_func: Callable[[str], AsyncGenerator[str, None]],
            chunk_token_size: int = 512
    ) -> AsyncGenerator[str, None]:
        chunk = ""
        count = 0
        # iter over chunks
        async for part in chunk_func(filename):
            if count >= chunk_token_size:
                yield chunk
                chunk = ""
                count = 0

            # count tokens
            token_count = get_tiktoken().token_count(part)
            count = count + token_count

            chunk = chunk + part

        # yield last chunk
        yield chunk





