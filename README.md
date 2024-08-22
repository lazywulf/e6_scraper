# e6_scrapper

## description
- An asynchronized web scrapper for e621.net.

## How to use
1. Run main.py straight ahead. Here's an example command:
```
python run.py -t cuddling -r safe -p 5 -d ./downloads
```
For any other flags, please see run.py.
    - blacklist: a list with the tags you don't want to see
    - tags: a list of tags you are searching for
        - with a config file, you may not do something like `-rating:e`, please use `run_with_searchbar.py`
    - config: a dictionary of some searching configuration, please see [e621 search cheat sheet](https://e621.net/help/cheatsheet) for more.
    - auth:
        - user: your username
        - api_key: api key for your account
            - login may override post per pages
            - Go to Account->Manage API Access for the key
    - post per page: how many post in a page
    - pages: how many pages you want to access
        - along with post per page, it determines how many post the scrapper is going to download
        - the numbers may be slightly off because of hidden items
    - chunk size
    - timeout: socket read timeout time

2. Set config.json and run run_by_file.py.

3. Use `Scrapper.run(<dict>)` if you have the argument dict.

## notes
It's a project for practice purposes. Don't expect too much.


