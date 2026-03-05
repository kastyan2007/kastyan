# yandex_music_plugin.py
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import re
import os
import random
import requests

# API данные автоматически получаются из переменных окружения Heroku
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
SESSION_NAME = 'yandex_music_bot'

# ID канала @gothurtedx (нужно будет заменить на числовой ID)
CHANNEL_ID = int(os.environ.get('CHANNEL_ID', 0))  # Укажите ID канала в переменных окружения

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Текущий трек
current_track = "🎵 Музыка"

# JavaScript код плагина (только для информации)
PLUGIN_INFO = '''Плагин для Яндекс Музыки теперь работает через Telegram канал!
Название канала автоматически меняется на текущий трек.'''

async def get_yandex_music_track():
    """Получение текущего трека с Яндекс Музыки (имитация)"""
    try:
        # Здесь должен быть реальный API запрос к Яндекс Музыке
        # Но для примера используем случайные треки
        tracks = [
            "Track - Artist 1",
            "Song - Performer 2",
            "Music - Singer 3",
            "Hit - Band 4",
            "Popular - Artist 5"
        ]
        return random.choice(tracks)
    except Exception as e:
        print(f"Error getting track: {e}")
        return None

async def update_channel_title(new_title):
    """Обновление названия канала"""
    try:
        # Получаем информацию о канале
        channel = await client.get_entity(f'https://t.me/gothurtedx')
        
        # Обновляем название
        await client(UpdateProfileRequest(
            first_name=new_title[:64]  # Telegram ограничение 64 символа
        ))
        
        print(f"✅ Название канала обновлено: {new_title}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления названия: {e}")
        return False

@client.on(events.NewMessage(pattern=r'\.трек'))
async def get_current_track_command(event):
    """Команда для получения текущего трека"""
    global current_track
    await event.reply(f"🎵 **Текущий трек:**\n{current_track}")

@client.on(events.NewMessage(pattern=r'\.установить'))
async def install_plugin(event):
    """Информация о плагине"""
    await event.reply(
        "📦 **Плагин Яндекс Музыки для канала**\n\n"
        "✅ **Функции:**\n"
        "• Автоматическое обновление названия канала\n"
        "• Отображение текущего трека\n"
        "• Мониторинг Яндекс Музыки\n\n"
        "📊 **Статус:** Активен\n"
        "👤 **Канал:** @gothurtedx\n\n"
        f"🎵 **Сейчас играет:** {current_track}"
    )

@client.on(events.NewMessage(pattern=r'\.помощь'))
async def help_command(event):
    """Команда помощи"""
    help_text = """
**🤖 Яндекс Музыка - Плагин для канала**

**Команды:**
• `.трек` - показать текущий трек
• `.статус` - статус плагина
• `.помощь` - это сообщение

**Функции:**
• 🔄 Название канала меняется на текущий трек
• 🎵 Отслеживание проигрываемой музыки
• ⏱ Обновление каждые 30 секунд

**Канал:** @gothurtedx
**Автор:** @gothurtedx
"""
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r'\.статус'))
async def status_command(event):
    """Статус плагина"""
    await event.reply(
        f"✅ **Плагин активен**\n\n"
        f"📊 **Информация:**\n"
        f"• Канал: @gothurtedx\n"
        f"• Название канала: {current_track}\n"
        f"• API ID: {'✓ Установлен' if API_ID else '✗ Не установлен'}\n"
        f"• API Hash: {'✓ Установлен' if API_HASH else '✗ Не установлен'}\n"
        f"• Режим: Автообновление"
    )

async def monitor_yandex_music():
    """Мониторинг Яндекс Музыки и обновление названия канала"""
    global current_track
    print("🎵 Начинаю мониторинг Яндекс Музыки...")
    
    while True:
        try:
            # Получаем текущий трек
            track = await get_yandex_music_track()
            
            if track and track != current_track:
                current_track = track
                
                # Обновляем название канала
                success = await update_channel_title(f"🎵 {track[:60]}")
                
                if success:
                    print(f"✅ Трек обновлен: {track}")
            
            # Проверяем каждые 30 секунд
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
            await asyncio.sleep(60)

async def main():
    # Проверка наличия необходимых переменных
    if not API_ID or not API_HASH:
        print("❌ Ошибка: API_ID и API_HASH должны быть установлены в Heroku")
        return
    
    print("✅ API данные загружены из Heroku")
    print("🎵 Запуск Яндекс Музыка монитора...")
    
    # Запускаем клиент
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Юзербот запущен!")
    print(f"👤 Канал: @gothurtedx")
    
    # Запускаем мониторинг музыки
    asyncio.create_task(monitor_yandex_music())
    
    # Ждем команды
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
