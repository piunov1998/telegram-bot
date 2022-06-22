import asyncio
import json
import logging
import os
import sys

import aiohttp

from robot import Bot

logging.basicConfig()

token = os.getenv('TOKEN')
base_url = f'https://api.telegram.org'
auth = f'/bot{token}'

sessions: dict[str | int, Bot] = {}


def setup_logger():
    logg = logging.getLogger(__name__)
    logg.setLevel(logging.DEBUG)
    logg.info('Logger started')
    return logg


def keyboard(chat_id) -> dict:
    if sessions[chat_id].state == 'guess':
        return {
            'keyboard': [
                [
                    {
                        'text': '1'
                    },
                    {
                        'text': '2'
                    },
                    {
                        'text': '3'
                    },
                    {
                        'text': '4'
                    },
                    {
                        'text': '5'
                    }
                ]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
    else:
        return {}


def message_handler(msg: str, chat_id) -> dict:
    logger.debug(f'Принято сообщение -> {chat_id} | {msg}')
    bot = sessions.get(chat_id)
    if bot is None:
        bot = Bot()
        sessions[chat_id] = bot

    body = {
        'chat_id': chat_id,
        'text': bot.chat(msg),
    }

    kb = keyboard(chat_id)
    if kb:
        body['reply_markup'] = kb

    return body


async def get_updates(
        session: aiohttp.ClientSession,
        offset: int = 0,
        timeout: int = 15
) -> dict:
    async with session.get(
            f'{auth}/getUpdates?offset={offset}&timeout={timeout}') as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            logger.error(
                'Error during getting updates',
                extra={'code': resp.status, 'resp': await resp.json()}
            )


async def send_message(
        session: aiohttp.ClientSession, body: dict):
    async with session.post(
            f'{auth}/sendMessage',
            data=json.dumps(body).encode('utf-8')
    ) as resp:
        if not 200 <= resp.status < 300:
            e = await resp.json()
            logger.error(
                f'Error during messaging -> {e}',
                extra={'code': resp.status, 'resp': e}
            )
        else:
            logger.debug(
                f'Сообщение отправлено -> {body["chat_id"]} | {body["text"]}',
                extra=body
            )


async def main():
    offset = 0
    async with aiohttp.ClientSession(
            base_url=base_url,
            headers={'Content-Type': 'application/json'}
    ) as session:
        while running:
            updates = await asyncio.wait_for(
                get_updates(session, offset=offset),
                timeout=5
            )
            if updates is None:
                continue
            else:
                for update in updates['result']:
                    last_upd = update['update_id']
                    if last_upd > offset:
                        offset = last_upd
                        try:
                            body = message_handler(
                                msg=update['message']['text'],
                                chat_id=update['message']['chat']['id']
                            )
                            await send_message(session=session, body=body)
                        except KeyError:
                            logger.warning('Неподдерживаемый тип сообщения')


if __name__ == '__main__':
    logger = setup_logger()
    try:
        running = True
        asyncio.run(main())
    except KeyboardInterrupt:
        running = False
        sys.exit(0)
