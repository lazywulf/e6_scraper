import argparse
from scrapper import Scrapper

def main():

    parser = argparse.ArgumentParser(description="Your program description")

    parser.add_argument("-b", "--blacklist", nargs='*', default=[], help="Blacklist")
    parser.add_argument("-t", "--tags", nargs='*', default=[], help="Tags")
    parser.add_argument("-f", "--fav", default="", help="Favorite")
    parser.add_argument("-r", "--rating", default="", help="Rating")
    parser.add_argument("-o", "--order", default="", help="Order")
    parser.add_argument("-s", "--score", default="", help="Score")
    parser.add_argument("-a", "--auth", action='store_true', help="Auth")
    parser.add_argument("-u", "--user", default="", help="User")
    parser.add_argument("-k", "--api_key", default="", help="API Key")
    parser.add_argument("-ppp", "--post_per_page", type=int, default=200, help="Post per page")
    parser.add_argument("-p", "--pages", type=int, default=1, help="Pages")
    parser.add_argument("-d", "--download_dir", default="", help="Download directory")
    parser.add_argument("-c", "--coroutine_count", type=int, default=0, help="Coroutine count")

    args_dict = vars(parser.parse_args())

    config = {
        "blacklist": args_dict["blacklist"],
        "tags": args_dict["tags"],
        "config": {
            "fav": args_dict["fav"],
            "rating": args_dict["rating"],
            "order": args_dict["order"],
            "score": args_dict["score"]
        },
        "auth": {
            "auth": args_dict["auth"],
            "user": args_dict["user"],
            "api_key": args_dict["api_key"]
        },
        "post_per_page": args_dict["post_per_page"],
        "pages": args_dict["pages"],
        "download_dir": args_dict["download_dir"],
        "coroutine_count": args_dict["coroutine_count"]
    }

    Scrapper.run(config)


if __name__ == "__main__":
    main()
