#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
osu!helper v2.0 - Enhanced Edition
Created by Kiro AI, Manus AI & debikv tupoi vibecoder
Enhanced with Statistics, Hotkeys, Customization, and Advanced Features
"""

import customtkinter as ctk
import websocket
import json
import threading
import time
from datetime import datetime
from pynput.keyboard import Controller, Key, Listener, GlobalHotKeys
import queue
import sys
import psutil
import win32gui
import win32process
import win32api
import win32con
import os
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import filedialog, messagebox
import tkinter as tk

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "osu_helper_config.json"
STATS_FILE = "osu_helper_stats.json"

class ColorSchemes:
    """Color scheme definitions with extended palette"""
    SCHEMES = {
        'blue': {
            'primary': '#3b8ed0',
            'success': '#30d158', 
            'warning': '#ff9500',
            'danger': '#ff3b30',
            'info': '#007bff',
            'button': '#1f538d'
        },
        'purple': {
            'primary': '#8e44ad',
            'success': '#27ae60',
            'warning': '#f39c12', 
            'danger': '#e74c3c',
            'info': '#9b59b6',
            'button': '#6c3483'
        },
        'green': {
            'primary': '#2ecc71',
            'success': '#27ae60',
            'warning': '#f1c40f',
            'danger': '#e74c3c', 
            'info': '#16a085',
            'button': '#239b56'
        },
        'orange': {
            'primary': '#e67e22',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#c0392b',
            'info': '#d35400',
            'button': '#ca6f1e'
        },
        'red': {
            'primary': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#c0392b',
            'info': '#e74c3c',
            'button': '#cb4335'
        },
        'teal': {
            'primary': '#1abc9c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'button': '#148f77'
        },
        'pink': {
            'primary': '#e91e63',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#e91e63',
            'button': '#c2185b'
        },
        'cyan': {
            'primary': '#00bcd4',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#00acc1',
            'button': '#0097a7'
        },
        'indigo': {
            'primary': '#3f51b5',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#3f51b5',
            'button': '#303f9f'
        },
        'lime': {
            'primary': '#8bc34a',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#689f38',
            'button': '#689f38'
        },
        'amber': {
            'primary': '#ffc107',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#ffa000',
            'button': '#ffa000'
        },
        'deep_purple': {
            'primary': '#673ab7',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#512da8',
            'button': '#512da8'
        }
    }
    
    @staticmethod
    def get_color_wheel_colors():
        """Get colors arranged in a color wheel pattern"""
        return [
            ('🔴 Red', 'red'),
            ('🟠 Orange', 'orange'), 
            ('🟡 Amber', 'amber'),
            ('🟢 Green', 'green'),
            ('🟢 Lime', 'lime'),
            ('🔵 Teal', 'teal'),
            ('🔵 Cyan', 'cyan'),
            ('🔵 Blue', 'blue'),
            ('🟣 Indigo', 'indigo'),
            ('🟣 Purple', 'purple'),
            ('🟣 Deep Purple', 'deep_purple'),
            ('🩷 Pink', 'pink')
        ]

class Statistics:
    """Statistics tracking and management"""
    
    def __init__(self):
        self.session_stats = {
            'misses': [],
            'restarts': 0,
            'maps_played': 0,
            'session_start': datetime.now(),
            'accuracy_data': [],
            'combo_data': [],
            'pp_data': [],
            'hp_data': []
        }
        self.all_time_stats = self.load_stats()
        
    def add_miss(self, miss_count, map_name="Unknown"):
        """Add miss data point"""
        timestamp = datetime.now()
        miss_data = {
            'timestamp': timestamp.isoformat(),
            'count': miss_count,
            'map': map_name
        }
        self.session_stats['misses'].append(miss_data)
        self.all_time_stats['misses'].append(miss_data)
        
    def add_restart(self):
        """Add restart count"""
        self.session_stats['restarts'] += 1
        self.all_time_stats['restarts'] += 1
        
    def add_map_played(self):
        """Add map played count"""
        self.session_stats['maps_played'] += 1
        self.all_time_stats['maps_played'] += 1
        
    def add_gameplay_data(self, accuracy=None, combo=None, pp=None, hp=None):
        """Add gameplay data points"""
        timestamp = datetime.now()
        if accuracy is not None:
            self.session_stats['accuracy_data'].append({'time': timestamp, 'value': accuracy})
        if combo is not None:
            self.session_stats['combo_data'].append({'time': timestamp, 'value': combo})
        if pp is not None:
            self.session_stats['pp_data'].append({'time': timestamp, 'value': pp})
        if hp is not None:
            self.session_stats['hp_data'].append({'time': timestamp, 'value': hp})
            
    def get_miss_averages(self):
        """Calculate miss averages"""
        if not self.session_stats['misses']:
            return {'session': 0, 'all_time': 0}
            
        session_avg = sum(m['count'] for m in self.session_stats['misses']) / len(self.session_stats['misses'])
        all_time_avg = sum(m['count'] for m in self.all_time_stats['misses']) / len(self.all_time_stats['misses'])
        
        return {'session': round(session_avg, 2), 'all_time': round(all_time_avg, 2)}
        
    def export_csv(self, filename):
        """Export statistics to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Misses', 'Map'])
            for miss in self.all_time_stats['misses']:
                writer.writerow([miss['timestamp'], miss['count'], miss['map']])
                
    def export_json(self, filename):
        """Export statistics to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_time_stats, f, indent=2, ensure_ascii=False)
            
    def load_stats(self):
        """Load statistics from file"""
        if not os.path.exists(STATS_FILE):
            return {'misses': [], 'restarts': 0, 'maps_played': 0}
            
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'misses': [], 'restarts': 0, 'maps_played': 0}
            
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.all_time_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Can't log here as we might not have GUI yet
            pass

class Language:
    """Language manager with extended translations"""
    
    def __init__(self):
        self.current = "ru"
        
    def toggle(self):
        self.current = "en" if self.current == "ru" else "ru"
        
    @property
    def is_russian(self):
        return self.current == "ru"
        
    TEXTS = {
        'ru': {
            'title': 'osu!helper v2.0',
            'credits': 'by Kiro AI, Manus AI & debikv tupoi vibecoder - Enhanced Edition',
            'disconnected': 'Не подключено',
            'connected': 'Подключено',
            'dark': '🌙 Темная',
            'light': '☀️ Светлая',
            'russian': '🇷🇺 RU',
            'english': 'EN',
            'current_misses': 'Текущие миссы',
            'threshold': 'Порог',
            'total_restarts': 'Перезагрузок',
            'current_map': '🎵 Текущая карта',
            'not_playing': 'Не в игре',
            'miss_threshold': 'Порог миссов:',
            'start_monitoring': '▶ Начать мониторинг',
            'stop_monitoring': '⏸ Остановить',
            'clear_log': '🗑 Очистить лог',
            'activity_log': '📋 Журнал активности',
            'footer': 'osu!helper v2.0 Enhanced | Powered by TOSU API | Created by Kiro AI, Manus AI & debikv tupoi vibecoder',
            'monitoring_started': '✓ Мониторинг запущен',
            'monitoring_stopped': '✓ Мониторинг остановлен',
            'connecting': 'Подключение к TOSU: {}',
            'connection_error': '✗ Ошибка подключения: {}',
            'connected_tosu': '✓ Подключено к TOSU',
            'disconnected_tosu': '⚠ Отключено от TOSU',
            'websocket_error': '✗ Ошибка WebSocket: {}',
            'data_error': '✗ Ошибка данных: {}',
            'new_map': '🎵 Новая карта - сброс счетчика',
            'threshold_reached': '✗ +{} мисс ({}/{}) - ПОРОГ!',
            'close_to_threshold': '⚠ +{} мисс ({}/{}) - близко',
            'miss_logged': '✗ +{} мисс ({}/{})',
            'cooldown_active': '⏳ Кулдаун {:.1f}с',
            'restarting': '🔄 Перезагрузка...',
            'pressing_key': '⏳ Нажатие {}...',
            'key_released': '✓ Клавиша отпущена',
            'counter_reset': '✓ Счетчик сброшен',
            'waiting': '⏳ Ожидание 3с...',
            'ready': '✓ Готово',
            'key_error': '✗ Ошибка: {}',
            'osu_focused': '✅ osu! в фокусе',
            'osu_not_focused': '⚠ osu! не в фокусе',
            'log_cleared': 'Лог очищен',
            'threshold_set': 'Порог: {}',
            'theme_changed': 'Тема: {}',
            'language_changed': 'Язык: {}',
            'restart_key': 'Клавиша перезапуска:',
            'hold_duration': 'Время зажатия (сек):',
            'key_settings': '⌨️ Настройки клавиши',
            'settings_applied': 'Настройки: {} на {:.1f}с',
            'capture_key': '🎯 Нажми клавишу',
            'key_captured': 'Клавиша: {}',
            'config_saved': '💾 Конфиг сохранен',
            'config_loaded': '📂 Конфиг загружен',
            'cooldown_duration': 'Кулдаун (сек):',
            'cooldown_set': 'Кулдаун: {}с',
            'apply': 'Применить',
            'not_set': 'Не задана',
            'hit_thresholds_section': 'Пороги очков:',
            'enable_hit100_threshold': 'Включить порог 100 очков',
            'hit100_threshold_label': 'Порог 100 очков:',
            'enable_hit50_threshold': 'Включить порог 50 очков',
            'hit50_threshold_label': 'Порог 50 очков:',
            'hit100_threshold_enabled': 'Порог 100 очков включен',
            'hit100_threshold_disabled': 'Порог 100 очков выключен',
            'hit50_threshold_enabled': 'Порог 50 очков включен',
            'hit50_threshold_disabled': 'Порог 50 очков выключен',
            'hit100_threshold_applied': 'Порог 100 очков: {}',
            'hit50_threshold_applied': 'Порог 50 очков: {}',
            'hit100_threshold_reached': 'Достигнут порог 100 очков: {} (≥{})',
            'hit50_threshold_reached': 'Достигнут порог 50 очков: {} (≥{})',
            'current_hit100': 'Hit 100',
            'current_hit50': 'Hit 50',
            # New translations
            'statistics': '📊 Статистика',
            'miss_graph': 'График миссов',
            'session_avg': 'Сессия: {}',
            'alltime_avg': 'Всего: {}',
            'export_csv': 'Экспорт CSV',
            'export_json': 'Экспорт JSON',
            'hotkeys': '⌨️ Горячие клавиши',
            'mini_mode': '📱 Мини режим',
            'always_on_top': '📌 Поверх всех окон',
            'transparency': '👻 Прозрачность',
            'color_scheme': '🎨 Цветовая схема',
            'font_size': '🔤 Размер шрифта',
            'show_accuracy': 'Показать точность',
            'show_combo': 'Показать комбо',
            'show_pp': 'Показать PP',
            'show_hp': 'Показать HP',
            'show_progress': 'Показать прогресс',
            'accuracy': 'Точность: {:.2f}%',
            'combo': 'Комбо: {}x',
            'pp': 'PP: {:.0f}',
            'hp': 'HP: {:.1f}%',
            'progress': 'Прогресс: {:.1f}%',
            'import_settings': 'Импорт настроек',
            'export_settings': 'Экспорт настроек',
            'settings_imported': 'Настройки импортированы',
            'settings_exported': 'Настройки экспортированы',
            'hotkey_mute': 'Ctrl+M: Вкл/выкл звук',
            'hotkey_log': 'Ctrl+L: Очистить лог',
            'hotkey_threshold': 'Ctrl+↑/↓: Порог ±1',
            'hotkey_mini': 'Ctrl+K: Мини режим',
            'customize': '⚙️ Настройки',
            'mini_mode_active': 'Мини режим активен',
            'normal_mode_active': 'Обычный режим активен',
            'click_through_enabled': '👻 Режим прозрачности (клики проходят сквозь)',
            'click_through_disabled': '👆 Интерактивный режим (можно кликать)',
            'resize_hint': '💡 Подсказка: Измените размер окна, потянув за края'
        },
        'en': {
            'title': 'osu!helper v2.0',
            'credits': 'by Kiro AI, Manus AI & debikv tupoi vibecoder - Enhanced Edition',
            'disconnected': 'Disconnected',
            'connected': 'Connected',
            'dark': '🌙 Dark',
            'light': '☀️ Light',
            'russian': '🇷🇺 RU',
            'english': 'EN',
            'current_misses': 'Current Misses',
            'threshold': 'Threshold',
            'total_restarts': 'Total Restarts',
            'current_map': '🎵 Current Map',
            'not_playing': 'Not playing',
            'miss_threshold': 'Miss Threshold:',
            'start_monitoring': '▶ Start Monitoring',
            'stop_monitoring': '⏸ Stop Monitoring',
            'clear_log': '🗑 Clear Log',
            'activity_log': '📋 Activity Log',
            'footer': 'osu!helper v2.0 Enhanced | Powered by TOSU API | Created by Kiro AI, Manus AI & debikv tupoi vibecoder',
            'monitoring_started': '✓ Monitoring started',
            'monitoring_stopped': '✓ Monitoring stopped',
            'connecting': 'Connecting to TOSU: {}',
            'connection_error': '✗ Connection error: {}',
            'connected_tosu': '✓ Connected to TOSU',
            'disconnected_tosu': '⚠ Disconnected from TOSU',
            'websocket_error': '✗ WebSocket error: {}',
            'data_error': '✗ Data error: {}',
            'new_map': '🎵 New map - counters reset',
            'threshold_reached': '✗ +{} miss ({}/{}) - THRESHOLD REACHED!',
            'close_to_threshold': '⚠ +{} miss ({}/{}) - close to threshold',
            'miss_logged': '✗ +{} miss ({}/{})',
            'cooldown_active': '⏳ Cooldown {:.1f}s',
            'restarting': '🔄 Restarting...',
            'pressing_key': '⏳ Pressing {}...',
            'key_released': '✓ Key released',
            'counter_reset': '✓ Counter reset',
            'waiting': '⏳ Waiting 3s...',
            'ready': '✓ Ready',
            'key_error': '✗ Error: {}',
            'osu_focused': '✅ osu! focused',
            'osu_not_focused': '⚠ osu! not focused',
            'log_cleared': 'Log cleared',
            'threshold_set': 'Threshold: {}',
            'theme_changed': 'Theme: {}',
            'language_changed': 'Language: {}',
            'restart_key': 'Restart Key:',
            'hold_duration': 'Hold Duration (sec):',
            'key_settings': '⌨️ Key Settings',
            'settings_applied': 'Settings applied: {} for {:.1f}s',
            'capture_key': '🎯 Press Any Key',
            'key_captured': 'Key captured: {}',
            'config_saved': '💾 Config saved',
            'config_loaded': '📂 Config loaded',
            'cooldown_duration': 'Cooldown (sec):',
            'cooldown_set': 'Cooldown: {}s',
            'apply': 'Apply',
            'not_set': 'Not set',
            'hit_thresholds_section': 'Hit Score Thresholds:',
            'enable_hit100_threshold': 'Enable 100-hit threshold',
            'hit100_threshold_label': '100-hit threshold:',
            'enable_hit50_threshold': 'Enable 50-hit threshold',
            'hit50_threshold_label': '50-hit threshold:',
            'hit100_threshold_enabled': '100-hit threshold enabled',
            'hit100_threshold_disabled': '100-hit threshold disabled',
            'hit50_threshold_enabled': '50-hit threshold enabled',
            'hit50_threshold_disabled': '50-hit threshold disabled',
            'hit100_threshold_applied': '100-hit threshold: {}',
            'hit50_threshold_applied': '50-hit threshold: {}',
            'hit100_threshold_reached': '100-hit threshold reached: {} (≥{})',
            'hit50_threshold_reached': '50-hit threshold reached: {} (≥{})',
            'current_hit100': 'Hit 100',
            'current_hit50': 'Hit 50',
            # New translations
            'statistics': '📊 Statistics',
            'miss_graph': 'Miss Graph',
            'session_avg': 'Session: {}',
            'alltime_avg': 'All-time: {}',
            'export_csv': 'Export CSV',
            'export_json': 'Export JSON',
            'hotkeys': '⌨️ Hotkeys',
            'mini_mode': '📱 Mini Mode',
            'always_on_top': '📌 Always on Top',
            'transparency': '👻 Transparency',
            'color_scheme': '🎨 Color Scheme',
            'font_size': '🔤 Font Size',
            'show_accuracy': 'Show Accuracy',
            'show_combo': 'Show Combo',
            'show_pp': 'Show PP',
            'show_hp': 'Show HP',
            'show_progress': 'Show Progress',
            'accuracy': 'Accuracy: {:.2f}%',
            'combo': 'Combo: {}x',
            'pp': 'PP: {:.0f}',
            'hp': 'HP: {:.1f}%',
            'progress': 'Progress: {:.1f}%',
            'import_settings': 'Import Settings',
            'export_settings': 'Export Settings',
            'settings_imported': 'Settings imported successfully',
            'settings_exported': 'Settings exported successfully',
            'hotkey_mute': 'Ctrl+M: Toggle Mute',
            'hotkey_log': 'Ctrl+L: Clear Log',
            'hotkey_threshold': 'Ctrl+↑/↓: Threshold ±1',
            'hotkey_mini': 'Ctrl+K: Mini Mode',
            'customize': '⚙️ Customize',
            'mini_mode_active': 'Mini mode activated',
            'normal_mode_active': 'Normal mode activated',
            'click_through_enabled': '👻 Click-through mode (clicks pass through)',
            'click_through_disabled': '👆 Interactive mode (can click)',
            'resize_hint': '💡 Tip: Resize window by dragging edges'
        }
    }
    
    def get(self, key):
        return self.TEXTS[self.current].get(key, key)


class OsuHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("osu!helper v2.0 Enhanced")
        self.root.geometry("1000x800")
        self.root.minsize(700, 600)
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Language and theme
        self.lang = Language()
        self.current_theme = "dark"
        self.color_scheme = "blue"
        self.font_size = 12
        
        # Window properties
        self.always_on_top = False
        self.transparency = 1.0
        self.mini_mode = False
        
        # Statistics
        self.stats = Statistics()
        
        # TOSU connection
        self.ws = None
        self.ws_thread = None
        self.running = False
        self.connected = False
        
        # Miss tracking
        self.current_misses = 0
        self.our_miss_count = 0
        self.last_tosu_misses = 0
        self.miss_threshold = 5
        self.total_restarts = 0
        self.current_map_id = None
        self.current_map_name = "Unknown"
        self.threshold_triggered = False
        
        # Hit value threshold settings (100-hit and 50-hit notes)
        self.hit100_threshold_enabled = False
        self.hit100_threshold = 10  # Threshold for 100-hit notes count
        self.current_hit100 = 0
        self.last_hit100 = 0
        
        self.hit50_threshold_enabled = False
        self.hit50_threshold = 5  # Threshold for 50-hit notes count
        self.current_hit50 = 0
        self.last_hit50 = 0
        
        # Additional TOSU data
        self.current_accuracy = 0.0
        self.current_combo = 0
        self.current_pp = 0.0
        self.current_hp = 0.0
        self.current_progress = 0.0
        
        # Display toggles
        self.show_accuracy = True
        self.show_combo = True
        self.show_pp = True
        self.show_hp = True
        self.show_progress = True
        
        # Restart settings
        self.restart_key = Key.f2  # Default to F2
        self.restart_key_name = "F2"
        self.hold_duration = 1.5
        self.cooldown_duration = 10.0
        
        # Protection
        self.is_restarting = False
        self.last_restart_time = 0
        
        # Keyboard
        self.keyboard = Controller()
        self.key_listener = None
        self.capturing_key = False
        self.hotkeys = None
        
        # Load config
        self.load_config()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Create GUI
        self.create_gui()
        
        # Update connection status after GUI creation
        self.update_connection_status()
        
        # Configure grid weights for resizing
        self.configure_grid_weights()
        
        # Apply window properties
        self.apply_window_properties()
        
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            # Global hotkeys (work with any layout)
            hotkey_map = {
                '<ctrl>+m': self.toggle_mute,
                '<ctrl>+l': self.clear_log,
                '<ctrl>+<up>': self.increase_threshold,
                '<ctrl>+<down>': self.decrease_threshold,
                '<ctrl>+k': self.toggle_mini_mode
            }
            self.hotkeys = GlobalHotKeys(hotkey_map)
            self.hotkeys.start()
            
            # Bind keys to window (works regardless of layout)
            # Using keycodes instead of keysyms for layout independence
            self.root.bind_all('<Control-KeyPress>', self.handle_ctrl_key)
            
        except Exception as e:
            self.log_message(f"⌨️ Hotkey setup error: {e}", "red")
            
    def handle_ctrl_key(self, event):
        """Handle Ctrl key combinations regardless of keyboard layout"""
        try:
            # Get the keycode for layout-independent handling
            keycode = event.keycode
            
            # Common keycodes (may vary by system, but these are typical)
            if keycode == 77 or keycode == 50:  # M key (different layouts)
                self.toggle_mute()
            elif keycode == 76 or keycode == 46:  # L key
                self.clear_log()
            elif keycode == 75 or keycode == 45:  # K key
                self.toggle_mini_mode()
            elif keycode == 38:  # Up arrow
                self.increase_threshold()
            elif keycode == 40:  # Down arrow
                self.decrease_threshold()
                
        except Exception as e:
            self.log_message(f"⌨️ Key handling error: {e}", "red")
            
    def toggle_mute(self):
        """Toggle system mute (placeholder)"""
        self.log_message("🔇 Mute toggled (hotkey)", "blue")
        
    def increase_threshold(self):
        """Increase threshold by 1"""
        if self.miss_threshold < 100:
            self.miss_threshold += 1
            self.threshold_value.configure(text=str(self.miss_threshold))
            self.threshold_entry.delete(0, "end")
            self.threshold_entry.insert(0, str(self.miss_threshold))
            self.log_message(f"⬆ Threshold: {self.miss_threshold}", "blue")
            self.save_config()
            
    def decrease_threshold(self):
        """Decrease threshold by 1"""
        if self.miss_threshold > 1:
            self.miss_threshold -= 1
            self.threshold_value.configure(text=str(self.miss_threshold))
            self.threshold_entry.delete(0, "end")
            self.threshold_entry.insert(0, str(self.miss_threshold))
            self.log_message(f"⬇ Threshold: {self.miss_threshold}", "blue")
            self.save_config()    
    
    def apply_window_properties(self):
        """Apply window properties like transparency and always on top"""
        if not self.mini_mode:
            # Normal mode - ensure proper window state
            try:
                self.root.attributes('-topmost', self.always_on_top)
                self.root.attributes('-alpha', self.transparency)
                
                # Ensure no transparent color in normal mode
                try:
                    self.root.attributes('-transparentcolor', '')
                except:
                    pass
                    
                # Force window refresh
                self.root.update_idletasks()
                
            except Exception as e:
                print(f"Error applying window properties: {e}")
        else:
            # Mini mode - keep topmost
            try:
                self.root.attributes('-topmost', True)
                self.root.attributes('-alpha', 0.85)
            except:
                pass
            
    def configure_grid_weights(self):
        """Configure grid weights for responsive layout"""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        if hasattr(self, 'main_frame'):
            self.main_frame.grid_rowconfigure(8, weight=1)  # Log section expands
            self.main_frame.grid_columnconfigure(0, weight=1)
        
    def create_gui(self):
        """Create the GUI"""
        if self.mini_mode:
            self.create_mini_gui()
        else:
            self.create_full_gui()
            
    def create_full_gui(self):
        """Create the full GUI"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Stats cards
        self.create_stats()
        
        # Additional TOSU data display
        self.create_tosu_data_display()
        
        # Current map
        self.create_map_display()
        
        # Threshold setting
        self.create_threshold_setting()
        
        # Key settings
        self.create_key_settings()
        
        # Cooldown setting
        self.create_cooldown_setting()
        
        # Action buttons
        self.create_action_buttons()
        
        # Statistics section
        self.create_statistics_section()
        
        # Activity log
        self.create_log()
        
        # Customization panel
        self.create_customization_panel()
        
        # Footer
        self.create_footer()
        
        self.configure_grid_weights()
        
    def create_mini_gui(self):
        """Create mini mode GUI with transparent overlay"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configure window for mini mode
        self.root.geometry("400x300")
        self.root.overrideredirect(False)  # Keep window decorations for resizing
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)
        self.root.resizable(True, True)  # Allow resizing
        self.root.minsize(300, 200)      # Minimum size
        self.root.maxsize(800, 600)      # Maximum size
        
        # Set background to a color that will be made transparent
        self.root.configure(bg='#010101')
        
        # Make background transparent
        try:
            self.root.attributes('-transparentcolor', '#010101')
        except:
            pass
        
        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Create a semi-transparent background frame for text readability
        bg_frame = ctk.CTkFrame(
            self.root, 
            fg_color=("gray20", "gray10"),
            corner_radius=10,
            border_width=1,
            border_color=("gray40", "gray60")
        )
        bg_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add drag functionality to bg_frame
        bg_frame.bind("<Button-1>", self.start_drag)
        bg_frame.bind("<B1-Motion>", self.on_drag)
        
        # Main content frame
        main_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Add drag functionality to main_frame too
        main_frame.bind("<Button-1>", self.start_drag)
        main_frame.bind("<B1-Motion>", self.on_drag)
        
        # Title with close hint
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎮 osu!helper Mini | Ctrl+K to toggle",
            font=("Segoe UI", 12, "bold"),
            text_color="white"
        )
        title_label.pack()
        
        # Resize hint
        hint_label = ctk.CTkLabel(
            title_frame,
            text="↔️ Resizable window",
            font=("Segoe UI", 8),
            text_color="gray"
        )
        hint_label.pack(pady=(0, 5))
        
        # Connection status
        status_text = self.lang.get('connected') if self.connected else self.lang.get('disconnected')
        status_color = "lime" if self.connected else "red"
        
        self.mini_status = ctk.CTkLabel(
            title_frame,
            text=f"● {status_text}",
            font=("Segoe UI", 10),
            text_color=status_color
        )
        self.mini_status.pack()
        
        # Live Game Data Section
        game_data_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        game_data_frame.pack(fill="x", pady=5)
        
        # Row 1: Misses and Threshold
        row1_frame = ctk.CTkFrame(game_data_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=2)
        
        # Misses
        miss_container = ctk.CTkFrame(row1_frame, fg_color="transparent")
        miss_container.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            miss_container, 
            text="Misses:", 
            font=("Segoe UI", 10),
            text_color="gray"
        ).pack(anchor="w")
        
        self.mini_miss_value = ctk.CTkLabel(
            miss_container,
            text="0",
            font=("Segoe UI", 24, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['danger']
        )
        self.mini_miss_value.pack(anchor="w")
        
        # Threshold
        threshold_container = ctk.CTkFrame(row1_frame, fg_color="transparent")
        threshold_container.pack(side="right", fill="x", expand=True)
        
        ctk.CTkLabel(
            threshold_container, 
            text="Threshold:", 
            font=("Segoe UI", 10),
            text_color="gray"
        ).pack(anchor="e")
        
        self.mini_threshold_value = ctk.CTkLabel(
            threshold_container,
            text=str(self.miss_threshold),
            font=("Segoe UI", 24, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['warning']
        )
        self.mini_threshold_value.pack(anchor="e")
        
        # Row 2: Accuracy and Combo
        if self.show_accuracy or self.show_combo:
            row2_frame = ctk.CTkFrame(game_data_frame, fg_color="transparent")
            row2_frame.pack(fill="x", pady=2)
            
            if self.show_accuracy:
                acc_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
                acc_container.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    acc_container, 
                    text="Accuracy:", 
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(anchor="w")
                
                self.mini_accuracy_label = ctk.CTkLabel(
                    acc_container,
                    text="0.00%",
                    font=("Segoe UI", 16, "bold"),
                    text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
                )
                self.mini_accuracy_label.pack(anchor="w")
            
            if self.show_combo:
                combo_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
                combo_container.pack(side="right", fill="x", expand=True)
                
                ctk.CTkLabel(
                    combo_container, 
                    text="Combo:", 
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(anchor="e")
                
                self.mini_combo_label = ctk.CTkLabel(
                    combo_container,
                    text="0x",
                    font=("Segoe UI", 16, "bold"),
                    text_color=ColorSchemes.SCHEMES[self.color_scheme]['success']
                )
                self.mini_combo_label.pack(anchor="e")
        
        # Row 3: PP and HP
        if self.show_pp or self.show_hp:
            row3_frame = ctk.CTkFrame(game_data_frame, fg_color="transparent")
            row3_frame.pack(fill="x", pady=2)
            
            if self.show_pp:
                pp_container = ctk.CTkFrame(row3_frame, fg_color="transparent")
                pp_container.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    pp_container, 
                    text="PP:", 
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(anchor="w")
                
                self.mini_pp_label = ctk.CTkLabel(
                    pp_container,
                    text="0",
                    font=("Segoe UI", 16, "bold"),
                    text_color=ColorSchemes.SCHEMES[self.color_scheme]['primary']
                )
                self.mini_pp_label.pack(anchor="w")
            
            if self.show_hp:
                hp_container = ctk.CTkFrame(row3_frame, fg_color="transparent")
                hp_container.pack(side="right", fill="x", expand=True)
                
                ctk.CTkLabel(
                    hp_container, 
                    text="HP:", 
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(anchor="e")
                
                self.mini_hp_label = ctk.CTkLabel(
                    hp_container,
                    text="0.0%",
                    font=("Segoe UI", 16, "bold"),
                    text_color=ColorSchemes.SCHEMES[self.color_scheme]['danger']
                )
                self.mini_hp_label.pack(anchor="e")
        
        # Progress bar (if enabled)
        if self.show_progress:
            progress_frame = ctk.CTkFrame(game_data_frame, fg_color="transparent")
            progress_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                progress_frame, 
                text="Progress:", 
                font=("Segoe UI", 9),
                text_color="gray"
            ).pack(anchor="w")
            
            self.mini_progress_label = ctk.CTkLabel(
                progress_frame,
                text="0.0%",
                font=("Segoe UI", 14, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
            )
            self.mini_progress_label.pack(anchor="w")
        
        # Current map (compact)
        map_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        map_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            map_frame, 
            text="🎵 Map:", 
            font=("Segoe UI", 9),
            text_color="gray"
        ).pack(anchor="w")
        
        self.mini_map_label = ctk.CTkLabel(
            map_frame,
            text=self.lang.get('not_playing'),
            font=("Segoe UI", 9),
            text_color="white",
            wraplength=330
        )
        self.mini_map_label.pack(anchor="w")
        
        # Control buttons
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.pack(fill="x", pady=(5, 0))
        
        # Click-through toggle button
        self.click_through_btn = ctk.CTkButton(
            control_frame,
            text="👆 Interactive",
            command=self.toggle_click_through,
            width=110,
            height=25,
            font=("Segoe UI", 9),
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['success'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.click_through_btn.pack(side="left", padx=2)
        
        # Exit mini mode button
        exit_btn = ctk.CTkButton(
            control_frame,
            text="🖥️ Normal",
            command=self.toggle_mini_mode,
            width=80,
            height=25,
            font=("Segoe UI", 9),
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        exit_btn.pack(side="right", padx=2)
        
        # Make window focusable for hotkeys
        self.root.focus_force()
        
        # Add right-click context menu for easy access
        def show_context_menu(event):
            try:
                context_menu = tk.Menu(self.root, tearoff=0)
                context_menu.add_command(label="Toggle Click-Through", command=self.toggle_click_through)
                context_menu.add_command(label="Normal Mode (Ctrl+K)", command=self.toggle_mini_mode)
                context_menu.add_separator()
                context_menu.add_command(label="Close", command=self.root.quit)
                context_menu.tk_popup(event.x_root, event.y_root)
            except:
                pass
        
        bg_frame.bind("<Button-3>", show_context_menu)
        
    def start_drag(self, event):
        """Start dragging the mini window"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        
    def on_drag(self, event):
        """Handle dragging the mini window"""
        try:
            x = self.root.winfo_x() + (event.x_root - self.drag_start_x)
            y = self.root.winfo_y() + (event.y_root - self.drag_start_y)
            self.root.geometry(f"+{x}+{y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
        except:
            pass
        
    def create_header(self):
        """Create header with title and controls"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title and credits
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")
        
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=self.lang.get('title'),
            font=("Segoe UI", 32, "bold")
        )
        self.title_label.pack(anchor="w")
        
        self.credits_label = ctk.CTkLabel(
            title_frame,
            text=self.lang.get('credits'),
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.credits_label.pack(anchor="w")
        
        # Status and controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e")
        
        # Set status based on current connection state
        status_text = self.lang.get('connected') if self.connected else self.lang.get('disconnected')
        status_color = "green" if self.connected else "red"
        
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text=f"● {status_text}",
            font=("Segoe UI", 14),
            text_color=status_color
        )
        self.status_label.pack(pady=2)
        
        # Mini mode button
        self.mini_mode_btn = ctk.CTkButton(
            controls_frame,
            text="📱 Mini",
            command=self.toggle_mini_mode,
            width=80,
            height=32,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.mini_mode_btn.pack(pady=2)
        
        # Language button
        self.lang_button = ctk.CTkButton(
            controls_frame,
            text=self.lang.get('russian') if self.lang.is_russian else self.lang.get('english'),
            command=self.toggle_language,
            width=80,
            height=32,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['info'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.lang_button.pack(pady=2)
        
        # Theme button
        theme_text = self.lang.get('dark') if self.current_theme == "dark" else self.lang.get('light')
        self.theme_button = ctk.CTkButton(
            controls_frame,
            text=theme_text,
            command=self.toggle_theme,
            width=80,
            height=32,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['warning'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.theme_button.pack(pady=2)
        
    def create_stats(self):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Current misses
        miss_card = ctk.CTkFrame(stats_frame)
        miss_card.grid(row=0, column=0, sticky="ew", padx=5)
        
        self.miss_title = ctk.CTkLabel(
            miss_card,
            text=self.lang.get('current_misses'),
            font=(f"Segoe UI", self.font_size)
        )
        self.miss_title.pack(pady=(15, 5))
        
        self.miss_value = ctk.CTkLabel(
            miss_card,
            text="0",
            font=(f"Segoe UI", 48, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['primary']
        )
        self.miss_value.pack(pady=(0, 15))
        
        # Hit100 count
        hit100_card = ctk.CTkFrame(stats_frame)
        hit100_card.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.hit100_title = ctk.CTkLabel(
            hit100_card,
            text=self.lang.get('current_hit100'),
            font=(f"Segoe UI", self.font_size)
        )
        self.hit100_title.pack(pady=(15, 5))
        
        self.hit100_value = ctk.CTkLabel(
            hit100_card,
            text="0",
            font=(f"Segoe UI", 48, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
        )
        self.hit100_value.pack(pady=(0, 15))
        
        # Hit50 count
        hit50_card = ctk.CTkFrame(stats_frame)
        hit50_card.grid(row=0, column=2, sticky="ew", padx=5)
        
        self.hit50_title = ctk.CTkLabel(
            hit50_card,
            text=self.lang.get('current_hit50'),
            font=(f"Segoe UI", self.font_size)
        )
        self.hit50_title.pack(pady=(15, 5))
        
        self.hit50_value = ctk.CTkLabel(
            hit50_card,
            text="0",
            font=(f"Segoe UI", 48, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['warning']
        )
        self.hit50_value.pack(pady=(0, 15))
        
        # Threshold
        threshold_card = ctk.CTkFrame(stats_frame)
        threshold_card.grid(row=0, column=2, sticky="ew", padx=5)
        
        self.threshold_title = ctk.CTkLabel(
            threshold_card,
            text=self.lang.get('threshold'),
            font=(f"Segoe UI", self.font_size)
        )
        self.threshold_title.pack(pady=(15, 5))
        
        self.threshold_value = ctk.CTkLabel(
            threshold_card,
            text=str(self.miss_threshold),
            font=(f"Segoe UI", 48, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['warning']
        )
        self.threshold_value.pack(pady=(0, 15))
        
        # Total restarts
        restart_card = ctk.CTkFrame(stats_frame)
        restart_card.grid(row=0, column=3, sticky="ew", padx=5)
        
        self.restart_title = ctk.CTkLabel(
            restart_card,
            text=self.lang.get('total_restarts'),
            font=(f"Segoe UI", self.font_size)
        )
        self.restart_title.pack(pady=(15, 5))
        
        self.restart_value = ctk.CTkLabel(
            restart_card,
            text=str(self.total_restarts),
            font=(f"Segoe UI", 48, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['success']
        )
        self.restart_value.pack(pady=(0, 15))
        
    def create_tosu_data_display(self):
        """Create additional TOSU data display"""
        tosu_frame = ctk.CTkFrame(self.main_frame)
        tosu_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        tosu_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            tosu_frame,
            text="🎮 Live Game Data",
            font=(f"Segoe UI", self.font_size + 2, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=5, pady=(10, 15))
        
        # Accuracy
        if self.show_accuracy:
            acc_frame = ctk.CTkFrame(tosu_frame)
            acc_frame.grid(row=1, column=0, sticky="ew", padx=2, pady=5)
            ctk.CTkLabel(acc_frame, text="Accuracy", font=(f"Segoe UI", self.font_size-2)).pack(pady=2)
            self.accuracy_label = ctk.CTkLabel(
                acc_frame, 
                text="0.00%", 
                font=(f"Segoe UI", self.font_size+2, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
            )
            self.accuracy_label.pack(pady=2)
        
        # Combo
        if self.show_combo:
            combo_frame = ctk.CTkFrame(tosu_frame)
            combo_frame.grid(row=1, column=1, sticky="ew", padx=2, pady=5)
            ctk.CTkLabel(combo_frame, text="Combo", font=(f"Segoe UI", self.font_size-2)).pack(pady=2)
            self.combo_label = ctk.CTkLabel(
                combo_frame, 
                text="0x", 
                font=(f"Segoe UI", self.font_size+2, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['success']
            )
            self.combo_label.pack(pady=2)
        
        # PP
        if self.show_pp:
            pp_frame = ctk.CTkFrame(tosu_frame)
            pp_frame.grid(row=1, column=2, sticky="ew", padx=2, pady=5)
            ctk.CTkLabel(pp_frame, text="PP", font=(f"Segoe UI", self.font_size-2)).pack(pady=2)
            self.pp_label = ctk.CTkLabel(
                pp_frame, 
                text="0", 
                font=(f"Segoe UI", self.font_size+2, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['primary']
            )
            self.pp_label.pack(pady=2)
        
        # HP
        if self.show_hp:
            hp_frame = ctk.CTkFrame(tosu_frame)
            hp_frame.grid(row=1, column=3, sticky="ew", padx=2, pady=5)
            ctk.CTkLabel(hp_frame, text="HP", font=(f"Segoe UI", self.font_size-2)).pack(pady=2)
            self.hp_label = ctk.CTkLabel(
                hp_frame, 
                text="0.0%", 
                font=(f"Segoe UI", self.font_size+2, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['danger']
            )
            self.hp_label.pack(pady=2)
        
        # Progress
        if self.show_progress:
            progress_frame = ctk.CTkFrame(tosu_frame)
            progress_frame.grid(row=1, column=4, sticky="ew", padx=2, pady=5)
            ctk.CTkLabel(progress_frame, text="Progress", font=(f"Segoe UI", self.font_size-2)).pack(pady=2)
            self.progress_label = ctk.CTkLabel(
                progress_frame, 
                text="0.0%", 
                font=(f"Segoe UI", self.font_size+2, "bold"),
                text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
            )
            self.progress_label.pack(pady=2)
        
    def create_map_display(self):
        """Create current map display"""
        map_frame = ctk.CTkFrame(self.main_frame)
        map_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        self.map_title = ctk.CTkLabel(
            map_frame,
            text=self.lang.get('current_map'),
            font=(f"Segoe UI", self.font_size + 2, "bold")
        )
        self.map_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.map_label = ctk.CTkLabel(
            map_frame,
            text=self.lang.get('not_playing'),
            font=(f"Segoe UI", self.font_size),
            text_color="gray"
        )
        self.map_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Map stats (CS, AR, OD, HP)
        stats_container = ctk.CTkFrame(map_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=15, pady=(0, 10))
        
        self.map_stats_label = ctk.CTkLabel(
            stats_container,
            text="",
            font=(f"Segoe UI", self.font_size - 2),
            text_color="gray"
        )
        self.map_stats_label.pack(anchor="w")
        
    def create_threshold_setting(self):
        """Create threshold setting"""
        threshold_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        threshold_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        threshold_frame.grid_columnconfigure(1, weight=1)
        
        self.threshold_label = ctk.CTkLabel(
            threshold_frame,
            text=self.lang.get('miss_threshold'),
            font=(f"Segoe UI", self.font_size)
        )
        self.threshold_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.threshold_entry = ctk.CTkEntry(
            threshold_frame,
            width=100,
            placeholder_text="5"
        )
        self.threshold_entry.grid(row=0, column=1, padx=5, sticky="w")
        self.threshold_entry.insert(0, str(self.miss_threshold))
        
        self.threshold_apply_btn = ctk.CTkButton(
            threshold_frame,
            text=self.lang.get('apply'),
            command=self.apply_threshold,
            width=100,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.threshold_apply_btn.grid(row=0, column=2, padx=5, sticky="w")
        
        # Hit thresholds section
        hit_section_label = ctk.CTkLabel(
            threshold_frame,
            text=f"🎯 {self.lang.get('hit_thresholds_section')}",
            font=(f"Segoe UI", self.font_size, "bold")
        )
        hit_section_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(15, 5))
        
        # Hit 100 threshold enable checkbox
        self.hit100_threshold_var = ctk.BooleanVar(value=self.hit100_threshold_enabled)
        hit100_threshold_cb = ctk.CTkCheckBox(
            threshold_frame,
            text=self.lang.get('enable_hit100_threshold'),
            variable=self.hit100_threshold_var,
            command=self.toggle_hit100_threshold,
            font=(f"Segoe UI", self.font_size - 1)
        )
        hit100_threshold_cb.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Hit 100 threshold field
        hit100_label = ctk.CTkLabel(
            threshold_frame,
            text=self.lang.get('hit100_threshold_label'),
            font=(f"Segoe UI", self.font_size - 1)
        )
        hit100_label.grid(row=3, column=0, padx=(20, 10), sticky="w")
        
        self.hit100_entry = ctk.CTkEntry(
            threshold_frame,
            width=80,
            placeholder_text="10"
        )
        self.hit100_entry.grid(row=3, column=1, padx=5, sticky="w")
        self.hit100_entry.insert(0, str(self.hit100_threshold))
        
        # Apply button for hit 100 threshold
        self.hit100_apply_btn = ctk.CTkButton(
            threshold_frame,
            text=self.lang.get('apply'),
            command=self.apply_hit100_threshold,
            width=100,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['warning'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.hit100_apply_btn.grid(row=3, column=2, padx=5, sticky="w")
        
        # Hit 50 threshold enable checkbox
        self.hit50_threshold_var = ctk.BooleanVar(value=self.hit50_threshold_enabled)
        hit50_threshold_cb = ctk.CTkCheckBox(
            threshold_frame,
            text=self.lang.get('enable_hit50_threshold'),
            variable=self.hit50_threshold_var,
            command=self.toggle_hit50_threshold,
            font=(f"Segoe UI", self.font_size - 1)
        )
        hit50_threshold_cb.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 10))
        
        # Hit 50 threshold field
        hit50_label = ctk.CTkLabel(
            threshold_frame,
            text=self.lang.get('hit50_threshold_label'),
            font=(f"Segoe UI", self.font_size - 1)
        )
        hit50_label.grid(row=5, column=0, padx=(20, 10), sticky="w")
        
        self.hit50_entry = ctk.CTkEntry(
            threshold_frame,
            width=80,
            placeholder_text="5"
        )
        self.hit50_entry.grid(row=5, column=1, padx=5, sticky="w")
        self.hit50_entry.insert(0, str(self.hit50_threshold))
        
        # Apply button for hit 50 threshold
        self.hit50_apply_btn = ctk.CTkButton(
            threshold_frame,
            text=self.lang.get('apply'),
            command=self.apply_hit50_threshold,
            width=100,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['warning'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.hit50_apply_btn.grid(row=5, column=2, padx=5, pady=(0, 15), sticky="w")
        
    def create_key_settings(self):
        """Create key settings section"""
        key_frame = ctk.CTkFrame(self.main_frame)
        key_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        key_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        self.key_settings_title = ctk.CTkLabel(
            key_frame,
            text=self.lang.get('key_settings'),
            font=(f"Segoe UI", self.font_size + 4, "bold")
        )
        self.key_settings_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 15))
        
        # Restart key
        self.restart_key_label = ctk.CTkLabel(
            key_frame,
            text=self.lang.get('restart_key'),
            font=(f"Segoe UI", self.font_size)
        )
        self.restart_key_label.grid(row=1, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.restart_key_display = ctk.CTkLabel(
            key_frame,
            text=self.restart_key_name,
            font=(f"Segoe UI", self.font_size, "bold"),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['primary']
        )
        self.restart_key_display.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.capture_key_btn = ctk.CTkButton(
            key_frame,
            text=self.lang.get('capture_key'),
            command=self.start_key_capture,
            width=150,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['warning'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.capture_key_btn.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Hold duration
        self.hold_duration_label = ctk.CTkLabel(
            key_frame,
            text=self.lang.get('hold_duration'),
            font=(f"Segoe UI", self.font_size)
        )
        self.hold_duration_label.grid(row=2, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.hold_duration_entry = ctk.CTkEntry(
            key_frame,
            width=100,
            placeholder_text="1.5"
        )
        self.hold_duration_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.hold_duration_entry.insert(0, str(self.hold_duration))
        
        self.hold_apply_btn = ctk.CTkButton(
            key_frame,
            text=self.lang.get('apply'),
            command=self.apply_key_settings,
            width=100,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.hold_apply_btn.grid(row=2, column=2, padx=5, pady=(5, 15), sticky="w")
        
    def create_cooldown_setting(self):
        """Create cooldown setting"""
        cooldown_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cooldown_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        cooldown_frame.grid_columnconfigure(1, weight=1)
        
        self.cooldown_label = ctk.CTkLabel(
            cooldown_frame,
            text=self.lang.get('cooldown_duration'),
            font=(f"Segoe UI", self.font_size)
        )
        self.cooldown_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.cooldown_entry = ctk.CTkEntry(
            cooldown_frame,
            width=100,
            placeholder_text="10.0"
        )
        self.cooldown_entry.grid(row=0, column=1, padx=5, sticky="w")
        self.cooldown_entry.insert(0, str(self.cooldown_duration))
        
        self.cooldown_apply_btn = ctk.CTkButton(
            cooldown_frame,
            text=self.lang.get('apply'),
            command=self.apply_cooldown,
            width=100,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        self.cooldown_apply_btn.grid(row=0, column=2, padx=5, sticky="w")
        
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=7, column=0, sticky="ew", pady=(0, 20))
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text=self.lang.get('start_monitoring'),
            command=self.start_monitoring,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['success'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button'],
            height=40,
            font=(f"Segoe UI", self.font_size, "bold")
        )
        self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text=self.lang.get('stop_monitoring'),
            command=self.stop_monitoring,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['danger'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button'],
            height=40,
            font=(f"Segoe UI", self.font_size, "bold")
        )
        self.stop_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.clear_btn = ctk.CTkButton(
            button_frame,
            text=self.lang.get('clear_log'),
            command=self.clear_log,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['primary'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button'],
            height=40,
            font=(f"Segoe UI", self.font_size, "bold")
        )
        self.clear_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
    def create_statistics_section(self):
        """Create statistics section with graphs"""
        stats_section = ctk.CTkFrame(self.main_frame)
        stats_section.grid(row=8, column=0, sticky="ew", pady=(0, 20))
        stats_section.grid_columnconfigure(1, weight=1)
        
        # Title
        stats_title = ctk.CTkLabel(
            stats_section,
            text=self.lang.get('statistics'),
            font=(f"Segoe UI", self.font_size + 4, "bold")
        )
        stats_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 15))
        
        # Averages display
        avg_frame = ctk.CTkFrame(stats_section, fg_color="transparent")
        avg_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=5)
        avg_frame.grid_columnconfigure((0, 1), weight=1)
        
        averages = self.stats.get_miss_averages()
        
        session_avg_label = ctk.CTkLabel(
            avg_frame,
            text=self.lang.get('session_avg').format(averages['session']),
            font=(f"Segoe UI", self.font_size),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['info']
        )
        session_avg_label.grid(row=0, column=0, sticky="w")
        
        alltime_avg_label = ctk.CTkLabel(
            avg_frame,
            text=self.lang.get('alltime_avg').format(averages['all_time']),
            font=(f"Segoe UI", self.font_size),
            text_color=ColorSchemes.SCHEMES[self.color_scheme]['warning']
        )
        alltime_avg_label.grid(row=0, column=1, sticky="w")
        
        # Export buttons
        export_frame = ctk.CTkFrame(stats_section, fg_color="transparent")
        export_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=15, pady=5)
        
        csv_btn = ctk.CTkButton(
            export_frame,
            text=self.lang.get('export_csv'),
            command=self.export_csv,
            width=120,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['success'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        csv_btn.pack(side="left", padx=5)
        
        json_btn = ctk.CTkButton(
            export_frame,
            text=self.lang.get('export_json'),
            command=self.export_json,
            width=120,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['info'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        json_btn.pack(side="left", padx=5)
        
        # Graph placeholder (simplified for now)
        graph_frame = ctk.CTkFrame(stats_section)
        graph_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=15, pady=(5, 15))
        
        graph_label = ctk.CTkLabel(
            graph_frame,
            text=f"📊 {self.lang.get('miss_graph')} - {len(self.stats.session_stats['misses'])} points",
            font=(f"Segoe UI", self.font_size)
        )
        graph_label.pack(pady=20)
        
    def create_customization_panel(self):
        """Create customization panel"""
        custom_frame = ctk.CTkFrame(self.main_frame)
        custom_frame.grid(row=9, column=0, sticky="ew", pady=(0, 20))
        custom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Title
        custom_title = ctk.CTkLabel(
            custom_frame,
            text=self.lang.get('customize'),
            font=(f"Segoe UI", self.font_size + 4, "bold")
        )
        custom_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 15))
        
        # Always on top
        self.always_on_top_var = ctk.BooleanVar(value=self.always_on_top)
        always_on_top_cb = ctk.CTkCheckBox(
            custom_frame,
            text=self.lang.get('always_on_top'),
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top
        )
        always_on_top_cb.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        # Transparency slider
        transparency_label = ctk.CTkLabel(
            custom_frame,
            text=self.lang.get('transparency'),
            font=(f"Segoe UI", self.font_size)
        )
        transparency_label.grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        self.transparency_slider = ctk.CTkSlider(
            custom_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=7,
            command=self.change_transparency
        )
        self.transparency_slider.set(self.transparency)
        self.transparency_slider.grid(row=1, column=2, sticky="ew", padx=15, pady=5)
        
        # Color scheme
        color_label = ctk.CTkLabel(
            custom_frame,
            text=self.lang.get('color_scheme'),
            font=(f"Segoe UI", self.font_size)
        )
        color_label.grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        # Color wheel palette
        color_wheel_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        color_wheel_frame.grid(row=2, column=1, columnspan=2, sticky="w", padx=15, pady=5)
        
        # Create color buttons in a circular arrangement
        colors = ColorSchemes.get_color_wheel_colors()
        self.color_buttons = {}
        
        # Arrange in 3 rows of 4 colors each
        for i, (display_name, scheme_name) in enumerate(colors):
            row = i // 4
            col = i % 4
            
            color_btn = ctk.CTkButton(
                color_wheel_frame,
                text=display_name.split(' ')[0],  # Just the emoji
                command=lambda s=scheme_name: self.change_color_scheme(s),
                width=35,
                height=35,
                fg_color=ColorSchemes.SCHEMES[scheme_name]['primary'],
                hover_color=ColorSchemes.SCHEMES[scheme_name]['button'],
                font=("Segoe UI", 16)
            )
            color_btn.grid(row=row, column=col, padx=2, pady=2)
            self.color_buttons[scheme_name] = color_btn
            
            # Highlight current scheme
            if scheme_name == self.color_scheme:
                color_btn.configure(border_width=3, border_color="white")
        
        # Font size
        font_label = ctk.CTkLabel(
            custom_frame,
            text=self.lang.get('font_size'),
            font=(f"Segoe UI", self.font_size)
        )
        font_label.grid(row=2, column=2, sticky="w", padx=15, pady=5)
        
        self.font_size_var = ctk.StringVar(value=str(self.font_size))
        font_menu = ctk.CTkOptionMenu(
            custom_frame,
            values=["10", "12", "14", "16", "18"],
            variable=self.font_size_var,
            command=self.change_font_size
        )
        font_menu.grid(row=2, column=3, sticky="w", padx=15, pady=5)
        
        # Import/Export settings
        import_btn = ctk.CTkButton(
            custom_frame,
            text=self.lang.get('import_settings'),
            command=self.import_settings,
            width=120,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['info'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        import_btn.grid(row=3, column=0, sticky="w", padx=15, pady=(5, 15))
        
        export_btn = ctk.CTkButton(
            custom_frame,
            text=self.lang.get('export_settings'),
            command=self.export_settings,
            width=120,
            fg_color=ColorSchemes.SCHEMES[self.color_scheme]['success'],
            hover_color=ColorSchemes.SCHEMES[self.color_scheme]['button']
        )
        export_btn.grid(row=3, column=1, sticky="w", padx=15, pady=(5, 15))
        
        # Hotkeys info
        hotkeys_info = ctk.CTkLabel(
            custom_frame,
            text=f"{self.lang.get('hotkeys')}: {self.lang.get('hotkey_mute')}, {self.lang.get('hotkey_log')}, {self.lang.get('hotkey_threshold')}, {self.lang.get('hotkey_mini')}",
            font=(f"Segoe UI", self.font_size - 2),
            text_color="gray"
        )
        hotkeys_info.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(0, 15))
        
    def create_log(self):
        """Create activity log"""
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.grid(row=10, column=0, sticky="nsew", pady=(0, 10))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_title = ctk.CTkLabel(
            log_frame,
            text=self.lang.get('activity_log'),
            font=(f"Segoe UI", self.font_size + 2, "bold")
        )
        self.log_title.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=("Consolas", self.font_size - 1)
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
    def create_footer(self):
        """Create footer"""
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get('footer'),
            font=(f"Segoe UI", 10),
            text_color="gray"
        )
        self.footer_label.grid(row=11, column=0, pady=(0, 10))
        
    def toggle_mini_mode(self):
        """Toggle between mini and full mode"""
        self.mini_mode = not self.mini_mode
        
        # Store current position
        try:
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
        except:
            current_x = 100
            current_y = 100
        
        if not self.mini_mode:
            # Restore normal window
            try:
                # Remove click-through if enabled
                try:
                    import win32gui
                    import win32con
                    hwnd = self.root.winfo_id()
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    style &= ~(win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
                except:
                    pass
                
                # Destroy all widgets
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                # Reset window attributes
                self.root.overrideredirect(False)
                
                # Remove transparent color
                try:
                    self.root.attributes('-transparentcolor', '')
                except:
                    pass
                
                # Reset window size and position
                self.root.geometry(f"1000x800+{current_x}+{current_y}")
                self.root.resizable(True, True)
                self.root.minsize(700, 600)
                self.root.maxsize(2000, 1500)
                
                # Force update
                self.root.update_idletasks()
                self.root.update()
                
            except Exception as e:
                print(f"Error restoring window: {e}")
        else:
            # Entering mini mode
            try:
                # Destroy all widgets
                for widget in self.root.winfo_children():
                    widget.destroy()
                    
            except Exception as e:
                print(f"Error entering mini mode: {e}")
        
        # Recreate GUI
        try:
            self.create_gui()
            
            # Apply window properties after GUI is created
            if not self.mini_mode:
                self.root.after(100, self.apply_window_properties)
                # Force window to front
                self.root.after(200, lambda: self.root.lift())
                self.root.after(200, lambda: self.root.focus_force())
            
            # Update connection status
            self.root.after(300, self.update_connection_status)
            
        except Exception as e:
            print(f"Error creating GUI: {e}")
        
        # Log message
        try:
            if self.mini_mode:
                self.log_message("📱 Mini mode activated", "blue")
            else:
                self.log_message("🖥️ Normal mode activated", "blue")
        except:
            pass
            
        self.save_config()
        
    def toggle_click_through(self):
        """Toggle click-through mode in mini mode"""
        try:
            import win32gui
            import win32con
            hwnd = self.root.winfo_id()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            if style & win32con.WS_EX_TRANSPARENT:
                # Disable click-through (make interactive)
                style &= ~(win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
                if hasattr(self, 'click_through_btn'):
                    self.click_through_btn.configure(
                        text="👆 Interactive",
                        fg_color=ColorSchemes.SCHEMES[self.color_scheme]['success']
                    )
                self.log_message("👆 Interactive mode (can click)", "green")
            else:
                # Enable click-through (clicks pass through)
                style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
                if hasattr(self, 'click_through_btn'):
                    self.click_through_btn.configure(
                        text="👻 Click-Through",
                        fg_color=ColorSchemes.SCHEMES[self.color_scheme]['warning']
                    )
                self.log_message("👻 Click-through mode (clicks pass through)", "orange")
        except Exception as e:
            self.log_message(f"🖱️ Click-through toggle error: {e}", "red")
        
    def toggle_hit100_threshold(self):
        """Toggle 100-hit threshold feature"""
        self.hit100_threshold_enabled = self.hit100_threshold_var.get()
        if self.hit100_threshold_enabled:
            self.log_message(self.lang.get('hit100_threshold_enabled'), "blue")
        else:
            self.log_message(self.lang.get('hit100_threshold_disabled'), "blue")
        self.save_config()
        
    def apply_hit100_threshold(self):
        """Apply 100-hit threshold setting"""
        try:
            threshold = int(self.hit100_entry.get())
            
            if 1 <= threshold <= 100:
                self.hit100_threshold = threshold
                self.log_message(self.lang.get('hit100_threshold_applied').format(threshold), "green")
                self.save_config()
            else:
                self.log_message("✗ Threshold must be 1-100", "red")
        except ValueError:
            self.log_message("✗ Invalid threshold value", "red")
    
    def toggle_hit50_threshold(self):
        """Toggle 50-hit threshold feature"""
        self.hit50_threshold_enabled = self.hit50_threshold_var.get()
        if self.hit50_threshold_enabled:
            self.log_message(self.lang.get('hit50_threshold_enabled'), "blue")
        else:
            self.log_message(self.lang.get('hit50_threshold_disabled'), "blue")
        self.save_config()
        
    def apply_hit50_threshold(self):
        """Apply 50-hit threshold setting"""
        try:
            threshold = int(self.hit50_entry.get())
            
            if 1 <= threshold <= 100:
                self.hit50_threshold = threshold
                self.log_message(self.lang.get('hit50_threshold_applied').format(threshold), "green")
                self.save_config()
            else:
                self.log_message("✗ Threshold must be 1-100", "red")
        except ValueError:
            self.log_message("✗ Invalid threshold value", "red")
        
    def toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top = self.always_on_top_var.get()
        self.apply_window_properties()
        self.save_config()
        
    def change_transparency(self, value):
        """Change window transparency"""
        self.transparency = value
        self.apply_window_properties()
        self.save_config()
        
    def change_color_scheme(self, scheme):
        """Change color scheme"""
        self.color_scheme = scheme
        
        # Update color button highlights
        if hasattr(self, 'color_buttons'):
            for scheme_name, button in self.color_buttons.items():
                if scheme_name == self.color_scheme:
                    button.configure(border_width=3, border_color="white")
                else:
                    button.configure(border_width=0)
        
        self.create_gui()  # Recreate GUI with new colors
        self.update_connection_status()
        self.save_config()
        
    def change_font_size(self, size):
        """Change font size"""
        self.font_size = int(size)
        self.create_gui()  # Recreate GUI with new font size
        self.update_connection_status()
        self.save_config()
        
    def export_csv(self):
        """Export statistics to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.stats.export_csv(filename)
            self.log_message(f"📊 CSV exported: {filename}", "green")
            
    def export_json(self):
        """Export statistics to JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.stats.export_json(filename)
            self.log_message(f"📊 JSON exported: {filename}", "green")
            
    def import_settings(self):
        """Import settings from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.apply_imported_config(config)
                self.log_message(self.lang.get('settings_imported'), "green")
            except Exception as e:
                self.log_message(f"✗ Import error: {e}", "red")
                
    def export_settings(self):
        """Export settings to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                config = self.get_current_config()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log_message(self.lang.get('settings_exported'), "green")
            except Exception as e:
                self.log_message(f"✗ Export error: {e}", "red")        

    def apply_imported_config(self, config):
        """Apply imported configuration"""
        self.miss_threshold = config.get('miss_threshold', self.miss_threshold)
        self.hold_duration = config.get('hold_duration', self.hold_duration)
        self.cooldown_duration = config.get('cooldown_duration', self.cooldown_duration)
        self.color_scheme = config.get('color_scheme', self.color_scheme)
        self.font_size = config.get('font_size', self.font_size)
        self.always_on_top = config.get('always_on_top', self.always_on_top)
        self.transparency = config.get('transparency', self.transparency)
        self.show_accuracy = config.get('show_accuracy', self.show_accuracy)
        self.show_combo = config.get('show_combo', self.show_combo)
        self.show_pp = config.get('show_pp', self.show_pp)
        self.show_hp = config.get('show_hp', self.show_hp)
        self.show_progress = config.get('show_progress', self.show_progress)
        
        # Apply changes
        self.create_gui()
        self.update_connection_status()
        self.apply_window_properties()
        self.save_config()
        
    def get_current_config(self):
        """Get current configuration for export"""
        return {
            'miss_threshold': self.miss_threshold,
            'hold_duration': self.hold_duration,
            'cooldown_duration': self.cooldown_duration,
            'restart_key_name': self.restart_key_name,
            'restart_key': str(self.restart_key) if self.restart_key else None,
            'language': self.lang.current,
            'theme': self.current_theme,
            'color_scheme': self.color_scheme,
            'font_size': self.font_size,
            'always_on_top': self.always_on_top,
            'transparency': self.transparency,
            'mini_mode': self.mini_mode,
            'show_accuracy': self.show_accuracy,
            'show_combo': self.show_combo,
            'show_pp': self.show_pp,
            'show_hp': self.show_hp,
            'show_progress': self.show_progress,
            'hit100_threshold_enabled': self.hit100_threshold_enabled,
            'hit100_threshold': self.hit100_threshold,
            'hit50_threshold_enabled': self.hit50_threshold_enabled,
            'hit50_threshold': self.hit50_threshold
        }
        
    def update_language(self):
        """Update all text elements with current language"""
        # Recreate GUI to update all text
        self.create_gui()
        # Force update connection status after GUI recreation
        self.update_connection_status()
        
    def toggle_language(self):
        """Toggle language"""
        self.lang.toggle()
        self.update_language()
        self.log_message(self.lang.get('language_changed').format(
            self.lang.get('russian') if self.lang.is_russian else self.lang.get('english')
        ))
        self.save_config()
        
    def update_connection_status(self):
        """Update connection status display"""
        status_text = self.lang.get('connected') if self.connected else self.lang.get('disconnected')
        status_color = "green" if self.connected else "red"
        
        try:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.configure(
                    text=f"● {status_text}",
                    text_color=status_color
                )
        except:
            pass
        
        try:
            if hasattr(self, 'mini_status') and self.mini_status.winfo_exists():
                self.mini_status.configure(
                    text=f"● {status_text}",
                    text_color=status_color
                )
        except:
            pass
        
    def toggle_theme(self):
        """Toggle theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        self.update_language()
        self.log_message(self.lang.get('theme_changed').format(
            self.lang.get('dark') if self.current_theme == "dark" else self.lang.get('light')
        ))
        self.save_config()
        
    def apply_threshold(self):
        """Apply miss threshold"""
        try:
            threshold = int(self.threshold_entry.get())
            if 1 <= threshold <= 100:
                self.miss_threshold = threshold
                if hasattr(self, 'threshold_value'):
                    self.threshold_value.configure(text=str(threshold))
                if hasattr(self, 'mini_threshold_value'):
                    self.mini_threshold_value.configure(text=str(threshold))
                self.log_message(self.lang.get('threshold_set').format(threshold))
                self.save_config()
            else:
                self.log_message("✗ Threshold must be 1-100", "red")
        except ValueError:
            self.log_message("✗ Invalid threshold value", "red")
            
    def apply_key_settings(self):
        """Apply key settings"""
        try:
            duration = float(self.hold_duration_entry.get())
            if 0.1 <= duration <= 10.0:
                self.hold_duration = duration
                self.log_message(self.lang.get('settings_applied').format(
                    self.restart_key_name, duration
                ))
                self.save_config()
            else:
                self.log_message("✗ Duration must be 0.1-10.0", "red")
        except ValueError:
            self.log_message("✗ Invalid duration value", "red")
            
    def apply_cooldown(self):
        """Apply cooldown setting"""
        try:
            cooldown = float(self.cooldown_entry.get())
            if 0.1 <= cooldown <= 60.0:
                self.cooldown_duration = cooldown
                self.log_message(self.lang.get('cooldown_set').format(cooldown))
                self.save_config()
            else:
                self.log_message("✗ Cooldown must be 0.1-60.0", "red")
        except ValueError:
            self.log_message("✗ Invalid cooldown value", "red")
            
    def start_key_capture(self):
        """Start capturing key press"""
        if self.capturing_key:
            return
            
        self.capturing_key = True
        self.capture_key_btn.configure(text="...")
        
        def on_press(key):
            if self.capturing_key:
                self.restart_key = key
                try:
                    self.restart_key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '').upper()
                except:
                    self.restart_key_name = str(key).replace('Key.', '').upper()
                
                self.root.after(0, lambda: self.restart_key_display.configure(text=self.restart_key_name))
                self.root.after(0, lambda: self.capture_key_btn.configure(text=self.lang.get('capture_key')))
                self.root.after(0, lambda: self.log_message(self.lang.get('key_captured').format(self.restart_key_name)))
                self.root.after(0, self.save_config)
                
                self.capturing_key = False
                return False
                
        self.key_listener = Listener(on_press=on_press)
        self.key_listener.start()
        
    def start_monitoring(self):
        """Start monitoring"""
        if self.running:
            return
            
        # Warn if restart key not set, but still allow monitoring
        if not self.restart_key:
            self.log_message("⚠ Restart key not set - auto-restart disabled", "orange")
            
        self.running = True
        self.ws_thread = threading.Thread(target=self.websocket_worker, daemon=True)
        self.ws_thread.start()
        self.log_message(self.lang.get('monitoring_started'), "green")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.ws:
            self.ws.close()
        self.log_message(self.lang.get('monitoring_stopped'), "orange")
        
    def clear_log(self):
        """Clear activity log"""
        if hasattr(self, 'log_text'):
            self.log_text.delete("1.0", "end")
        self.log_message(self.lang.get('log_cleared'))
        
    def log_message(self, message, color=None):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert("end", log_entry)
            self.log_text.see("end")
        else:
            # Store in memory for mini mode display
            if not hasattr(self, 'mini_log_messages'):
                self.mini_log_messages = []
            self.mini_log_messages.append(log_entry.strip())
            # Keep only last 50 messages
            if len(self.mini_log_messages) > 50:
                self.mini_log_messages.pop(0)
        
    def is_osu_focused(self):
        """Check if osu! is the active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name() == "osu!.exe"
        except:
            return False
            
    def websocket_worker(self):
        """WebSocket worker thread"""
        while self.running:
            try:
                self.log_message(self.lang.get('connecting').format("ws://127.0.0.1:24050/websocket/v2"))
                self.ws = websocket.WebSocketApp(
                    "ws://127.0.0.1:24050/websocket/v2",
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                self.ws.run_forever()
            except Exception as e:
                self.log_message(self.lang.get('connection_error').format(str(e)), "red")
                time.sleep(5)
                
    def on_open(self, ws):
        """WebSocket opened"""
        self.connected = True
        self.root.after(0, self.update_connection_status)
        self.log_message(self.lang.get('connected_tosu'), "green")
        
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        self.connected = False
        self.root.after(0, self.update_connection_status)
        self.log_message(self.lang.get('disconnected_tosu'), "orange")
        
    def on_error(self, ws, error):
        """WebSocket error"""
        self.log_message(self.lang.get('websocket_error').format(str(error)), "red")
        
    def on_message(self, ws, message):
        """Handle WebSocket message"""
        try:
            data = json.loads(message)
            # Log first message to confirm data is received
            if not hasattr(self, '_first_message_logged'):
                self._first_message_logged = True
                self.log_message("✓ Receiving data from TOSU", "green")
            self.process_data(data)
        except Exception as e:
            self.log_message(f"✗ Error: {str(e)}", "red")
            
    def process_data(self, data):
        """Process TOSU data"""
        try:
            # Silently process data (no debug logs)
            
            # Get current map ID and info from beatmap data
            bm_data = data.get('beatmap', {})
            if not bm_data:
                return
            
            # Debug: log beatmap structure once
            if not hasattr(self, '_logged_beatmap'):
                self._logged_beatmap = True
                self.log_message(f"🗺️ Beatmap keys: {list(bm_data.keys())}", "blue")
                if 'metadata' in bm_data:
                    meta = bm_data['metadata']
                    self.log_message(f"✓ Metadata: {meta.get('artist')} - {meta.get('title')}", "green")
                
            map_id = bm_data.get('id', 0)
            
            # Update map display
            if map_id and map_id != 0:
                # Artist and title are directly in beatmap, not in metadata
                artist = bm_data.get('artist', '').strip()
                title = bm_data.get('title', '').strip()
                difficulty = bm_data.get('version', '').strip()  # 'version' is difficulty name
                
                # Get map stats
                stats = bm_data.get('stats', {})
                cs = stats.get('CS', 0)
                ar = stats.get('AR', 0)
                od = stats.get('OD', 0)
                hp = stats.get('HP', 0)
                
                # Only update if we have valid data
                if artist and title:
                    map_name = f"{artist} - {title}"
                    if difficulty:
                        map_name += f" [{difficulty}]"
                    
                    # Only update if changed
                    if self.current_map_name != map_name:
                        self.current_map_name = map_name
                        
                        if hasattr(self, 'map_label'):
                            self.root.after(0, lambda name=map_name: self.map_label.configure(text=name))
                        if hasattr(self, 'mini_map_label'):
                            self.root.after(0, lambda name=map_name: self.mini_map_label.configure(text=name))
                    
                    # Update map stats display
                    if cs or ar or od or hp:  # Only show if we have stats
                        stats_text = f"CS: {cs:.1f}  AR: {ar:.1f}  OD: {od:.1f}  HP: {hp:.1f}"
                        if hasattr(self, 'map_stats_label'):
                            self.root.after(0, lambda text=stats_text: self.map_stats_label.configure(text=text))
                elif self.current_map_name != "Unknown":
                    # No metadata but have map ID - show loading
                    self.current_map_name = "Loading..."
                    if hasattr(self, 'map_label'):
                        self.root.after(0, lambda: self.map_label.configure(text="Loading..."))
                    if hasattr(self, 'mini_map_label'):
                        self.root.after(0, lambda: self.mini_map_label.configure(text="Loading..."))
            else:
                # No map or invalid map ID - show "not playing"
                if self.current_map_name != self.lang.get('not_playing'):
                    self.current_map_name = self.lang.get('not_playing')
                    if hasattr(self, 'map_label'):
                        self.root.after(0, lambda: self.map_label.configure(text=self.lang.get('not_playing')))
                    if hasattr(self, 'mini_map_label'):
                        self.root.after(0, lambda: self.mini_map_label.configure(text=self.lang.get('not_playing')))
                    if hasattr(self, 'map_stats_label'):
                        self.root.after(0, lambda: self.map_stats_label.configure(text=""))
            
            # Check for new map
            if map_id != self.current_map_id and map_id is not None:
                self.current_map_id = map_id
                self.our_miss_count = 0
                self.last_tosu_misses = 0
                self.threshold_triggered = False
                self.current_hit100 = 0  # Reset hit100 tracking
                self.current_hit50 = 0  # Reset hit50 tracking
                
                # Update displays
                if hasattr(self, 'miss_value'):
                    self.root.after(0, lambda: self.miss_value.configure(text="0"))
                if hasattr(self, 'mini_miss_value'):
                    self.root.after(0, lambda: self.mini_miss_value.configure(text="0"))
                if hasattr(self, 'hit100_value'):
                    self.root.after(0, lambda: self.hit100_value.configure(text="0"))
                if hasattr(self, 'hit50_value'):
                    self.root.after(0, lambda: self.hit50_value.configure(text="0"))
                    
                self.stats.add_map_played()
                self.log_message(self.lang.get('new_map'), "blue")
                return
                
            # Get gameplay data (use 'play' key)
            gameplay_data = data.get('play', {})
            
            if not gameplay_data:
                return  # No gameplay data available
            
            hits_data = gameplay_data.get('hits', {})
            if not hits_data:
                return  # No hits data available
            
            # Try both integer and string keys for compatibility
            current_tosu_misses = hits_data.get(0, 0) if 0 in hits_data else hits_data.get('0', 0)
            
            # Get 100-hit data (try both int and string keys)
            current_hit100 = hits_data.get(100, 0) if 100 in hits_data else hits_data.get('100', 0)
            
            # Get 50-hit data (try both int and string keys)
            current_hit50 = hits_data.get(50, 0) if 50 in hits_data else hits_data.get('50', 0)
            
            # Additional TOSU data
            self.current_accuracy = gameplay_data.get('accuracy', 0.0)
            self.current_combo = gameplay_data.get('combo', {}).get('current', 0) if isinstance(gameplay_data.get('combo'), dict) else gameplay_data.get('combo', 0)
            self.current_pp = gameplay_data.get('pp', {}).get('current', 0.0) if isinstance(gameplay_data.get('pp'), dict) else gameplay_data.get('pp', 0.0)
            self.current_hp = gameplay_data.get('hp', {}).get('normal', 0.0) * 100 if isinstance(gameplay_data.get('hp'), dict) else gameplay_data.get('hp', 0.0) * 100
            
            # No score data needed - we only track hit100 count
            
            # Progress calculation (simplified)
            time_data = gameplay_data.get('time', {})
            current_time = time_data.get('current', 0)
            total_time = time_data.get('full', 1)
            self.current_progress = (current_time / total_time * 100) if total_time > 0 else 0
            
            # Update additional data displays
            self.update_tosu_displays()
            
            # Add gameplay data to statistics
            self.stats.add_gameplay_data(
                accuracy=self.current_accuracy,
                combo=self.current_combo,
                pp=self.current_pp,
                hp=self.current_hp
            )
            
            # Update miss count, hit100 and hit50 counts
            self.update_miss_count(current_tosu_misses, current_hit100, current_hit50)
            
        except Exception as e:
            self.log_message(self.lang.get('data_error').format(str(e)), "red")
            
    def update_tosu_displays(self):
        """Update additional TOSU data displays"""
        # Full mode updates
        if hasattr(self, 'accuracy_label') and self.show_accuracy:
            self.root.after(0, lambda: self.accuracy_label.configure(
                text=f"{self.current_accuracy:.2f}%"
            ))
            
        if hasattr(self, 'combo_label') and self.show_combo:
            self.root.after(0, lambda: self.combo_label.configure(
                text=f"{self.current_combo}x"
            ))
            
        if hasattr(self, 'pp_label') and self.show_pp:
            self.root.after(0, lambda: self.pp_label.configure(
                text=f"{self.current_pp:.0f}"
            ))
            
        if hasattr(self, 'hp_label') and self.show_hp:
            self.root.after(0, lambda: self.hp_label.configure(
                text=f"{self.current_hp:.1f}%"
            ))
            
        if hasattr(self, 'progress_label') and self.show_progress:
            self.root.after(0, lambda: self.progress_label.configure(
                text=f"{self.current_progress:.1f}%"
            ))
            
        # Mini mode updates
        if hasattr(self, 'mini_accuracy_label') and self.show_accuracy:
            self.root.after(0, lambda: self.mini_accuracy_label.configure(
                text=f"{self.current_accuracy:.2f}%"
            ))
            
        if hasattr(self, 'mini_combo_label') and self.show_combo:
            self.root.after(0, lambda: self.mini_combo_label.configure(
                text=f"{self.current_combo}x"
            ))
            
        if hasattr(self, 'mini_pp_label') and self.show_pp:
            self.root.after(0, lambda: self.mini_pp_label.configure(
                text=f"{self.current_pp:.0f}"
            ))
            
        if hasattr(self, 'mini_hp_label') and self.show_hp:
            self.root.after(0, lambda: self.mini_hp_label.configure(
                text=f"{self.current_hp:.1f}%"
            ))
            
        if hasattr(self, 'mini_progress_label') and self.show_progress:
            self.root.after(0, lambda: self.mini_progress_label.configure(
                text=f"{self.current_progress:.1f}%"
            ))
            
    def update_miss_count(self, current_tosu_misses, current_hit100, current_hit50):
        """Update miss count and check thresholds"""
        # Block during restart
        if self.is_restarting:
            return
            
        # Calculate new misses
        miss_diff = current_tosu_misses - self.last_tosu_misses
        
        # Update hit100 count
        hit100_diff = current_hit100 - self.current_hit100
        self.current_hit100 = current_hit100
        
        # Update hit100 display
        if hasattr(self, 'hit100_value'):
            self.root.after(0, lambda: self.hit100_value.configure(text=str(self.current_hit100)))
        
        # Log hit100 changes if threshold is enabled
        if self.hit100_threshold_enabled and hit100_diff > 0:
            if self.current_hit100 >= self.hit100_threshold:
                # Will be handled below
                pass
            elif self.current_hit100 == self.hit100_threshold - 1:
                self.log_message(f"⚠️ Hit 100: {self.current_hit100}/{self.hit100_threshold} (близко к порогу!)", "orange")
            else:
                self.log_message(f"📊 Hit 100: +{hit100_diff} (всего: {self.current_hit100}/{self.hit100_threshold})", "blue")
        
        # Update hit50 count
        hit50_diff = current_hit50 - self.current_hit50
        self.current_hit50 = current_hit50
        
        # Update hit50 display
        if hasattr(self, 'hit50_value'):
            self.root.after(0, lambda: self.hit50_value.configure(text=str(self.current_hit50)))
        
        # Log hit50 changes if threshold is enabled
        if self.hit50_threshold_enabled and hit50_diff > 0:
            if self.current_hit50 >= self.hit50_threshold:
                # Will be handled below
                pass
            elif self.current_hit50 == self.hit50_threshold - 1:
                self.log_message(f"⚠️ Hit 50: {self.current_hit50}/{self.hit50_threshold} (близко к порогу!)", "orange")
            else:
                self.log_message(f"📊 Hit 50: +{hit50_diff} (всего: {self.current_hit50}/{self.hit50_threshold})", "blue")
        
        # Check miss threshold
        miss_threshold_reached = False
        if miss_diff > 0:
            self.our_miss_count += miss_diff
            self.last_tosu_misses = current_tosu_misses
            
            # Add to statistics
            self.stats.add_miss(self.our_miss_count, self.current_map_name)
            
            # Update displays
            if hasattr(self, 'miss_value'):
                self.root.after(0, lambda: self.miss_value.configure(text=str(self.our_miss_count)))
            if hasattr(self, 'mini_miss_value'):
                self.root.after(0, lambda: self.mini_miss_value.configure(text=str(self.our_miss_count)))
            
            # Check if miss threshold is reached
            miss_threshold_reached = self.our_miss_count >= self.miss_threshold
            
            if miss_threshold_reached:
                self.log_message(self.lang.get('threshold_reached').format(
                    miss_diff, self.our_miss_count, self.miss_threshold
                ), "red")
            elif self.our_miss_count == self.miss_threshold - 1:
                self.log_message(self.lang.get('close_to_threshold').format(
                    miss_diff, self.our_miss_count, self.miss_threshold
                ), "orange")
            else:
                self.log_message(self.lang.get('miss_logged').format(
                    miss_diff, self.our_miss_count, self.miss_threshold
                ))
        
        # Check 100-hit threshold if enabled (always check, not just on misses)
        hit100_threshold_reached = False
        if self.hit100_threshold_enabled:
            if self.current_hit100 >= self.hit100_threshold and not self.threshold_triggered:
                hit100_threshold_reached = True
                self.log_message(self.lang.get('hit100_threshold_reached').format(
                    self.current_hit100, self.hit100_threshold
                ), "red")
        
        # Check 50-hit threshold if enabled
        hit50_threshold_reached = False
        if self.hit50_threshold_enabled:
            if self.current_hit50 >= self.hit50_threshold and not self.threshold_triggered:
                hit50_threshold_reached = True
                self.log_message(self.lang.get('hit50_threshold_reached').format(
                    self.current_hit50, self.hit50_threshold
                ), "red")
        
        # Trigger restart if any threshold is reached
        if (miss_threshold_reached or hit100_threshold_reached or hit50_threshold_reached) and not self.threshold_triggered:
            # Check cooldown
            time_since_restart = time.time() - self.last_restart_time
            if time_since_restart < self.cooldown_duration:
                remaining = self.cooldown_duration - time_since_restart
                self.log_message(self.lang.get('cooldown_active').format(remaining), "orange")
                return
                
            self.threshold_triggered = True
            self.trigger_restart()
                
    def trigger_restart(self):
        """Trigger map restart"""
        if self.is_restarting:
            return
        
        # Check if restart key is set
        if not self.restart_key:
            self.log_message("⚠ Cannot restart - restart key not set", "orange")
            return
            
        # Set flags immediately
        self.is_restarting = True
        self.last_restart_time = time.time()
        
        # Start restart in separate thread
        restart_thread = threading.Thread(target=self._do_restart, daemon=True)
        restart_thread.start()
        
    def _do_restart(self):
        """Perform the restart"""
        try:
            # Check if osu! is in focus
            if not self.is_osu_focused():
                self.log_message("⚠ osu! not in focus - skipping restart", "orange")
                self.is_restarting = False
                return
            
            self.log_message(self.lang.get('restarting'), "orange")
            self.log_message(self.lang.get('pressing_key').format(self.restart_key_name), "blue")
            
            # Press key
            self.keyboard.press(self.restart_key)
            time.sleep(self.hold_duration)
            self.keyboard.release(self.restart_key)
            
            self.log_message(self.lang.get('key_released'), "green")
            
            # Reset counters
            self.our_miss_count = 0
            self.last_tosu_misses = 0
            self.threshold_triggered = False
            self.total_restarts += 1
            
            # Add to statistics
            self.stats.add_restart()
            
            # Update displays
            if hasattr(self, 'miss_value'):
                self.root.after(0, lambda: self.miss_value.configure(text="0"))
            if hasattr(self, 'mini_miss_value'):
                self.root.after(0, lambda: self.mini_miss_value.configure(text="0"))
            if hasattr(self, 'hit100_value'):
                self.root.after(0, lambda: self.hit100_value.configure(text="0"))
            if hasattr(self, 'hit50_value'):
                self.root.after(0, lambda: self.hit50_value.configure(text="0"))
            if hasattr(self, 'restart_value'):
                self.root.after(0, lambda: self.restart_value.configure(text=str(self.total_restarts)))
            
            self.log_message(self.lang.get('counter_reset'), "green")
            
            # Wait for TOSU to update
            self.log_message(self.lang.get('waiting'), "blue")
            time.sleep(3)
            
            self.log_message(self.lang.get('ready'), "green")
            
        except Exception as e:
            self.log_message(self.lang.get('key_error').format(str(e)), "red")
        finally:
            self.is_restarting = False
            
    def save_config(self):
        """Save configuration"""
        config = self.get_current_config()
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            # Save statistics too
            self.stats.save_stats()
        except Exception as e:
            self.log_message(f"✗ Config save error: {e}", "red")
            
    def load_config(self):
        """Load configuration"""
        if not os.path.exists(CONFIG_FILE):
            return
            
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.miss_threshold = config.get('miss_threshold', 5)
            self.hold_duration = config.get('hold_duration', 1.5)
            self.cooldown_duration = config.get('cooldown_duration', 10.0)
            self.restart_key_name = config.get('restart_key_name', self.lang.get('not_set'))
            self.color_scheme = config.get('color_scheme', 'blue')
            self.font_size = config.get('font_size', 12)
            self.always_on_top = config.get('always_on_top', False)
            self.transparency = config.get('transparency', 1.0)
            self.mini_mode = config.get('mini_mode', False)
            self.show_accuracy = config.get('show_accuracy', True)
            self.show_combo = config.get('show_combo', True)
            self.show_pp = config.get('show_pp', True)
            self.show_hp = config.get('show_hp', True)
            self.show_progress = config.get('show_progress', True)
            self.hit100_threshold_enabled = config.get('hit100_threshold_enabled', False)
            self.hit100_threshold = config.get('hit100_threshold', 10)
            self.hit50_threshold_enabled = config.get('hit50_threshold_enabled', False)
            self.hit50_threshold = config.get('hit50_threshold', 5)
            
            # Restore key
            key_str = config.get('restart_key')
            if key_str and key_str != '*':  # Ignore invalid keys
                try:
                    if 'Key.' in key_str:
                        key_name = key_str.replace('Key.', '')
                        self.restart_key = getattr(Key, key_name, None)
                    elif len(key_str) == 1:
                        # Single character key
                        self.restart_key = key_str
                    # Otherwise keep default F2
                except:
                    pass  # Keep default F2
                    
            self.lang.current = config.get('language', 'ru')
            self.current_theme = config.get('theme', 'dark')
            ctk.set_appearance_mode(self.current_theme)
            
        except Exception as e:
            # Can't log here as GUI might not exist yet
            pass
            
    def run(self):
        """Run the application"""
        self.log_message("🚀 osu!helper v2.0 Enhanced Edition started!", "green")
        self.log_message(self.lang.get('config_loaded'), "blue")
        
        # Show hotkeys info
        self.log_message(f"⌨️ {self.lang.get('hotkeys')}: Ctrl+M, Ctrl+L, Ctrl+↑/↓, Ctrl+K", "blue")
        
        # Auto-connect to TOSU after 1 second
        self.root.after(1000, self.auto_connect_tosu)
        
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            if self.hotkeys:
                self.hotkeys.stop()
            if self.key_listener:
                self.key_listener.stop()
    
    def auto_connect_tosu(self):
        """Automatically connect to TOSU on startup"""
        if not self.running:
            self.log_message("🔄 Auto-connecting to TOSU...", "blue")
            self.start_monitoring()


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import customtkinter
        import websocket
        import matplotlib
        import pynput
        import psutil
        import win32gui
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install customtkinter websocket-client matplotlib pynput psutil pywin32")
        sys.exit(1)
    
    root = ctk.CTk()
    app = OsuHelper(root)
    app.run()
