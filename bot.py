from hikkatl.types import Message
from telethon.tl.types import KeyboardButtonCallback
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from .. import loader, utils
import asyncio

@loader.tds
class AutoFarmMod(loader.Module):
    """Auto Farm Bot for Hamster Kombat"""
    strings = {"name": "AutoFarm", "started": "Auto farm started!", "stopped": "Auto farm stopped!"}

    def __init__(self):
        self._running = False

    async def client_ready(self, client, db):
        self._client = client

    @loader.command
    async def startfarm(self, message: Message):
        """Start auto-farming"""
        self._running = True
        await utils.answer(message, self.strings("started", message))
        while self._running:
            await self._farm(message)
            await asyncio.sleep(10)  # Интервал между действиями (в секундах)

    @loader.command
    async def stopfarm(self, message: Message):
        """Stop auto-farming"""
        self._running = False
        await utils.answer(message, self.strings("stopped", message))

    async def _farm(self, message: Message):
        try:
            # Отправляем команду для запуска игры
            await self._client.send_message('@hamster_kombat_bot', '/start')

            # Ждем сообщения с кнопками
            async for msg in self._client.iter_messages('@hamster_kombat_bot', limit=10):
                if msg.buttons:
                    for row in msg.buttons:
                        for button in row:
                            if isinstance(button, KeyboardButtonCallback):
                                try:
                                    # Нажимаем кнопку "Играть в 1 клик 🐹"
                                    if 'Играть в 1 клик 🐹' in button.text:
                                        await self._client(GetBotCallbackAnswerRequest(
                                            peer=msg.peer_id,
                                            msg_id=msg.id,
                                            data=button.data
                                        ))
                                        await utils.answer(message, f"Clicked: {button.text}")
                                        return
                                except Exception as e:
                                    await utils.answer(message, f"Failed to click button: {e}")
                                    return
        except Exception as e:
            await utils.answer(message, f"Failed to start game or farm: {e}")
