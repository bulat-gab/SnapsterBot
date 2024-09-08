import asyncio
import sys
from urllib.parse import unquote, quote
import aiohttp
import html
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from random import randint

from bot.core.snapster_client import SnapsterClient
from .agents import generate_random_user_agent
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from bot.config import settings
from bot.utils import bulat_utils

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.url = "https://prod.snapster.bot/"
        self.snapster: SnapsterClient = None
        self.next_claim_dt = None

    def info(self, message):
        from bot.utils import info
        info(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def debug(self, message):
        from bot.utils import debug
        debug(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def warning(self, message):
        from bot.utils import warning
        warning(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def error(self, message):
        from bot.utils import error
        error(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def critical(self, message):
        from bot.utils import critical
        critical(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def success(self, message):
        from bot.utils import success
        success(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(scheme=proxy.protocol, hostname=proxy.host, port=proxy.port, username=proxy.login, password=proxy.password)
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict
    
        try:
            if not self.tg_client.is_connected:
                await self.tg_client.connect()
                async for message in self.tg_client.get_chat_history('snapster_bot'):
                    if message.text and message.text.startswith('/start'):
                        break
                    else:
                        ref_id = settings.REF_ID
                        await self.tg_client.send_message("snapster_bot", f"/start {ref_id}")
    
            while True:
                try:
                    peer = await self.tg_client.resolve_peer('snapster_bot')
                    break
                except FloodWait as fl:
                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fl.value}s")
                    await asyncio.sleep(fl.value + 3)
    
            web_view = await self.tg_client.invoke(RequestWebView(peer=peer, bot=peer, platform='android',from_bot_menu=False, url=self.url))

            auth_url = web_view.url
            tg_web_data = unquote(string=unquote(string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            self.user_id = (await self.tg_client.get_me()).id

            if not self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data
    
        except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
            raise InvalidSession(self.session_name)
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {html.escape(str(error))}")
            await asyncio.sleep(3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            escaped_error = str(error).replace('<', '&lt;').replace('>', '&gt;')
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {escaped_error}")

    async def auto_farm(self):
        try:
            claim = await self.snapster.claim_mining()
            if claim.get("result"):
                self.success(f"Claimed {claim.get('data').get('pointsClaimed')} points.")

            referrals = await self.snapster.get_referral_points()
            ref_points = referrals.get('data').get('pointsToClaim')
            if ref_points > 0:
                claim_ref = await self.snapster.claim_referrals()
                claimed_points = claim_ref.get('data').get('pointsClaimed')
                self.success(f"Claimed {claimed_points} referral points.")

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while claiming: {error}")
            await asyncio.sleep(delay=3)

    async def auto_tasks(self):
        try:
            quests = await self.snapster.get_quests()
            if not quests:
                self.info("Quests not found.")
                return

            for quest in quests.get('data'):
                if quest.get('type') == 'REFERRAL':
                    continue
                
                id = quest.get('id')
                title = quest.get('title')

                if quest.get('status') == 'EARN':
                    start = await self.snapster.start_quest(id)

                    if start.get('result'):
                        self.info(f"Task {title} started.")
                        await asyncio.sleep(delay=3)

                elif quest.get('status') == 'UNCLAIMED':
                    claim = await self.snapster.claim_quest(id)
                    if claim.get('result'):
                        self.success(f"Task {title} claimed.")
                        await asyncio.sleep(delay=3)

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while auto tasks: {error}")
            await asyncio.sleep(delay=3)
            
    async def run(self, proxy: str | None) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(f"{self.tg_client.name} | Run for <lw>{random_delay}s</lw>")

            await asyncio.sleep(delay=random_delay)

        while True:
            proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
            async with CloudflareScraper(headers=headers, connector=proxy_conn) as http_client:
                if proxy:
                    await self.check_proxy(http_client=http_client, proxy=proxy)
                
                tg_web_data = await self.get_tg_web_data(proxy=proxy)
                if not tg_web_data:
                    self.critical("Could not get tg_web_data")
                    sys.exit()
                http_client = self.__prepare_http_client(http_client, tg_web_data)
                self.snapster = SnapsterClient(self.session_name, self.user_id, http_client)


                try:
                    if settings.DAILY_BONUS:
                        try:
                            start_daily = await self.snapster.start_daily()
                            if start_daily.get('result') is True:
                                self.success(f"Daily bonus claimed!")

                        except Exception as error:
                            logger.error(f"{self.session_name} | Unknown error while daily bonus: {error}")
                            await asyncio.sleep(delay=3)

                    if settings.AUTO_FARM:
                        await self.auto_farm()

                    if settings.AUTO_TASKS:
                        await self.auto_tasks()

                    delay = bulat_utils.get_random_delay(settings.RANDOM_SLEEP_DELAY[0], settings.RANDOM_SLEEP_DELAY[1])
                    (h, min) = bulat_utils.get_hours_and_minutes(delay)
                    self.info(f"Sleep for {h} hours {min} minutes")
                    
                    await http_client.close()
                    if proxy_conn:
                        if not proxy_conn.closed:
                            proxy_conn.close()

                    await asyncio.sleep(delay=delay)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {html.escape(str(error))}")
                    await asyncio.sleep(3)

    def __prepare_http_client(self, http_client: CloudflareScraper, tg_web_data: str) -> CloudflareScraper:
        tg_web_data_parts = tg_web_data.split('&')
        query_id = tg_web_data_parts[0].split('=')[1]
        user_data = quote(tg_web_data_parts[1].split('=')[1])
        auth_date = tg_web_data_parts[2].split('=')[1]
        hash_value = tg_web_data_parts[3].split('=')[1]

        init_data = f"query_id={query_id}&user={user_data}&auth_date={auth_date}&hash={hash_value}"
        http_client.headers['Telegram-Data'] = init_data
        http_client.headers['User-Agent'] = generate_random_user_agent(device_type='android', browser_type='chrome')

        return http_client

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session!")