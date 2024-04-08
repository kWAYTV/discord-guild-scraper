import requests, random
from loguru import logger
from threading import Lock
from os import system, name
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor

class GuildScraper:
    def __init__(self):
        self.lock = Lock()
        self.tokens = []
        self.total_tokens, self.checked_tokens, self.total_guilds, self.threads = 0, 0, 0, 0

    # Clear console function
    def clear_console(self):
        system("cls" if name in ("nt", "dos") else "clear")

    # Set a proxy each request
    def set_proxy(self):
        with open("proxies.txt", "r", encoding="utf8", errors="ignore") as proxies_file:
            proxy_list = proxies_file.read().splitlines()
        proxy = random.choice(proxy_list)
        return {'http': f"http://{proxy}", 'https': f'http://{proxy}'}
    
    # Read tokens from file
    def load_tokens(self):
        with open("tokens.txt", "r", encoding="utf8", errors="ignore") as tokens_file:
            self.tokens = tokens_file.read().splitlines()
            self.total_tokens = len(self.tokens)

    # Process token with ThreadPoolExecutor
    def process_token(self, token):
        session = requests.Session()
        session.proxies = self.set_proxy()

        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }
        response = session.get("https://discord.com/api/v9/users/@me/guilds", headers=headers).json()

        with self.lock: 
            self.checked_tokens += 1

            if "message" in response:
                error = response["message"]
                if "401" in error:
                    logger.error(f"Invalid Token! ({token})")
                    # Save invalid token
                    with open("invalid.txt", "a", encoding="utf8", errors="ignore") as invalid_file:
                        invalid_file.write(f"{token}\n")
                else:
                    logger.error(f"Unknown Error {error} ({token})")
                    # Save unknown error token
                    with open("unknown.txt", "a", encoding="utf8", errors="ignore") as unknown_file:
                        unknown_file.write(f"{token}\n")
                return

            for guild in response:
                guild_id = guild["id"]
                with open("results.txt", "a", encoding="utf8", errors="ignore") as results_file:
                    results_file.write(f"{guild_id}\n")
                    self.total_guilds += 1
                    logger.info(f"Saved guild: {Style.DIM}{Fore.MAGENTA}{guild_id}{Style.RESET_ALL}")

            system(f"title Guild ID Scraper - {self.total_guilds} scraped - {self.checked_tokens}/{self.total_tokens} checked")

    def start(self):
        # Load tokens
        self.load_tokens()

        # Ask for threads
        self.threads = int(input(f"{Fore.GREEN}>{Fore.RESET} Threads: "))

        # Start ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.process_token, self.tokens)

        # Print results after all threads are done
        logger.info(f"Total guilds scraped: {self.total_guilds}")

if __name__ == "__main__":
    scraper = GuildScraper()
    scraper.start()
