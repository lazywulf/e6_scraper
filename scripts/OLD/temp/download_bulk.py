import aiohttp
import asyncio
import aiofiles

import csv

import os
import os.path as path
import time
import pathlib

import util

# https://e621.net/posts.json?tags=order%3Arandom+-type%3Agif+-type%3Aswf+-type%3Awebm+-type%3Amp4+-animated

url = ["/posts.json?tags=order%3Arandom+-type%3Agif+-type%3Aswf+-type%3Awebm+-type%3Amp4+-animated"]
lw_prof = aiohttp.BasicAuth("lazywulf", "tDHJc5Ftv92pc2m9euRX83Aa")
header = {
    "User-Agent": "TestProject/GetPics/b1.7 username:lazywulf"
}


def _path_finder(relative_path: str) -> str:
    project_dir = pathlib.Path(__file__).parents[1]
    return path.normpath(path.join(project_dir, relative_path))


async def gen_post_list():
    global url
    buffer = []

    async with aiohttp.ClientSession("https://e621.net", headers=header, auth=lw_prof) as session:
        for url in url:
            async with session.get(url) as resp:
                posts = dict(await resp.json())["posts"]
                for post in posts:
                    if post["file"]["url"] is not None:
                        buffer.append((post["id"], post["rating"], post["file"]["url"]))
    return buffer


async def download(post: tuple) -> None:
    bfile = b''
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(post[2]) as resp:
            bfile = await resp.content.read()
        async with aiofiles.open(_path_finder("downloads/{}.jpg".format(post[0])), "wb") as output:
            await output.write(bfile)


async def task():
    tasks = []
    for post in await gen_post_list():
        tasks.append(asyncio.create_task(download(post)))
    return asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(task())
