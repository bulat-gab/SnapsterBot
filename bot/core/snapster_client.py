import asyncio
import aiohttp

from bot.utils import logger


class SnapsterClient:
    def __init__(self, session_name: str, user_id: int, http_client: aiohttp.ClientSession) -> None:
        self.session_name = session_name
        self.user_id = user_id
        self.http_client = http_client

    async def user_info(self):
        try:
            response = await self.http_client.get(
                url=f'https://prod.snapster.bot/api/user/getUserByTelegramId?telegramId={self.user_id}')
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting user info: {error}")
            await asyncio.sleep(delay=3)

    async def claim_mining(self):
        try:
            payload = {'telegramId': f'{self.user_id}'}
            response = await self.http_client.post(url='https://prod.snapster.bot/api/user/claimMiningBonus', json=payload)
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting user info: {error}")
            await asyncio.sleep(delay=3)

    async def get_quests(self):
        try:
            response = await self.http_client.get(
                url=f'https://prod.snapster.bot/api/quest/getQuests?telegramId={self.user_id}')
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting quests: {error}")
            await asyncio.sleep(delay=3)

    async def start_quest(self, quest_id: int):
        try:
            payload = {'telegramId': f'{self.user_id}', 'questId': quest_id}
            response = await self.http_client.post(url='https://prod.snapster.bot/api/quest/startQuest', json=payload)
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while starting quest: {error}")
            await asyncio.sleep(delay=3)

    async def claim_quest(self, quest_id: int):
        try:
            payload = {'telegramId': f'{self.user_id}', 'questId': quest_id}
            response = await self.http_client.post(url='https://prod.snapster.bot/api/quest/claimQuestBonus', json=payload)
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while claiming quest: {error}")
            await asyncio.sleep(delay=3)

    async def get_referral_points(self):
        try:
            response = await self.http_client.get(
                url=f'https://prod.snapster.bot/api/referral/calculateReferralPoints?telegramId={self.user_id}')
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting referral points: {error}")
            await asyncio.sleep(delay=3)

    async def claim_referrals(self):
        try:
            payload = {'telegramId': f'{self.user_id}'}
            response = await self.http_client.post(url='https://prod.snapster.bot/api/referral/claimReferralPoints',
                                              json=payload)
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while claiming referrals: {error}")
            await asyncio.sleep(delay=3)

    async def start_daily(self):
        try:
            payload = {'telegramId': f'{self.user_id}'}
            response = await self.http_client.post(url='https://prod.snapster.bot/api/dailyQuest/startDailyBonusQuest',
                                              json=payload)
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while starting daily bonus: {error}")
            await asyncio.sleep(delay=3)

    async def user_info(self):
        try:
            response = await self.http_client.get(
                url=f'https://prod.snapster.bot/api/user/getUserByTelegramId?telegramId={self.user_id}')
            response.raise_for_status()
            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting user info: {error}")
            await asyncio.sleep(delay=3)