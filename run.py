import argparse
from scrapper import Scrapper

def main():
    def remove_none(d):
        if isinstance(d, dict):
            return {k: remove_none(v) for k, v in d.items() if v is not None}
        return d
    
    parser = argparse.ArgumentParser(description="e621.net scrapper")

    parser.add_argument("-b", "--blacklist", nargs='*', default=None, help="Blacklist")
    parser.add_argument("-t", "--tags", nargs='*', default=None, help="Tags")
    parser.add_argument("-f", "--fav", default=None, help="Favorite")
    parser.add_argument("-r", "--rating", default=None, help="Rating")
    parser.add_argument("-o", "--order", default=None, help="Order")
    parser.add_argument("-s", "--score", default=None, help="Score")
    parser.add_argument("-u", "--user", default=None, help="User")
    parser.add_argument("-k", "--api_key", default=None, help="API Key")
    parser.add_argument("-d", "--download_dir", default=None, help="Download directory")
    parser.add_argument("-pp", "--post_per_page", type=int, default=50, help="Post per page")
    parser.add_argument("-p", "--pages", type=int, default=1, help="Pages")
    parser.add_argument("-c", "--chunk_size", type=int, default=1, help="chunk size")
    parser.add_argument('-to', '--timeout', type=int, default=20, help='Timeout for each request')

    args = vars(parser.parse_args())
    config = {
        "blacklist": args["blacklist"],
        "tags": args["tags"],
        "config": {
            "fav": args["fav"],
            "rating": args["rating"],
            "order": args["order"],
            "score": args["score"]
        },
        "auth": {
            "user": args["user"],
            "api_key": args["api_key"]
        },
        "post_per_page": args["post_per_page"],
        "pages": args["pages"],
        "download_dir": args["download_dir"],
        "chunk_size": args["chunk_size"]
    }
    config = remove_none(config)

    Scrapper.run(config)


if __name__ == "__main__":
    main()
