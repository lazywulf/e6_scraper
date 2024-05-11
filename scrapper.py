import asyncio
import aiofiles
import aiohttp

import json

from time import time as t


class Scrapper:
    def __init__(self, config):
        self.header = {
            "User-Agent": "e621 scrapper 1.1 - by lazywulf"
        }
        self.semaphore = asyncio.Semaphore(2)
        self.pics = []
        self.blacklist = config["blacklist"]
        self.tags = config["tags"]
        self.config = {}
        for key, val in config["config"].items():
            if val != "":
                self.config[key] = val
        self.AUTH = config["auth"]["auth"]
        self.basic_auth = aiohttp.BasicAuth(config["auth"]["user"], config["auth"]["api_key"])
        self.post_per_page = config["post_per_page"]
        self.pages = config["pages"] if config["pages"] > 0 else 0
        self.directory = config["download_dir"]
        self.COROUTINE_COUNT = config["coroutine_count"] if config["coroutine_count"] > 0 else 0


    async def gen_post_list(self, pages) -> list[dict]:
        picture_info = []
        # remember the bracket, without that bracket, the order is completely wrong.
        for item in self.blacklist:
            self.tags.append("-" + item)
        temp = "+".join(self.tags) +\
               ("+" if self.tags and self.config else "") +\
               "+".join(f"{key}%3A{val}" for key, val in self.config.items())
        url_path = f"/posts.json?page={pages}&limit={self.post_per_page}&tags=" + temp

        async with self.semaphore:
            async with aiohttp.ClientSession(
                    "https://e621.net",
                    headers=self.header,
                    auth=self.basic_auth if self.AUTH else None) as session:
                async with session.get(url_path) as resp:
                    posts = dict(await resp.json())["posts"]
                    for post in posts:
                        if post["file"]["url"] is not None:
                            picture_info.append({
                                "id": post["id"],
                                "rating": post["rating"],
                                "file": post["file"]["url"],
                                "preview": post["preview"]["url"],
                                "ext": post["file"]["ext"]})
        return picture_info

    async def get_one_pic(self, pic_info: dict[str, str], session: aiohttp.ClientSession):
        # "session" can be pass into a func.
        try:
            async with session.get(pic_info["file"]) as resp:
                bfile = await resp.read()
            async with aiofiles.open(
                    "{}\\{}.{}".format(self.directory, pic_info["id"], pic_info["ext"]),
                    mode="wb") as output:
                await output.write(bfile)
        except asyncio.exceptions.TimeoutError as e:
            print(f"TimeoutError: post '{pic_info['id']}.{pic_info['ext']}' fetch timeout.")

    async def fetch(self):
        async def f(tasks):
            for info in await asyncio.gather(*tasks):
                self.pics += info

        if self.pages != 0:
            await f([asyncio.create_task(self.gen_post_list(x)) for x in range(1, self.pages + 1)])
        else:
            i, length = 0, 0
            while True:
                await f([asyncio.create_task(self.gen_post_list(x + i)) for x in range(1, 11)])
                i += 10
                print(i, length)
                print(len(self.pics))
                if length == len(self.pics):
                    break
                length = len(self.pics)


    async def download(self) -> None:
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
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))

        coroutines = [self.get_one_pic(info, session) for info in self.pics]
        if self.COROUTINE_COUNT != 0:
            for i in range(int(length / self.COROUTINE_COUNT) + 1):
                chunk = coroutines[i * self.COROUTINE_COUNT: (i + 1) * self.COROUTINE_COUNT]
                await asyncio.gather(*chunk)
        else:
            await asyncio.gather(*coroutines)
        await session.close()

    @classmethod
    def run(cls, config):
        scrapper = cls(config)
        loop = asyncio.get_event_loop()
        print("fetching...")
        loop.run_until_complete(scrapper.fetch())
        print("done", "file count: ", len(scrapper.pics))
        s = t()
        loop.run_until_complete(scrapper.download())
        print(t() - s)
        del scrapper

    @classmethod
    def run_by_file(cls, config_file):
        with open(config_file, "r") as f:
            config = json.loads(f.read(), cls=json.JSONDecoder)
        scrapper = cls(config)
        loop = asyncio.get_event_loop()
        print("fetching...")
        loop.run_until_complete(scrapper.fetch())
        print("done", "file count: ", len(scrapper.pics))
        s = t()
        loop.run_until_complete(scrapper.download())
        print(t() - s)
        del scrapper

