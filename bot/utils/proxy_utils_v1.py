import os
import random
from better_proxy import Proxy
from pyrogram import Client
import json
import sys

from . import logger

PROXY_FILE_PATH = "sessions/do_not_commit.proxies.json"
def create_tg_client_proxy_pairs(tg_clients: list[Client]) -> list[tuple[Client, Proxy]]:
    """For each tg client fetches the corresponding proxy from do_not_commit.proxies.json
    
    Returns
    -------
    list[tuple[Client, Proxy]]
        List of tuples
        First element of a tuple - Pyrogram.Client
        Second element - better_proxy.Proxy
    """
    if not tg_clients:
        logger.error("Input argument 'tg_clients' is empty.")
        sys.exit()

    proxies = _load_proxies_from_file()
    result = []
    for tg in tg_clients:
        proxy = proxies.get(tg.name)
        if not proxy:
            logger.warning(f"Session {tg.name} does not have a matching proxy. Skipping it.")
            continue

        pair = (tg, proxy)
        result.append(pair)
    
    logger.info(f"Found {len(result)} sessions with proxies.")
    return result

def get_random_delay(left_hour: int = 1, right_hour: int = 10):
    """
        Get random delay between @left_hour and @right_hour that can be used with asyncio.sleep(delay)
        returns delay in seconds
    """

    if left_hour < 0:
        left_hour = 1
    if right_hour < 0:
        right_hour = 10

    delay = random.randint(8 * 3600, 11 * 3600)  # Random delay between 8 and 11 hours
    return delay

def get_hours_and_minutes(seconds: int) -> tuple[int, int]:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return (hours, minutes)

def _load_proxies_from_file() -> dict[str, Proxy]:
    if not os.path.exists(PROXY_FILE_PATH):
        logger.critical(f"File with proxies {PROXY_FILE_PATH} was not found. Stopping application...")
        sys.exit()

    proxies_json = None
    with open(file=PROXY_FILE_PATH, mode="r", encoding="utf-8-sig") as file:
        proxies_json = json.load(file)

    result = {}
    for session_name, proxy_str in proxies_json.items():
        result[session_name] = Proxy.from_str(proxy=proxy_str.strip())
    
    if not result:
        logger.error(f"File {PROXY_FILE_PATH} does not contain proxies.")
        sys.exit()

    return result