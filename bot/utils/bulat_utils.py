from better_proxy import Proxy
from pyrogram import Client
import json
import sys

from . import logger


def get_proxies_with_clients(tg_clients: list[Client]) -> list[tuple[Client, Proxy]]:
    if not tg_clients:
        logger.error("Tg_clients not found.")
        sys.exit()

    proxies = __get_proxies()
    if not proxies:
        logger.error("Proxies not found.")
        sys.exit()
    if len(proxies) != len(tg_clients):
        logger.error(f"Number of proxies and sessions do not match. Found '{len(proxies)}' proxies and '{len(tg_clients)}' sessions")
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

def __get_proxies() -> dict[str, Proxy]:
    proxies_json = None
    with open(file="do_not_commit.proxies.json", encoding="utf-8-sig") as file:
        proxies_json = json.load(file)

    result = {}
    for session_name, proxy_str in proxies_json.items():
        result[session_name] = Proxy.from_str(proxy=proxy_str.strip())
    
    return result