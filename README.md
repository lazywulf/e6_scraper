# e6_scrapper

## description
- An asynchronized web scrapper for e621.net.

## How to use
1. Edit the config.json file.
    - blacklist: a list with the tags you don't want to see
    - tags: a list of tags you are searching for
    - config: a dictionary of some searching configuration, please see e621 search cheat sheet for more.
    - auth:
        - auth: Enable/ disable login feature
          - login may override post per pages
        - user: your username
        - api_key: api key for your account
            - Go to Account->Manage API Access for the key
    - post per page: how many post in a page
    - pages: how many pages you want to access
        - along with post per page, it determines how many post the scrapper is going to download
        - the numbers may be slightly off because of the blacklist item
    - coroutine count: count of the coroutine executed at the same time.
        - I don't actually know if it's correct.
2. Go to main.py and execute.

## notes
It's a project for practice purposes. Don't expect too much.