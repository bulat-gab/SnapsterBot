import random
from better_proxy import Proxy
from pyrogram import Client
import json
import sys

from . import logger

def __get_proxies() -> dict[str, Proxy]:
    proxies_json = None
    with open(file="do_not_commit.proxies.json", encoding="utf-8-sig") as file:
        proxies_json = json.load(file)

    result = {}
    for session_name, proxy_str in proxies_json.items():
        result[session_name] = Proxy.from_str(proxy=proxy_str.strip())
    
    return result

def get_proxies_with_clients(tg_clients: list[Client]) -> list[tuple[Client, Proxy]]:
    if not tg_clients:
        logger.error("Tg_clients not found.")
        sys.exit()

    proxies = __get_proxies()
    if not proxies:
        logger.error("Proxies not found.")
        sys.exit()

    result = []
    for tg in tg_clients:

        proxy = proxies.get(tg.name)
        if not proxy:
            logger.error(f"Proxy with name {tg.name} was not found.")
            sys.exit()

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