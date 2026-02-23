# yandex_music_plugin.py
import asyncio
from telethon import TelegramClient, events
import re
import os

# Конфигурация
API_ID = os.environ.get('API_ID', 'YOUR_API_ID')
API_HASH = os.environ.get('API_HASH', 'YOUR_API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')

client = TelegramClient('userbot', API_ID, API_HASH)

# JavaScript код плагина
PLUGIN_CODE = '''// ==UserScript==
// @name         Яндекс Музыка Трекер с @gothurtedx
// @namespace    https://t.me/gothurtedx
// @version      1.4
// @description  Показывает текущий трек в Яндекс.Музыке и прикрепляет канал @gothurtedx
// @author       gothurtedx
// @match        https://music.yandex.ru/*
// @match        https://music.yandex.by/*
// @match        https://music.yandex.kz/*
// @match        https://music.yandex.ua/*
// @grant        none
// @run-at       document-end
// @icon         https://music.yandex.ru/favicon.ico
// ==/UserScript==

(function() {
    "use strict";
    
    const CHANNEL_USERNAME = "gothurtedx";
    const CHANNEL_URL = "https://t.me/" + CHANNEL_USERNAME;
    
    // Функция для создания и добавления стилей
    function injectStyles() {
        const style = document.createElement("style");
        style.textContent = `
            .gothurtedx-channel-badge {
                display: inline-flex !important;
                align-items: center !important;
                margin-left: 8px !important;
                padding: 4px 12px !important;
                background: linear-gradient(135deg, #0088cc, #00a0e9) !important;
                color: white !important;
                text-decoration: none !important;
                border-radius: 30px !important;
                font-size: 12px !important;
                font-weight: 500 !important;
                transition: 0.2s !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                cursor: pointer !important;
                z-index: 9999 !important;
            }
            
            .gothurtedx-channel-badge:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(0,136,204,0.4) !important;
            }
            
            .gothurtedx-now-playing {
                position: fixed !important;
                bottom: 15px !important;
                right: 15px !important;
                background: linear-gradient(135deg, #1E1E2A, #2A2A3A) !important;
                color: #FFDB4D !important;
                padding: 10px 18px !important;
                border-radius: 40px !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                font-size: 13px !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
                z-index: 999998 !important;
                border: 2px solid #FFDB4D !important;
                cursor: pointer !important;
                transition: 0.3s !important;
                max-width: 280px !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                backdrop-filter: blur(5px) !important;
            }
            
            .gothurtedx-now-playing:hover {
                transform: scale(1.02) !important;
                box-shadow: 0 6px 20px rgba(255,219,77,0.3) !important;
            }
            
            .gothurtedx-player-button {
                display: inline-flex !important;
                align-items: center !important;
                margin-left: 12px !important;
                padding: 6px 14px !important;
                background: linear-gradient(135deg, #0088cc, #00a0e9) !important;
                color: white !important;
                text-decoration: none !important;
                border-radius: 30px !important;
                font-size: 13px !important;
                font-weight: 500 !important;
                transition: 0.2s !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                border: none !important;
            }
            
            .gothurtedx-player-button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0,136,204,0.4) !important;
                color: white !important;
                text-decoration: none !important;
            }
            
            @media (max-width: 768px) {
                .gothurtedx-now-playing {
                    bottom: 10px !important;
                    right: 10px !important;
                    padding: 8px 14px !important;
                    font-size: 11px !important;
                    max-width: 220px !important;
                }
                
                .gothurtedx-player-button {
                    display: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Функция для добавления канала в профиль
    function addChannelToProfile() {
        const profileSelectors = [
            ".user__info",
            ".sidebar__user",
            ".profile__header",
            ".header__user"
        ];
        
        for (const selector of profileSelectors) {
            const profile = document.querySelector(selector);
            if (profile && !document.querySelector(".gothurtedx-channel-badge")) {
                const channelLink = document.createElement("a");
                channelLink.className = "gothurtedx-channel-badge";
                channelLink.href = CHANNEL_URL;
                channelLink.target = "_blank";
                channelLink.innerHTML = "📱 @" + CHANNEL_USERNAME;
                profile.appendChild(channelLink);
                break;
            }
        }
    }
    
    // Функция для добавления кнопки в плеер
    function addButtonToPlayer() {
        const playerSelectors = [
            ".player-controls",
            ".player-controls__wrapper",
            ".player-controls__buttons"
        ];
        
        for (const selector of playerSelectors) {
            const player = document.querySelector(selector);
            if (player && !document.querySelector(".gothurtedx-player-button")) {
                const channelBtn = document.createElement("a");
                channelBtn.className = "gothurtedx-player-button";
                channelBtn.href = CHANNEL_URL;
                channelBtn.target = "_blank";
                channelBtn.innerHTML = "📱 @" + CHANNEL_USERNAME;
                player.appendChild(channelBtn);
                break;
            }
        }
    }
    
    // Функция для получения текущего трека
    function getCurrentTrack() {
        try {
            const trackSelectors = [
                ".player-controls__track-info",
                ".player-controls__track",
                ".track__title"
            ];
            
            let trackElement = null;
            for (const selector of trackSelectors) {
                trackElement = document.querySelector(selector);
                if (trackElement) break;
            }
            
            if (trackElement) {
                const title = trackElement.querySelector(".track__title");
                const artist = trackElement.querySelector(".track__artists");
                
                if (title && artist) {
                    return {
                        title: title.textContent.trim(),
                        artist: artist.textContent.trim(),
                        full: artist.textContent.trim() + " - " + title.textContent.trim()
                    };
                }
            }
            
            return null;
        } catch (e) {
            console.log("Track info error:", e);
            return null;
        }
    }
    
    // Функция для создания виджета с треком
    function createTrackWidget() {
        if (document.querySelector(".gothurtedx-now-playing")) {
            return;
        }
        
        const widget = document.createElement("div");
        widget.className = "gothurtedx-now-playing";
        widget.addEventListener("click", function() {
            window.open(CHANNEL_URL, "_blank");
        });
        document.body.appendChild(widget);
    }
    
    // Функция обновления информации о треке
    function updateTrackInfo() {
        const widget = document.querySelector(".gothurtedx-now-playing");
        if (!widget) return;
        
        const track = getCurrentTrack();
        const now = new Date();
        const timeStr = now.getHours().toString().padStart(2, "0") + ":" + now.getMinutes().toString().padStart(2, "0");
        
        if (track && track.full) {
            widget.innerHTML = "🎵 " + track.full + " | <span style=\"color:#fff;\">@" + CHANNEL_USERNAME + "</span> <span style=\"color:#888;font-size:10px;\">" + timeStr + "</span>";
            widget.title = "Сейчас: " + track.full + "\\nКликни для @" + CHANNEL_USERNAME;
        } else {
            widget.innerHTML = "⏸️ Трек не играет | <span style=\"color:#fff;\">@" + CHANNEL_USERNAME + "</span> <span style=\"color:#888;font-size:10px;\">" + timeStr + "</span>";
            widget.title = "Кликни для @" + CHANNEL_USERNAME;
        }
    }
    
    // Инициализация
    function init() {
        console.log("🚀 Запуск Яндекс Музыка плагина с @" + CHANNEL_USERNAME);
        injectStyles();
        createTrackWidget();
        addChannelToProfile();
        addButtonToPlayer();
        
        // Обновление каждую секунду
        setInterval(function() {
            updateTrackInfo();
            addChannelToProfile();
            addButtonToPlayer();
        }, 1000);
        
        // Наблюдение за изменениями в DOM
        const observer = new MutationObserver(function(mutations) {
            for (const mutation of mutations) {
                if (mutation.target && mutation.target.nodeType === 1) {
                    if (mutation.target.classList && 
                        (mutation.target.classList.contains("player-controls__track-info") ||
                         mutation.target.classList.contains("track__title") ||
                         mutation.target.classList.contains("track__artists"))) {
                        updateTrackInfo();
                    }
                }
            }
        });
        
        setTimeout(function() {
            const trackInfo = document.querySelector(".player-controls__track-info");
            if (trackInfo) {
                observer.observe(trackInfo, {
                    childList: true,
                    subtree: true,
                    characterData: true
                });
            }
        }, 3000);
    }
    
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();'''

