// ==UserScript==
// @name         Яндекс.Музыка - Now Playing Display with Channel
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Отображает текущий играющий трек в Яндекс.Музыке с прикрепленным каналом
// @author       gothurtedx
// @match        https://music.yandex.ru/*
// @match        https://music.yandex.by/*
// @match        https://music.yandex.kz/*
// @match        https://music.yandex.ua/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Функция для прикрепления канала
    function attachChannel() {
        // Проверяем, есть ли уже ссылка на канал в профиле
        const profileSection = document.querySelector('.user__info') || document.querySelector('.sidebar__user');
        
        if (profileSection && !document.querySelector('#gothurtedx-channel')) {
            const channelLink = document.createElement('a');
            channelLink.id = 'gothurtedx-channel';
            channelLink.href = 'https://t.me/gothurtedx';
            channelLink.target = '_blank';
            channelLink.textContent = '📱 @gothurtedx';
            channelLink.style.cssText = `
                display: inline-block;
                margin-left: 10px;
                padding: 5px 12px;
                background: linear-gradient(135deg, #0088cc, #00a0e9);
                color: white;
                text-decoration: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                transition: transform 0.2s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            
            // Добавляем эффект при наведении
            channelLink.addEventListener('mouseenter', () => {
                channelLink.style.transform = 'scale(1.05)';
            });
            
            channelLink.addEventListener('mouseleave', () => {
                channelLink.style.transform = 'scale(1)';
            });
            
            profileSection.appendChild(channelLink);
        }
    }

    // Создаем виджет для отображения трека
    function createNowPlayingWidget() {
        // Проверяем, не существует ли уже виджет
        if (document.getElementById('ya-music-now-playing')) {
            return;
        }

        const widget = document.createElement('div');
        widget.id = 'ya-music-now-playing';
        widget.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1E1E2A, #2A2A3A);
            color: #FFDB4D;
            padding: 15px 25px;
            border-radius: 50px;
            font-family: 'Segoe UI', Arial, sans-serif;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            z-index: 9999;
            border: 2px solid #FFDB4D;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            backdrop-filter: blur(5px);
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        `;

        // Добавляем эффекты при наведении
        widget.addEventListener('mouseenter', () => {
            widget.style.transform = 'scale(1.02)';
            widget.style.boxShadow = '0 6px 20px rgba(255, 219, 77, 0.3)';
        });

        widget.addEventListener('mouseleave', () => {
            widget.style.transform = 'scale(1)';
            widget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.5)';
        });

        // При клике открываем канал
        widget.addEventListener('click', () => {
            window.open('https://t.me/gothurtedx', '_blank');
        });

        document.body.appendChild(widget);
        
        // Добавляем информацию о канале в виджет
        updateTrackInfo();
    }

    // Функция для получения информации о текущем треке
    function getCurrentTrack() {
        const trackTitle = document.querySelector('.player-controls__track-info .track__title');
        const trackArtist = document.querySelector('.player-controls__track-info .track__artists');
        
        if (trackTitle && trackArtist) {
            const title = trackTitle.textContent.trim();
            const artist = trackArtist.textContent.trim();
            return `${artist} - ${title}`;
        }
        
        return '🎵 Трек не играет';
    }

    // Функция обновления информации о треке
    function updateTrackInfo() {
        const widget = document.getElementById('ya-music-now-playing');
        if (!widget) return;

        const trackInfo = getCurrentTrack();
        
        // Добавляем эмодзи в зависимости от статуса
        if (trackInfo === '🎵 Трек не играет') {
            widget.innerHTML = `⏸️ ${trackInfo} | <span style="color: #fff;">@gothurtedx</span>`;
        } else {
            widget.innerHTML = `🎵 ${trackInfo} | <span style="color: #fff;">@gothurtedx</span>`;
        }
        
        // Добавляем тултип с полным названием трека
        if (trackInfo !== '🎵 Трек не играет') {
            widget.title = `Сейчас играет: ${trackInfo}\nКликни, чтобы перейти в канал @gothurtedx`;
        } else {
            widget.title = 'Кликни, чтобы перейти в канал @gothurtedx';
        }
    }

    // Функция для добавления канала в шапку плеера
    function addChannelToPlayer() {
        const playerControls = document.querySelector('.player-controls');
        
        if (playerControls && !document.querySelector('#player-channel-link')) {
            const channelButton = document.createElement('a');
            channelButton.id = 'player-channel-link';
            channelButton.href = 'https://t.me/gothurtedx';
            channelButton.target = '_blank';
            channelButton.innerHTML = '📱 @gothurtedx';
            channelButton.style.cssText = `
                display: inline-block;
                margin-left: 15px;
                padding: 8px 15px;
                background: linear-gradient(135deg, #0088cc, #00a0e9);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: 500;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: all 0.3s;
                border: 1px solid rgba(255,255,255,0.2);
            `;
            
            channelButton.addEventListener('mouseenter', () => {
                channelButton.style.transform = 'translateY(-2px)';
                channelButton.style.boxShadow = '0 4px 10px rgba(0,136,204,0.4)';
            });
            
            channelButton.addEventListener('mouseleave', () => {
                channelButton.style.transform = 'translateY(0)';
                channelButton.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            });
            
            playerControls.appendChild(channelButton);
        }
    }

    // Инициализация плагина
    function init() {
        createNowPlayingWidget();
        attachChannel();
        addChannelToPlayer();
        
        // Обновляем информацию о треке каждую секунду
        setInterval(() => {
            updateTrackInfo();
            // Периодически проверяем наличие канала в профиле
            attachChannel();
            addChannelToPlayer();
        }, 1000);
        
        // Добавляем наблюдатель за изменениями в DOM для отслеживания смены трека
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.classList && 
                    (mutation.target.classList.contains('player-controls__track-info') ||
                     mutation.target.classList.contains('track__title') ||
                     mutation.target.classList.contains('track__artists'))) {
                    updateTrackInfo();
                }
            });
        });

        // Начинаем наблюдение за изменениями
        const trackInfoElement = document.querySelector('.player-controls__track-info');
        if (trackInfoElement) {
            observer.observe(trackInfoElement, { 
                childList: true, 
                subtree: true,
                characterData: true 
            });
        }
    }

    // Запускаем плагин после загрузки страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Добавляем стили для адаптации на мобильных устройствах
    const style = document.createElement('style');
    style.textContent = `
        @media (max-width: 768px) {
            #ya-music-now-playing {
                bottom: 10px;
                right: 10px;
                padding: 10px 15px;
                font-size: 12px;
                max-width: 250px;
            }
            
            #player-channel-link {
                display: none !important;
            }
            
            #gothurtedx-channel {
                font-size: 11px !important;
                padding: 3px 8px !important;
            }
        }
    `;
    document.head.appendChild(style);

    console.log('✅ Плагин Яндекс.Музыки с каналом @gothurtedx загружен!');
})();
