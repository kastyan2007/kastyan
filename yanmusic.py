// ==UserScript==
// @name         Яндекс.Музыка - Now Playing Display with Channel
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Отображает текущий играющий трек в Яндекс.Музыке с прикрепленным каналом
// @author       gothurtedx
// @match        https://music.yandex.ru/*
// @match        https://music.yandex.by/*
// @match        https://music.yandex.kz/*
// @match        https://music.yandex.ua/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // Функция для безопасного добавления CSS стилей
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #gothurtedx-channel {
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
            }
            
            #gothurtedx-channel:hover {
                transform: scale(1.05);
            }
            
            #ya-music-now-playing {
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
            }
            
            #ya-music-now-playing:hover {
                transform: scale(1.02);
                box-shadow: 0 6px 20px rgba(255, 219, 77, 0.3);
            }
            
            #player-channel-link {
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
            }
            
            #player-channel-link:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 10px rgba(0,136,204,0.4);
            }
            
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
    }

    // Функция для прикрепления канала
    function attachChannel() {
        const profileSection = document.querySelector('.user__info') || document.querySelector('.sidebar__user');
        
        if (profileSection && !document.querySelector('#gothurtedx-channel')) {
            const channelLink = document.createElement('a');
            channelLink.id = 'gothurtedx-channel';
            channelLink.href = 'https://t.me/gothurtedx';
            channelLink.target = '_blank';
            channelLink.textContent = '📱 @gothurtedx';
            profileSection.appendChild(channelLink);
        }
    }

    // Создаем виджет для отображения трека
    function createNowPlayingWidget() {
        if (document.getElementById('ya-music-now-playing')) {
            return;
        }

        const widget = document.createElement('div');
        widget.id = 'ya-music-now-playing';
        
        widget.addEventListener('click', () => {
            window.open('https://t.me/gothurtedx', '_blank');
        });

        document.body.appendChild(widget);
        updateTrackInfo();
    }

    // Функция для получения информации о текущем треке
    function getCurrentTrack() {
        try {
            const trackTitle = document.querySelector('.player-controls__track-info .track__title');
            const trackArtist = document.querySelector('.player-controls__track-info .track__artists');
            
            if (trackTitle && trackArtist) {
                const title = trackTitle.textContent.trim();
                const artist = trackArtist.textContent.trim();
                return artist + ' - ' + title;
            }
            
            return '🎵 Трек не играет';
        } catch (e) {
            return '🎵 Трек не играет';
        }
    }

    // Функция обновления информации о треке
    function updateTrackInfo() {
        const widget = document.getElementById('ya-music-now-playing');
        if (!widget) return;

        const trackInfo = getCurrentTrack();
        
        if (trackInfo === '🎵 Трек не играет') {
            widget.innerHTML = '⏸️ ' + trackInfo + ' | <span style="color: #fff;">@gothurtedx</span>';
            widget.title = 'Кликни, чтобы перейти в канал @gothurtedx';
        } else {
            widget.innerHTML = '🎵 ' + trackInfo + ' | <span style="color: #fff;">@gothurtedx</span>';
            widget.title = 'Сейчас играет: ' + trackInfo + '\nКликни, чтобы перейти в канал @gothurtedx';
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
            playerControls.appendChild(channelButton);
        }
    }

    // Инициализация плагина
    function init() {
        addStyles();
        createNowPlayingWidget();
        attachChannel();
        addChannelToPlayer();
        
        // Обновляем информацию о треке каждую секунду
        setInterval(function() {
            updateTrackInfo();
            attachChannel();
            addChannelToPlayer();
        }, 1000);
        
        // Добавляем наблюдатель за изменениями в DOM
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.target && mutation.target.classList) {
                    if (mutation.target.classList.contains('player-controls__track-info') ||
                        mutation.target.classList.contains('track__title') ||
                        mutation.target.classList.contains('track__artists')) {
                        updateTrackInfo();
                    }
                }
            });
        });

        // Начинаем наблюдение за изменениями
        setTimeout(function() {
            const trackInfoElement = document.querySelector('.player-controls__track-info');
            if (trackInfoElement) {
                observer.observe(trackInfoElement, { 
                    childList: true, 
                    subtree: true,
                    characterData: true 
                });
            }
        }, 2000);
    }

    // Запускаем плагин после загрузки страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('✅ Плагин Яндекс.Музыки с каналом @gothurtedx загружен!');
})();
