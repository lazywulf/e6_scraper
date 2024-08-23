import os
from typing import Optional, Tuple
import logging
import json
import asyncio
from asyncio import Semaphore, gather, get_event_loop
import aiofiles
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrapper.log'),
        logging.StreamHandler()
    ]
)

class Scraper:
    def __init__(self, config: dict):
        self.header = {
            "User-Agent": "e621 scrapper 1.2 - by lazywulf"
        }
        self.semaphore: Semaphore = Semaphore(2)
        self.pics: list = []
        self.blacklist: list = config.get("blacklist", [])
        self.tags: list = config.get("tags", [])
        self.config: dict = {key: val for key, val in config.get("config", {}).items() if val}
        self.AUTH: Optional[dict] = config.get("auth", None)
        self.basic_auth: Optional[aiohttp.BasicAuth] = aiohttp.BasicAuth(
            self.AUTH.get("user", ""), 
            self.AUTH.get("api_key", "")
        ) if self.AUTH else None
        self.post_per_page: int = config.get("post_per_page", 50)
        self.pages: int = max(config.get("pages", 5), 1)
        self.directory: str = config.get("download_dir", "./downloads")
        self.CHUNKSIZE: int = max(config.get("CHUNKSIZE", 32), 1)
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout: int = config.get("timeout", None)

    async def _gen_post_list(self, page: int) -> list[dict]:
        picture_info = []
        b_list = []
        for item in self.blacklist:
            b_list.append("-" + item)
        temp = "+".join(self.tags) +\
                "+".join(b_list) +\
                ("+" if self.tags and self.config else "") +\
                "+".join(f"{key}%3A{val}" for key, val in self.config.items())
        url_path = f"https://e621.net/posts.json?page={page}&limit={self.post_per_page}&tags=" + temp

        async with self.semaphore:
            try:
                async with self.session.get(url_path) as resp:
                    if resp.status == 200:
                        try:
                            response_json = await resp.json()
                        except ValueError as e:
                            logging.error(f"Failed to decode JSON: {e}")
                            return picture_info

                        posts = response_json.get("posts", [])
                        for post in posts:
                            file_info = post.get("file", {})
                            if file_info.get("url"):
                                picture_info.append({
                                    "id": post.get("id"),
                                    "rating": post.get("rating"),
                                    "file": file_info.get("url"),
                                    "preview": post.get("preview", {}).get("url"),
                                    "ext": file_info.get("ext")
                                })
                        logging.info(f"Page {page} info fetched")
                    else:
                        logging.error(f"Failed to fetch posts on page {page}: HTTP {resp.status}")
            except aiohttp.ClientError as e:
                logging.error(f"HTTP request failed on page {page}: {e}")
            except TimeoutError:
                logging.error(f"Page {page} request timed out")
            except Exception as e:
                logging.error(f"Unexpected error occurred: {e}")
        return picture_info

    async def _get_one_pic(self, pic_info: dict[str, str]) -> None:
        pic_id = pic_info.get("id")
        file_url = pic_info.get("file")
        file_ext = pic_info.get("ext")
        
        if not all([pic_id, file_url, file_ext]):
            logging.error("Missing required information in pic_info: %s", pic_info)
            return
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            logging.info(f"Created directory {self.directory}")

        file_path = os.path.join(self.directory, f"{pic_id}.{file_ext}")
        
        try:
            async with self.session.get(file_url) as resp:
                if resp.status == 200:
                    bfile = await resp.read()
                else:
                    logging.error(f"Failed to download {file_url}: HTTP {resp.status}")
                    return 
                
            async with aiofiles.open(file_path, mode="wb") as output:
                await output.write(bfile)
                
            logging.info(f"Successfully downloaded {file_path}")
            
        except asyncio.TimeoutError:
            logging.error(f"TimeoutError: Post '{pic_id}.{file_ext}' fetch timed out.")
        except aiohttp.ClientError as e:
            logging.error(f"ClientError: Failed to fetch {file_url}. Error: {e}")
        except OSError as e:
            logging.error(f"OSError: Failed to write file {file_path}. Error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")

    async def _fetch(self) -> None:
        async def f(tasks):
            for info in await gather(*tasks):
                self.pics += info

        logging.info("Fetching static links...")
        if self.pages != 0:
            await f([self._gen_post_list(x) for x in range(1, self.pages + 1)])
        else:
            i, length = 0, 0
            while True:
                await f([self._gen_post_list(x + i) for x in range(1, 11)])
                i += 10
                print(i, length)
                print(len(self.pics))
                if length == len(self.pics):
                    break
                length = len(self.pics)
        logging.info(f"Static link fetching complete. Count: {len(self.pics)}")

    async def _download(self) -> None:
        """
        Did some test on this (200 pics/ 1800 pics)
        2 factors to consider:
            1. wrapping it into a task or pass the coroutine directly
            2. using for to await or use asyncio.gather.
        The results:
            in the 200 pics test, differences between each other(except passing directly/for... await) are neglectable.
            in the 1800 pics test, passing directly/ gather is the fastest.
            https://stackoverflow.com/questions/55761652/what-is-the-overhead-of-an-asyncio-task
        """
        length = len(self.pics)
        c_size = max(self.CHUNKSIZE, 1)

        logging.info("Downloading...")
        coroutines = [self._get_one_pic(info) for info in self.pics]
        for i in range(0, length, c_size):
            chunk = coroutines[i: i + c_size]
            await gather(*chunk)
        logging.info("Download complete.")

    @classmethod
    def run(cls, config: dict) -> None:
        scrapper = cls(config)
        loop = get_event_loop()
        scrapper.session = aiohttp.ClientSession(headers=scrapper.header, auth=scrapper.basic_auth,
                                                 timeout=aiohttp.ClientTimeout(sock_read=scrapper.timeout))
        try:
            loop.run_until_complete(scrapper._fetch())
            loop.run_until_complete(scrapper._download())
        except KeyboardInterrupt:
            logging.exception("Iterrupted")
        finally:
            loop.run_until_complete(scrapper.session.close())

    @classmethod
    def run_with_config(cls, config_file: str) -> None:
        with open(config_file, "r") as f:
            config = json.loads(f.read(), cls=json.JSONDecoder)
        cls.run(config)

    @classmethod
    def run_with_searchbar(cls, keyword: str, 
                           auth: Optional[Tuple[str, str]] = None,
                           page_count: int = 5,
                           post_per_page: int = 5,
                           download_dir: Optional[str] = None,
                           chunk_size: int =  32,
                           timeout: Optional[int] = None):
        tmp = keyword.split()
        config = {"tags": tmp}
        if auth:
            config["auth"] =  {"user": auth[0], "api_key": auth[1]}
        config["post_per_page"] = post_per_page
        config["pages"] = page_count
        if download_dir:
            config["download_dir"] = download_dir
        config["chunk_size"] = chunk_size
        config["timeout"] = timeout
        cls.run(config)
        