@client.on(events.NewMessage(pattern=r'\.установить плагин'))
async def install_plugin(event):
    await event.reply("🔧 **Установка плагина Яндекс Музыки...**\n\nПлагин будет добавлен в Tampermonkey/Greasemonkey")
    
    # Отправляем код плагина
    await event.reply(
        "📦 **Код плагина для Яндекс Музыки:**\n\n"
        "```javascript\n" + PLUGIN_CODE + "\n```\n\n"
        "📋 **Инструкция:**\n"
        "1. Установи Tampermonkey (для Chrome) или Greasemonkey (для Firefox)\n"
        "2. Создай новый скрипт\n"
        "3. Вставь этот код\n"
        "4. Сохрани (Ctrl+S)\n"
        "5. Обнови страницу Яндекс Музыки\n\n"
        "👤 **Канал:** @gothurtedx"
    )

@client.on(events.NewMessage(pattern=r'\.помощь плагин'))
async def plugin_help(event):
    help_text = """
**🤖 Плагин Яндекс Музыки**

**Команды:**
• `.установить плагин` - получить код плагина
• `.статус плагина` - проверить статус

**Функции:**
• 🎵 Отображение текущего трека
• 🔄 Автообновление при смене трека
• 📱 Кнопка @gothurtedx в профиле
• 🎮 Кнопка в плеере
• ⏱ Время последнего обновления

**Установка:**
1. Установи Tampermonkey
2. Скопируй код из `.установить плагин`
3. Вставь в новый скрипт
4. Обнови music.yandex.ru

**Автор:** @gothurtedx
"""
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r'\.статус плагина'))
async def plugin_status(event):
    await event.reply(
        "✅ **Плагин активен и готов к установке**\n\n"
        "📊 **Статистика:**\n"
        "• Версия: 1.4\n"
        "• Совместимость: Яндекс Музыка\n"
        "• Канал: @gothurtedx\n"
        "• Размер: " + str(len(PLUGIN_CODE)) + " символов\n\n"
        "Используй `.установить плагин` для получения кода"
    )

@client.on(events.NewMessage(pattern=r'\.обновить плагин'))
async def update_plugin(event):
    await event.reply(
        "🔄 **Обновление плагина...**\n\n"
        "Последняя версия уже отправлена!\n"
        "Используй `.установить плагин` для получения актуального кода"
    )

async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Юзербот запущен! Плагин Яндекс Музыки готов к установке")
    print("📱 Канал: @gothurtedx")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
