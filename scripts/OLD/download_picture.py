import bs4
import requests as rq
import requests.auth as rqa
from bs4 import BeautifulSoup as bs

import time
import threading

import os.path as path
import pathlib

import util

# url = ["https://e621.net/posts?tags=order%3Arandom+-type%3Agif+-type%3Aswf+-type%3Awebm+-type%3Amp4+-animated+vore+score:>250" for x in range(10)]
url = ["https://e621.net/posts?tags=order%3Arandom+-type%3Agif+-type%3Aswf+-type%3Awebm+-type%3Amp4+-animated"]
header = {
    "User-Agent": "TestProject/GetPics/1.0 username:lazywulf",
}
auth = rqa.HTTPBasicAuth("lazywulf", "tDHJc5Ftv92pc2m9euRX83Aa")
path = "dsfaf" if __name__ == "__main__" else "fdhsoafd"

def check_response(response: rq.Response) -> None:
    local_time = time.ctime(time.time())
    with open(_path_finder("data/responses.txt"), mode="a") as r_file:
        r_file.write("{} {}\n".format(local_time, response))
        print(local_time, response)


def _path_finder(relative_path: str) -> str:
    project_dir = pathlib.Path(__file__).parents[1]
    return path.normpath(path.join(project_dir, relative_path))


def download(soup: bs4.BeautifulSoup) -> None:
    def get_one_pic(tag):
        with open(_path_finder("downloads/{}.{}".format(tag.attrs["id"], tag.attrs["data-file-ext"])),
                  mode="wb") as output:
            pic_url = tag.attrs["data-file-url"]
            output.write(rq.get(pic_url).content)
    thread = [threading.Thread(target=get_one_pic, args=[x]) for x in soup.find_all("article")]
    for t in thread:
        t.start()


if __name__ == "__main__":
    util.clear_dir("downloads")
    rq.get("https://e621.net/users/lazywulf.json?login=lazywulf&api_key=tDHJc5Ftv92pc2m9euRX83Aa")
    for url in url:
        r = rq.get(url, headers=header, auth=auth)
        check_response(r)
        soup = bs(r.content, "html.parser")
        download(soup)
