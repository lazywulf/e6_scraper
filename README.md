# e6_scraper

## description
- An asynchronized web scraper for [e621.net](https://e621.net/).
    - This site runs off of the Ouroboros platform, a danbooru-style software specifically designed for the site.
    - So it can support other similiar site with little modification.
        - I'll do it in the future. (Maybe)
- Supports batch commands.

## How to use
### `run.py`
Example command:
```
python run.py -t cuddling romantic -r safe -o random -s ">450" -p 5 -d ./downloads
```
> Avalible flags listed below.
1. `-b`, `--blacklist`: a list with the tags you don't want to see
2. `-t`, `--tags`: a list of tags you are searching for
    - with a config file, you may not do something like `-rating:e`, please use `run_with_searchbar.py`
3. `-f`, `--fav`: favorite list of a user
4. `-r`, `--rating`: rating tag
5. `-o`, `--order`: the order of the posts
    - All downloads will start from page 1
6. `-s`, `--score`: score of the post
7. `-a`, `--auth`: takes two args
    1. your username
    2. api key for your account
>
    Login may override post per pages.
    Go to Account->Manage API Access for the key

8. `-d`, `--download_dir`: the directory the downloaded files should be
8. `-pp`, `--post_per_page`: how many post in a page
9. `-p`, `--pages`: how many pages you want to access
>
    Along with post per page, it determines how many post the scrapper is going to download.
    The numbers may be slightly off because of hidden items.
10. `-c`, `--chunk_size`: self explanatory
11. `-to`, `--timeout`: socket read timeout time

### `run_with_config.py`
Example command:
```
python run_with_config.py
```
Set a configuration file.
For more options in "config", please see [e621 search cheat sheet](https://e621.net/help/cheatsheet).

### `run_with_searchbar.py`
Example command:
```
python run_with_searchbar.py -k "cuddling -kissing -rating:e" -p 10 -pp 20 -d "./downloads"
```
1. `-k`, `--keyword`: what you type in the searchbar on the site
2. `-a`, `--auth`: takes two args
    1. your username
    2. api key for your account
3. `-d`, `--download_dir`: the directory the downloaded files should be
4. `-pp`, `--post_per_page`: how many post in a page
5. `-p`, `--pages`: how many pages you want to access
6. `-c`, `--chunk_size`: self explanatory
7. `-to`, `--timeout`: socket read timeout time

> All methods can be found in the `Scrapper` class, you can call them directly if needed.


