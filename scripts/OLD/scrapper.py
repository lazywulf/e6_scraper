import threading
import asyncio

import aiohttp
import requests as rq

from util import *

header = {
    "User-Agent": "TestProject/GetPics/b1.9 username:lazywulf"
}
basic_auth = aiohttp.BasicAuth("lazywulf", "tDHJc5Ftv92pc2m9euRX83Aa")
blacklist = []
pics = []

THREAD_COUNT = 17


async def gen_post_list(*tags, auth=False, **config) -> list[dict]:
    picture_info = []
    # remember the bracket, without that bracket, the order is completely wrong.
    temp = "+".join(tags) + ("+" if tags and config else "") + "+".join(f"{key}%3A{val}" for key, val in config.items())
    url_path = "/posts.json?tags=" + temp

    async with aiohttp.ClientSession(
            "https://e621.net",
            headers=header,
            auth=basic_auth if auth else None) as session:
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


def get_one_pic(pic_info: dict[str, str]):
    with open(path_finder("downloads/{}.{}".format(pic_info["id"], pic_info["ext"])), mode="wb") as output:
        output.write(rq.get(pic_info["file"]).content)


# things to modify
async def fetch():
    global pics
    tasks = [asyncio.create_task(gen_post_list()) for _ in range(10)]
    return await asyncio.gather(*tasks)


def download() -> None:
    def task(*args):
        for x in args:
            get_one_pic(x)

    global pics
    length = len(pics)
    batch_size = int(length / THREAD_COUNT)
    batch_index = [i for i in range(0, length, batch_size)]
    batch_index[-1] = length - 1
    thread = []

    for i in range(THREAD_COUNT):
        thread.append(threading.Thread(target=task, args=pics[batch_index[i]: batch_index[i + 1]]))
    for t in thread:
        t.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for future_result in loop.run_until_complete(fetch()):
        pics += future_result
    # download()
