from telebot import TeleBot
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
import asyncio

# Настройки для Telethon
api_id = '28705623'
api_hash = '45f18a635a5ec41b4320ab258c3a8365'
phone = '+380674485616'
group_id = -4584764861  # Замени на ID твоей группы
bot_token = '7479387331:AAFfJKZAQFxZuZpkpNZvxVAHuepjY3HF_Fs'

# Создаем клиент Telethon и бота Telebot
client = TelegramClient('session_name', api_id, api_hash)
bot = TeleBot(bot_token)


async def get_messages_by_date(date_str):
    # Устанавливаем подключение к клиенту
    await client.start(phone)
    date = datetime.strptime(date_str, '%Y-%m-%d')
    offset_id = 0
    limit = 100
    all_messages = []

    while True:
        history = await client(GetHistoryRequest(
            peer=group_id,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        messages = [msg for msg in history.messages if msg.date.date() == date.date()]
        all_messages.extend(messages)

        offset_id = history.messages[-1].id

    # Записываем сообщения в файл
    with open(f'messages_{date_str}.txt', 'w', encoding='utf-8') as f:
        for msg in all_messages:
            sender = await msg.get_sender()
            f.write(f'{sender.first_name if sender else "Unknown"}: {msg.message}\n')

    await client.disconnect()
    return f"Сообщения за {date_str} сохранены в файл."

@bot.message_handler(commands=['get_messages'])
def handle_get_messages(message):
    try:
        date_str = message.text.split(maxsplit=1)[1]
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_messages_by_date(date_str))
        bot.reply_to(message, result)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажи дату в формате YYYY-MM-DD.")
    except ValueError:
        bot.reply_to(message, "Неверный формат даты. Используй YYYY-MM-DD.")


loop = asyncio.new_event_loop()
bot.polling()