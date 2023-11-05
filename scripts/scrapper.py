import asyncio
import aiofiles
import aiohttp

import json

from time import time as t

pics = []


class Scrapper:
    def __init__(self, config_path):
        with open(config_path, "r") as config:
            attr = json.loads(config.read(), cls=json.JSONDecoder)
        self.header = {
            "User-Agent": "e621 scrapper 1.0 - by lazywulf"
        }
        self.semaphore = asyncio.Semaphore(2)

        self.blacklist = attr["blacklist"]
        self.tags = attr["tags"]
        self.config = {}
        for key, val in attr["config"].items():
            if val != "":
                self.config[key] = val
        self.AUTH = attr["auth"]["auth"]
        self.basic_auth = aiohttp.BasicAuth(attr["auth"]["user"], attr["auth"]["api_key"])
        self.post_per_page = attr["post_per_page"]
        self.pages = attr["pages"] if attr["pages"] > 0 else 0
        self.directory = attr["download_dir"]
        self.COROUTINE_COUNT = attr["coroutine_count"] if attr["coroutine_count"] > 0 else 0

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
            raise e

    async def fetch(self):
        async def f(tasks):
            global pics
            for info in await asyncio.gather(*tasks):
                pics += info

        global pics
        if self.pages != 0:
            await f([asyncio.create_task(self.gen_post_list(x)) for x in range(1, self.pages + 1)])
        else:
            i, length = 0, 0
            while True:
                await f([asyncio.create_task(self.gen_post_list(x + i)) for x in range(1, 11)])
                i += 10
                print(i, length)
                print(len(pics))
                if length == len(pics):
                    break
                length = len(pics)


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
        global pics
        length = len(pics)
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))

        coroutines = [self.get_one_pic(info, session) for info in pics]
        if self.COROUTINE_COUNT != 0:
            for i in range(int(length / self.COROUTINE_COUNT) + 1):
                chunk = coroutines[i * self.COROUTINE_COUNT: (i + 1) * self.COROUTINE_COUNT]
                await asyncio.gather(*chunk)
        else:
            await asyncio.gather(*coroutines)
        await session.close()

    @classmethod
    def run(cls, config_path):
        scrapper = cls(config_path)
        loop = asyncio.get_event_loop()
        print("fetching...")
        loop.run_until_complete(scrapper.fetch())
        print("done", "file count: ", len(pics))
        s = t()
        loop.run_until_complete(scrapper.download())
        print(t() - s)

