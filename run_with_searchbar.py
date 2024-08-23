from scraper import Scraper
import argparse

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-k', '--keyword', type=str, help='The keyword to search for')
    parser.add_argument('-a', '--auth', nargs=2, default=None, type=str, help='Optional authentication credentials')
    parser.add_argument('-p', '--page_count', type=int, default=5, help='Number of pages to scrape')
    parser.add_argument('-pp', '--post_per_page', type=int, default=5, help='Number of posts per page')
    parser.add_argument('-d', '--download_dir', type=str, default=None, help='Directory to save downloaded files')
    parser.add_argument('-c', '--chunk_size', type=int, default=32, help='Chunk size for downloading files')
    parser.add_argument('-t', '--timeout', type=int, default=None, help='Timeout for each request')

    args = parser.parse_args()

    
    Scraper.run_with_searchbar(args.keyword, 
                                args.auth,
                                args.page_count,
                                args.post_per_page,
                                args.download_dir,
                                args.chunk_size,
                                args.timeout)
    

if __name__ == '__main__':
    main()
