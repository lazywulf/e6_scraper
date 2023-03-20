import asyncio
import aiofiles
import aiohttp

from time import time as t
from util import *

# variables that should not be modified
header = {
    "User-Agent": "e621 scrapper 1.0 - by lazywulf"
}
semaphore = asyncio.Semaphore(2)
pics = []

blacklist = []

tags = []
config = {"fav": "lazywulf"}
AUTH = True
basic_auth = aiohttp.BasicAuth("lazywulf", "tDHJc5Ftv92pc2m9euRX83Aa")
post_per_page = 200
directory = "downloads"

ITER_COUNT = 1


async def gen_post_list(pages) -> list[dict]:
    picture_info = []
    # remember the bracket, without that bracket, the order is completely wrong.
    temp = "+".join(tags) + ("+" if tags and config else "") + "+".join(f"{key}%3A{val}" for key, val in config.items())
    url_path = f"/posts.json?page={pages}&limit={post_per_page}&tags=" + temp

    async with semaphore:
        async with aiohttp.ClientSession(
                "https://e621.net",
                headers=header,
                auth=basic_auth if AUTH else None) as session:
            async with session.get(url_path + "+-".join(blacklist)) as resp:
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


async def get_one_pic(pic_info: dict[str, str], session: aiohttp.ClientSession):
    bfile = ""
    # "session" can be pass into a func.
    try:
        async with session.get(pic_info["file"]) as resp:
            bfile = await resp.read()
        async with aiofiles.open(
                path_finder("{}/{}.{}".format(directory, pic_info["id"], pic_info["ext"])), mode="wb+") as output:
            await output.write(bfile)
    except asyncio.exceptions.TimeoutError as e:
        raise e


# things to modify
async def fetch():
    global pics
    tasks = [asyncio.create_task(gen_post_list(x)) for x in range(1, 10)]
    for info in await asyncio.gather(*tasks):
        pics += info


# download funcs.
async def download() -> None:
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

    coroutines = [get_one_pic(info, session) for info in pics]
    if ITER_COUNT > 1:
        batch_size = int(length / (ITER_COUNT - 1))
        for i in range(ITER_COUNT - 1):
            chunk = coroutines[i * batch_size: (i + 1) * batch_size]
            await asyncio.gather(*chunk)
    else:
        await asyncio.gather(*coroutines)
    await session.close()


if __name__ == "__main__":
    clear_dir("downloads")

    loop = asyncio.get_event_loop()
    print("fetching")
    loop.run_until_complete(fetch())
    print("done", len(pics))
    s = t()
    loop.run_until_complete(download())
    print(t() - s)

