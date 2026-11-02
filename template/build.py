#!/usr/bin/env python3
"""Единый скрипт сборки. Python 3, только стандартная библиотека.
Запуск из корня проекта:  python template/build.py [slug ...]
Берёт content/{slug}.json + photos/{slug}/ и пишет sites/{slug}/.
Пустое поле или пустой список -> блок скрывается. Ничего не подставляется."""
import csv, datetime, html, json, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "template"
STATUS_FILE = ROOT / "data" / "sites_status.json"
TOK = re.compile(r"\{\{(#if|#each|/if|/each) ?(\w*)\}\}")
VAR = re.compile(r"\{\{(\w+)\}\}")

THEMES = {
    # КЕМЕРОВО
    "kem-01": {
        "theme_name": "MotorsLab Dark Teal & Crimson Red",
        "theme_accent": "#ef4444",
        "theme_accent_dark": "#dc2626",
        "theme_accent_soft": "rgba(239, 68, 68, 0.14)",
        "theme_accent_border": "rgba(239, 68, 68, 0.45)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0f1a24",
        "theme_hero_grad": "linear-gradient(rgba(15,26,36,0.85),rgba(15,26,36,0.92))",
        "theme_bg": "#0f1a24",
        "theme_ink": "#e2e8f0",
        "theme_paper": "#162432",
        "theme_paper_subtle": "#132230",
        "theme_line": "#24384d",
        "theme_line_light": "rgba(255, 255, 255, 0.08)",
        "theme_steel": "#94a3b8",
        "theme_steel_light": "#64748b",
        "theme_headings": "#ffffff",
        "theme_text_body": "#e2e8f0",
        "theme_text_muted": "#94a3b8",
        "theme_card_border": "#24384d",
        "theme_price_color": "#ef4444",
        "theme_service_btn_bg": "#ef4444",
        "theme_service_btn_text": "#ffffff",
        "theme_service_btn_hover_bg": "#dc2626",
        "theme_service_btn_hover_text": "#ffffff",
        "theme_more_btn_bg": "#162432",
        "theme_more_btn_border": "#ef4444",
        "theme_more_btn_text": "#ef4444",
        "theme_more_btn_arrow": "#ef4444",
        "theme_more_btn_hover_bg": "rgba(239, 68, 68, 0.14)",
        "theme_more_btn_hover_text": "#ef4444",
        "theme_badge_color": "#ef4444",
        "theme_rating_color": "#ef4444",
        "theme_btn_arrow_color": "#ef4444",
        "theme_btn_secondary_hover_bg": "#162432",
        "theme_btn_secondary_hover_text": "#ef4444",
        "theme_bar_bg": "#ef4444",
        "theme_bar_text": "#ffffff",
    },
    "kem-02": {
        "theme_name": "Nordic Steel Teal",
        "theme_accent": "#0891b2",
        "theme_accent_dark": "#0e7490",
        "theme_accent_soft": "rgba(8, 145, 178, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0e181c",
        "theme_hero_grad": "linear-gradient(rgba(14,24,28,0.85),rgba(14,24,28,0.92))",
        "theme_bg": "#edf3f5",
    },
    "kem-03": {
        "theme_name": "Safari Bronze Ochre",
        "theme_accent": "#d97706",
        "theme_accent_dark": "#b45309",
        "theme_accent_soft": "rgba(217, 119, 6, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#1a140d",
        "theme_hero_grad": "linear-gradient(rgba(26,20,13,0.85),rgba(26,20,13,0.92))",
        "theme_bg": "#f7f3ee",
    },
    "kem-04": {
        "theme_name": "Pandora Ruby Tech",
        "theme_accent": "#e11d48",
        "theme_accent_dark": "#be123c",
        "theme_accent_soft": "rgba(225, 29, 72, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#1c0d12",
        "theme_hero_grad": "linear-gradient(rgba(28,13,18,0.85),rgba(28,13,18,0.92))",
        "theme_bg": "#f8f0f2",
    },
    "kem-05": {
        "theme_name": "Royal Blue Tech",
        "theme_accent": "#2563eb",
        "theme_accent_dark": "#1d4ed8",
        "theme_accent_soft": "rgba(37, 99, 235, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0c1527",
        "theme_hero_grad": "linear-gradient(rgba(12,21,39,0.85),rgba(12,21,39,0.92))",
        "theme_bg": "#eef3fa",
    },
    "kem-06": {
        "theme_name": "Exhaust Ember",
        "theme_accent": "#ea580c",
        "theme_accent_dark": "#c2410c",
        "theme_accent_soft": "rgba(234, 88, 12, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#19110b",
        "theme_hero_grad": "linear-gradient(rgba(25,17,11,0.85),rgba(25,17,11,0.92))",
        "theme_bg": "#f7f1ec",
    },
    "kem-07": {
        "theme_name": "Ast Amber Gold",
        "theme_accent": "#f59e0b",
        "theme_accent_dark": "#b45309",
        "theme_accent_soft": "rgba(245, 158, 11, 0.12)",
        "theme_accent_text": "#0f1a24",
        "theme_hero_ink": "#17150e",
        "theme_hero_grad": "linear-gradient(rgba(23,21,14,0.85),rgba(23,21,14,0.92))",
        "theme_bg": "#f6f3ed",
    },
    "kem-08": {
        "theme_name": "Club Navy Cyan",
        "theme_accent": "#0284c7",
        "theme_accent_dark": "#0369a1",
        "theme_accent_soft": "rgba(2, 132, 199, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#091527",
        "theme_hero_grad": "linear-gradient(rgba(9,21,39,0.85),rgba(9,21,39,0.92))",
        "theme_bg": "#edf4f9",
    },
    "kem-09": {
        "theme_name": "Wrap Neon Lime",
        "theme_accent": "#84cc16",
        "theme_accent_dark": "#65a30d",
        "theme_accent_soft": "rgba(132, 204, 22, 0.14)",
        "theme_accent_text": "#0c1906",
        "theme_hero_ink": "#11180d",
        "theme_hero_grad": "linear-gradient(rgba(17,24,13,0.85),rgba(17,24,13,0.92))",
        "theme_bg": "#f3f6ee",
    },
    "kem-10": {
        "theme_name": "Tun №1 Stealth Obsidian & Amber Gold",
        "theme_accent": "#ff9f1a",
        "theme_accent_dark": "#e08800",
        "theme_accent_soft": "rgba(255, 159, 26, 0.14)",
        "theme_accent_border": "rgba(255, 159, 26, 0.45)",
        "theme_accent_text": "#0a0b0e",
        "theme_hero_ink": "#07080a",
        "theme_hero_grad": "linear-gradient(rgba(7,8,10,0.80),rgba(7,8,10,0.92))",
        "theme_bg": "#0a0b0e",
        "theme_ink": "#e2e8f0",
        "theme_paper": "#12141a",
        "theme_paper_subtle": "#181a24",
        "theme_line": "#222634",
        "theme_line_light": "rgba(255, 255, 255, 0.08)",
        "theme_steel": "#94a3b8",
        "theme_steel_light": "#64748b",
        "theme_headings": "#ffffff",
        "theme_text_body": "#cbd5e1",
        "theme_text_muted": "#8b9bb0",
        "theme_card_border": "#222634",
        "theme_price_color": "#ff9f1a",
        "theme_service_btn_bg": "#ff9f1a",
        "theme_service_btn_text": "#0a0b0e",
        "theme_service_btn_hover_bg": "#e08800",
        "theme_service_btn_hover_text": "#0a0b0e",
        "theme_more_btn_bg": "#12141a",
        "theme_more_btn_border": "#ff9f1a",
        "theme_more_btn_text": "#ff9f1a",
        "theme_more_btn_arrow": "#ff9f1a",
        "theme_more_btn_hover_bg": "rgba(255, 159, 26, 0.14)",
        "theme_more_btn_hover_text": "#ff9f1a",
        "theme_badge_color": "#ff9f1a",
        "theme_rating_color": "#ff9f1a",
        "theme_btn_arrow_color": "#ff9f1a",
        "theme_btn_secondary_hover_bg": "#12141a",
        "theme_btn_secondary_hover_text": "#ff9f1a",
        "theme_bar_bg": "#ff9f1a",
        "theme_bar_text": "#0a0b0e",
        "hero_photo_file": "07.jpg",
    },
    "kem-12": {
        "theme_name": "Mint Teal Detailing",
        "theme_accent": "#0d9488",
        "theme_accent_dark": "#0f766e",
        "theme_accent_soft": "rgba(13, 148, 136, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0a1716",
        "theme_hero_grad": "linear-gradient(rgba(10,23,22,0.85),rgba(10,23,22,0.92))",
        "theme_bg": "#ecf5f4",
    },
    "kem-13": {
        "theme_name": "Gunmetal Graphite",
        "theme_accent": "#475569",
        "theme_accent_dark": "#334155",
        "theme_accent_soft": "rgba(71, 85, 105, 0.14)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0f172a",
        "theme_hero_grad": "linear-gradient(rgba(15,23,42,0.85),rgba(15,23,42,0.92))",
        "theme_bg": "#edf1f5",
    },
    "kem-14": {
        "theme_name": "Aspeed Racing Yellow",
        "theme_accent": "#eab308",
        "theme_accent_dark": "#ca8a04",
        "theme_accent_soft": "rgba(234, 179, 8, 0.14)",
        "theme_accent_text": "#16150f",
        "theme_hero_ink": "#17150c",
        "theme_hero_grad": "linear-gradient(rgba(23,21,12,0.85),rgba(23,21,12,0.92))",
        "theme_bg": "#f7f5ed",
    },
    "kem-15": {
        "theme_name": "BMW M Motorsport Blue",
        "theme_accent": "#1d4ed8",
        "theme_accent_dark": "#1e40af",
        "theme_accent_soft": "rgba(29, 78, 216, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0b1426",
        "theme_hero_grad": "linear-gradient(rgba(11,20,38,0.85),rgba(11,20,38,0.92))",
        "theme_bg": "#edf2fa",
    },
    "kem-16": {
        "theme_name": "Industrial Slate",
        "theme_accent": "#52525b",
        "theme_accent_dark": "#27272a",
        "theme_accent_soft": "rgba(82, 82, 91, 0.14)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#121215",
        "theme_hero_grad": "linear-gradient(rgba(18,18,21,0.85),rgba(18,18,21,0.92))",
        "theme_bg": "#edf0f2",
    },

    # ТОМСК
    "tom-01": {
        "theme_name": "Obsidian & Amber HUD",
        "theme_accent": "#f5a800",
        "theme_accent_dark": "#cc8400",
        "theme_accent_soft": "rgba(245, 168, 0, 0.14)",
        "theme_accent_text": "#0f1a24",
        "theme_hero_ink": "#0f1a24",
        "theme_hero_grad": "linear-gradient(rgba(15,26,36,0.85),rgba(15,26,36,0.92))",
        "theme_bg": "#edf1f4",
    },
    "tom-02": {
        "theme_name": "Siberian Racing Red",
        "theme_accent": "#dc2626",
        "theme_accent_dark": "#b91c1c",
        "theme_accent_soft": "rgba(220, 38, 38, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#1a0e0e",
        "theme_hero_grad": "linear-gradient(rgba(26,14,14,0.85),rgba(26,14,14,0.92))",
        "theme_bg": "#f8f0f0",
    },
    "tom-03": {
        "theme_name": "Honda Azure Sport",
        "theme_accent": "#0284c7",
        "theme_accent_dark": "#0369a1",
        "theme_accent_soft": "rgba(2, 132, 199, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#081624",
        "theme_hero_grad": "linear-gradient(rgba(8,22,36,0.85),rgba(8,22,36,0.92))",
        "theme_bg": "#ecf4f9",
    },
    "tom-04": {
        "theme_name": "Adamant Forest Emerald",
        "theme_accent": "#16a34a",
        "theme_accent_dark": "#15803d",
        "theme_accent_soft": "rgba(22, 163, 74, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#0c1810",
        "theme_hero_grad": "linear-gradient(rgba(12,24,16,0.85),rgba(12,24,16,0.92))",
        "theme_bg": "#eef5f0",
    },
    "tom-05": {
        "theme_name": "Deep Indigo Tech",
        "theme_accent": "#4f46e5",
        "theme_accent_dark": "#4338ca",
        "theme_accent_soft": "rgba(79, 70, 229, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#101229",
        "theme_hero_grad": "linear-gradient(rgba(16,18,41,0.85),rgba(16,18,41,0.92))",
        "theme_bg": "#f0f1fa",
    },
    "tom-06": {
        "theme_name": "AutoBox Lava Tangerine",
        "theme_accent": "#f97316",
        "theme_accent_dark": "#c2410c",
        "theme_accent_soft": "rgba(249, 115, 22, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#1a120c",
        "theme_hero_grad": "linear-gradient(rgba(26,18,12,0.85),rgba(26,18,12,0.92))",
        "theme_bg": "#f7f1ec",
    },
}

DEFAULT_THEME = {
    "theme_name": "Amber Gold",
    "theme_accent": "#f5a800",
    "theme_accent_dark": "#cc8400",
    "theme_accent_soft": "rgba(245, 168, 0, 0.12)",
    "theme_accent_border": "#f5a800",
    "theme_accent_text": "#0f1a24",
    "theme_hero_ink": "#0f1a24",
    "theme_hero_grad": "linear-gradient(rgba(15,26,36,0.80),rgba(15,26,36,0.88))",
    "theme_bg": "#edf1f4",
    "theme_ink": "#0f1a24",
    "theme_paper": "#ffffff",
    "theme_paper_subtle": "#f8fafb",
    "theme_line": "#c8d3dc",
    "theme_line_light": "#e3e9ef",
    "theme_steel": "#3c5468",
    "theme_steel_light": "#5a7388",
    "theme_headings": "#0f1a24",
    "theme_text_body": "#1e2c38",
    "theme_text_muted": "#5a7388",
    "theme_card_border": "#c8d3dc",
    "theme_price_color": "#cc8400",
    "theme_service_btn_bg": "#0f1a24",
    "theme_service_btn_text": "#ffffff",
    "theme_service_btn_hover_bg": "#cc8400",
    "theme_service_btn_hover_text": "#ffffff",
    "theme_more_btn_bg": "#ffffff",
    "theme_more_btn_border": "#c8d3dc",
    "theme_more_btn_text": "#0f1a24",
    "theme_more_btn_arrow": "#cc8400",
    "theme_more_btn_hover_bg": "#f8fafb",
    "theme_more_btn_hover_text": "#cc8400",
    "theme_badge_color": "#cc8400",
    "theme_rating_color": "#cc8400",
    "theme_btn_arrow_color": "#3c5468",
    "theme_btn_secondary_hover_bg": "#ffffff",
    "theme_btn_secondary_hover_text": "#cc8400",
    "theme_bar_bg": "#0f1a24",
    "theme_bar_text": "#ffffff",
}

SOCIALS_MAP = {
    # КЕМЕРОВО
    "kem-01": [
        {"name": "Telegram", "url": "https://t.me/+79069839530"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
        {"name": "Instagram", "url": "https://www.instagram.com/motorslab.kem?utm_source=qr"},
    ],
    "kem-02": [
        {"name": "WhatsApp", "url": "https://wa.me/79955132353"},
        {"name": "Telegram", "url": "https://t.me/+79955132353"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
    ],
    "kem-03": [
        {"name": "WhatsApp", "url": "https://wa.me/73842348515"},
    ],
    "kem-04": [
        {"name": "WhatsApp", "url": "https://wa.me/79618660403"},
    ],
    "kem-05": [
        {"name": "WhatsApp", "url": "https://wa.me/79235331664"},
        {"name": "Telegram", "url": "https://t.me/+79235331664"},
    ],
    "kem-06": [
        {"name": "WhatsApp", "url": "https://wa.me/79000528462"},
    ],
    "kem-07": [
        {"name": "WhatsApp", "url": "https://wa.me/79951640409"},
        {"name": "Telegram", "url": "https://t.me/+79951640409"},
    ],
    "kem-08": [
        {"name": "WhatsApp", "url": "https://wa.me/79059191199"},
        {"name": "Telegram", "url": "https://t.me/clubservice_vag"},
        {"name": "ВКонтакте", "url": "https://vk.com/clubservice_kmr"},
    ],
    "kem-09": [
        {"name": "WhatsApp", "url": "https://wa.me/79511660299"},
        {"name": "Telegram", "url": "https://t.me/Wrap_Force42"},
        {"name": "ВКонтакте", "url": "https://vk.com/wrap_force42"},
    ],
    "kem-10": [
        {"name": "Telegram", "url": "https://t.me/tun1channel"},
        {"name": "ВКонтакте", "url": "https://vk.com/tun1kem"},
        {"name": "Instagram", "url": "https://instagram.com/semenov.yus"},
        {"name": "Авито", "url": "https://www.avito.ru/brands/7d2aa740243d38f59357bb9b5784cc2f"},
    ],
    "kem-12": [
        {"name": "WhatsApp", "url": "https://wa.me/79029843322"},
        {"name": "Telegram", "url": "https://t.me/+79029843322"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
        {"name": "Max", "url": "https://max.ru"},
    ],
    "kem-13": [
        {"name": "WhatsApp", "url": "https://wa.me/79235670093"},
        {"name": "Telegram", "url": "https://t.me/+79235670093"},
    ],
    "kem-14": [
        {"name": "WhatsApp", "url": "https://wa.me/79049657797"},
    ],
    "kem-15": [
        {"name": "Telegram", "url": "https://t.me/+79627346664"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
        {"name": "Max", "url": "https://max.ru"},
    ],
    "kem-16": [
        {"name": "WhatsApp", "url": "https://wa.me/79039841858"},
        {"name": "Telegram", "url": "https://t.me/+79039841858"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
    ],

    # ТОМСК
    "tom-01": [
        {"name": "WhatsApp", "url": "https://wa.me/79138151819"},
        {"name": "ВКонтакте", "url": "https://vk.com/avtokatdelete"},
    ],
    "tom-02": [
        {"name": "Telegram", "url": "https://t.me/+79627774000"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
    ],
    "tom-03": [
        {"name": "WhatsApp", "url": "https://wa.me/79138410689"},
        {"name": "ВКонтакте", "url": "https://vk.com/ridesshonda"},
    ],
    "tom-04": [
        {"name": "WhatsApp", "url": "https://wa.me/79539130411"},
        {"name": "Telegram", "url": "https://t.me/+79539130411"},
        {"name": "Max", "url": "https://max.ru"},
    ],
    "tom-05": [
        {"name": "ВКонтакте", "url": "https://vk.com/ots70"},
        {"name": "Max", "url": "https://max.ru"},
    ],
    "tom-06": [
        {"name": "ВКонтакте", "url": "https://vk.com/id146152316"},
    ],
}


CLOSING_BANNERS = {
    # КЕМЕРОВО
    "kem-01": {
        "title_1": "РАСКРОЙ",
        "title_2": "ПОТЕНЦИАЛ",
        "text": "Позвоните, чтобы записаться на Stage-калибровку Revo или диагностику.",
    },
    "kem-02": {
        "title_1": "НЕ ОТКЛАДЫВАЙ",
        "title_2": "НА ЗАВТРА",
        "text": "Позвоните, чтобы записаться на ТО или диагностику авто.",
    },
    "kem-03": {
        "title_1": "МОТОР",
        "title_2": "ТРЕБУЕТ ДЕЛА",
        "text": "Позвоните, чтобы проконсультироваться с мастером или записаться.",
    },
    "kem-04": {
        "title_1": "ЗАЩИТА",
        "title_2": "И ДИНАМИКА",
        "text": "Позвоните, чтобы подобрать сигнализацию или записаться на чип.",
    },
    "kem-05": {
        "title_1": "МАШИНА",
        "title_2": "НЕ ЖДЁТ",
        "text": "Позвоните, чтобы записаться на ремонт ДВС или диагностику.",
    },
    "kem-06": {
        "title_1": "ТИШИНА",
        "title_2": "И МОЩНОСТЬ",
        "text": "Позвоните, чтобы записаться на ремонт выхлопа или прошивку.",
    },
    "kem-07": {
        "title_1": "ОШИБКИ",
        "title_2": "НЕ ПРОЙДУТ САМИ",
        "text": "Позвоните Дмитрию, чтобы продиагностировать автоэлектрику.",
    },
    "kem-08": {
        "title_1": "КАЧЕСТВО",
        "title_2": "БЕЗ ПЕРЕПЛАТ",
        "text": "Позвоните, чтобы записаться на обслуживание или чип-тюнинг.",
    },
    "kem-09": {
        "title_1": "СТИЛЬ",
        "title_2": "И СКОРОСТЬ",
        "text": "Позвоните, чтобы забронировать время в студии Wrap Force.",
    },
    "kem-10": {
        "title_1": "МОМЕНТАЛЬНЫЙ",
        "title_2": "ОТКЛИК",
        "text": "Позвоните, чтобы записаться на чип-тюнинг или выхлоп.",
    },
    "kem-12": {
        "title_1": "БЕЗУПРЕЧНЫЙ",
        "title_2": "РЕЗУЛЬТАТ",
        "text": "Позвоните, чтобы записаться на детейлинг или тюнинг.",
    },
    "kem-13": {
        "title_1": "ВСЁ ДЛЯ АВТО",
        "title_2": "В ОДНОМ МЕСТЕ",
        "text": "Позвоните, чтобы уточнить наличие деталей или записаться.",
    },
    "kem-14": {
        "title_1": "ХАРАКТЕР",
        "title_2": "ТВОЕГО АВТО",
        "text": "Позвоните, чтобы обсудить индивидуальные доработки.",
    },
    "kem-15": {
        "title_1": "ЭКСПЕРТНЫЙ",
        "title_2": "ПОДХОД К BMW",
        "text": "Позвоните, чтобы записаться в профильный центр BMW.",
    },
    "kem-16": {
        "title_1": "ИНДИВИДУАЛЬНЫЙ",
        "title_2": "ПОДХОД",
        "text": "Позвоните, чтобы забронировать удобное время по звонку.",
    },

    # ТОМСК
    "tom-01": {
        "title_1": "МАШИНА",
        "title_2": "НЕ ЖДЁТ",
        "text": "Позвоните, чтобы записаться на бесплатную диагностику выхлопа за 0 ₽ или уточнить стоимость.",
    },
    "tom-02": {
        "title_1": "СВОБОДНЫЙ",
        "title_2": "ВЫДОХ МОТОРА",
        "text": "Позвоните, чтобы записаться на тюнинг выхлопа или чип.",
    },
    "tom-03": {
        "title_1": "ЯПОНСКАЯ",
        "title_2": "ТОЧНОСТЬ",
        "text": "Позвоните, чтобы записать вашу Honda/Acura к специалистам.",
    },
    "tom-04": {
        "title_1": "РЕМОНТ",
        "title_2": "БЕЗ ЗАДЕРЖЕК",
        "text": "Позвоните, чтобы записаться на диагностику или прошивку.",
    },
    "tom-05": {
        "title_1": "ЧЕСТНЫЙ",
        "title_2": "АВТОСЕРВИС",
        "text": "Позвоните, чтобы записаться в сервис с рейтингом 5.0.",
    },
    "tom-06": {
        "title_1": "КОМФОРТ",
        "title_2": "И ДИНАМИКА",
        "text": "Позвоните, чтобы записаться в тюнинг-бокс AutoBox.",
    },
}


def parse(tpl):
    """Шаблон -> дерево; блоки if/each могут вкладываться друг в друга."""
    root = []
    stack = [root]
    pos = 0
    for m in TOK.finditer(tpl):
        stack[-1].append(tpl[pos:m.start()])
        pos = m.end()
        tag, key = m.groups()
        if tag[0] == "#":
            node = (tag[1:], key, [])
            stack[-1].append(node)
            stack.append(node[2])
        else:
            stack.pop()
    stack[-1].append(tpl[pos:])
    return root


def render(nodes, ctx):
    out = []
    for n in nodes:
        if isinstance(n, str):
            def _repl(m):
                k = m.group(1)
                val = ctx.get(k)
                s = "" if val is None else str(val)
                if k.endswith("_html") or k.endswith("_raw"):
                    return s
                return html.escape(s, quote=True)
            out.append(VAR.sub(_repl, n))
            continue
        kind, key, body = n
        val = ctx.get(key)
        if kind == "if":
            if val:
                out.append(render(body, ctx))
        else:
            for i in val or []:
                out.append(render(body, {**ctx, **(i if isinstance(i, dict) else {"this": i})}))
    return "".join(out)


def load_statuses():
    """Загружает словарь статусов сайтов из data/sites_status.json"""
    if not STATUS_FILE.exists():
        statuses = {}
        for p in sorted((ROOT / "data" / "raw").glob("*.csv")):
            statuses[p.stem] = {"status": "active"}
        save_statuses(statuses)
        return statuses
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_statuses(statuses):
    """Сохраняет словарь статусов в data/sites_status.json"""
    STATUS_FILE.write_text(json.dumps(statuses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(slug):
    statuses = load_statuses()
    slug_status_info = statuses.get(slug, {"status": "active"})
    is_hidden = (slug_status_info.get("status") == "hidden")

    out = ROOT / "sites" / slug

    if is_hidden:
        raw_csv = ROOT / "data" / "raw" / f"{slug}.csv"
        name = slug
        city = ""
        if raw_csv.exists():
            try:
                line = raw_csv.read_text(encoding="utf-8").splitlines()[1]
                parts = line.split(";")
                city = parts[2].strip()
                name = parts[3].strip()
            except Exception:
                pass

        ctx = {
            "slug": slug,
            "name": name,
            "city": city,
            "reason": slug_status_info.get("reason", "По обращению представителя компании"),
            "updated_at": slug_status_info.get("updated_at", "")
        }

        deactivated_tpl = (TPL / "deactivated.html").read_text(encoding="utf-8")
        rendered_deactivated = render(parse(deactivated_tpl), ctx)

        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(rendered_deactivated, encoding="utf-8")
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        (out / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", encoding="utf-8")
        print(f"OK [HIDDEN] {slug} (страница-заглушка сгенерирована, фото удалены)")
        return

    data = json.loads((ROOT / "content" / f"{slug}.json").read_text(encoding="utf-8"))
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    
    phone_raw = re.split(r"[,|;]", data.get("phone") or "")[0].strip()
    digits = re.sub(r"\D", "", phone_raw)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    data["phone_href"] = ("+" + digits) if digits else ""
    data["phone_primary"] = phone_raw or data.get("phone", "")
    data["contacts"] = any(data.get(k) for k in ("address", "hours", "phone"))

    # Обработка услуг: первые 3 открыты, остальные скрываются классом is-more-service
    services = [s for s in data.get("services") or [] if s.get("title")]
    has_more = len(services) > 3
    more_count = len(services) - 3 if has_more else 0
    for idx, s in enumerate(services):
        s["phone_href"] = data.get("phone_href", "")
        if has_more and idx >= 3:
            s["is_more_service"] = True
        else:
            s["is_more_service"] = False

    data["services"] = services
    data["has_more_services"] = has_more
    data["more_count"] = more_count

    # Уникальная тема оформления
    raw_theme = THEMES.get(slug, DEFAULT_THEME)
    theme = {**DEFAULT_THEME}
    accent = raw_theme.get("theme_accent", DEFAULT_THEME["theme_accent"])
    accent_dark = raw_theme.get("theme_accent_dark", DEFAULT_THEME["theme_accent_dark"])
    hero_ink = raw_theme.get("theme_hero_ink", DEFAULT_THEME["theme_hero_ink"])
    theme["theme_accent_border"] = accent
    theme["theme_price_color"] = accent_dark
    theme["theme_service_btn_bg"] = hero_ink
    theme["theme_service_btn_hover_bg"] = accent_dark
    theme["theme_more_btn_arrow"] = accent_dark
    theme["theme_more_btn_hover_text"] = accent_dark
    theme["theme_badge_color"] = accent_dark
    theme["theme_rating_color"] = accent_dark
    theme["theme_btn_secondary_hover_text"] = accent_dark
    theme["theme_bar_bg"] = hero_ink
    theme.update(raw_theme)
    data.update(theme)

    # Вспомогательные поля для карты и ссылок на маршрут
    addr = f"{data.get('city', '')} {data.get('address', '')}".strip()
    data["map_query"] = urllib.parse.quote(addr)
    data["map_url"] = f"https://yandex.ru/map-widget/v1/?text={data['map_query']}&z=16" if addr else ""
    data["yandex_route_url"] = f"https://yandex.ru/maps/?rtext=~{data['map_query']}&rtt=auto" if addr else ""

    # Соцсети и мессенджеры
    data["socials"] = SOCIALS_MAP.get(slug, [])

    # Финальный призыв к действию (табличка по референсу)
    banner = CLOSING_BANNERS.get(slug, {})
    data["closing_title_1"] = banner.get("title_1", "")
    data["closing_title_2"] = banner.get("title_2", "")
    data["closing_subtitle"] = banner.get("text", "")

    # Сохраняем флагманский эталон tom-01, если он уже существует или есть в резервной копии
    custom_index = None
    custom_css = None
    if slug == "tom-01":
        tpl_custom_idx = TPL / "custom" / "tom-01" / "index.html"
        tpl_custom_css = TPL / "custom" / "tom-01" / "style.css"
        if tpl_custom_idx.exists():
            custom_index = tpl_custom_idx.read_text(encoding="utf-8")
        if tpl_custom_css.exists():
            custom_css = tpl_custom_css.read_text(encoding="utf-8")

        idx_file = out / "index.html"
        css_file = out / "style.css"
        if idx_file.exists():
            content = idx_file.read_text(encoding="utf-8")
            if "tom01-inline-css" in content and len(content) > 20000:
                custom_index = content
                (TPL / "custom" / "tom-01").mkdir(parents=True, exist_ok=True)
                tpl_custom_idx.write_text(content, encoding="utf-8")
        if css_file.exists():
            content_css = css_file.read_text(encoding="utf-8")
            if len(content_css) > 5000:
                custom_css = content_css
                (TPL / "custom" / "tom-01").mkdir(parents=True, exist_ok=True)
                tpl_custom_css.write_text(content_css, encoding="utf-8")

    shutil.rmtree(out, ignore_errors=True)
    (out / "img").mkdir(parents=True)
    photos_dir = ROOT / "photos" / slug
    photos = sorted(photos_dir.glob("*.[jp][pn]g"))[:8] if photos_dir.exists() else []
    data["photos"] = []
    for p in photos:
        shutil.copy(p, out / "img" / p.name)
        data["photos"].append({"src": f"img/{p.name}"})
    hero_photo_file = raw_theme.get("hero_photo_file")
    if hero_photo_file and (photos_dir / hero_photo_file).exists():
        dest_hero = out / "img" / hero_photo_file
        if not dest_hero.exists():
            shutil.copy(photos_dir / hero_photo_file, dest_hero)
        data["hero_photo"] = f"img/{hero_photo_file}"
    elif photos:
        data["hero_photo"] = f"img/{photos[0].name}"
    else:
        fallback_hero = TPL / "assets" / f"hero-business-{slug}.jpg"
        if fallback_hero.exists():
            shutil.copy(fallback_hero, out / "img" / "hero-business.jpg")
            data["hero_photo"] = "img/hero-business.jpg"

    if slug == "kem-10":
        data["brand_title_html"] = '<span class="brand-plate"><span class="plate-tu">TU</span><span class="plate-n">N</span><span class="plate-num"><span class="plate-deg">o</span>1</span></span>'
        data["has_default_title"] = False
    else:
        data["brand_title_html"] = ""
        data["has_default_title"] = True

    rendered_html = render(parse((TPL / "index.html").read_text(encoding="utf-8")), data)

    if slug == "tom-01" and custom_index:
        # Сохраняем флагманский дизайн index.html и его style.css
        (out / "index.html").write_text(custom_index, encoding="utf-8")
        if custom_css:
            (out / "style.css").write_text(custom_css, encoding="utf-8")
        else:
            shutil.copy(TPL / "style.css", out / "style.css")
        # Шаблонную версию сохраняем в standard.html со стилем standard.css
        std_html = rendered_html.replace('href="style.css?v=20261101_v9"', 'href="standard.css"')
        (out / "standard.html").write_text(std_html, encoding="utf-8")
        shutil.copy(TPL / "style.css", out / "standard.css")
    else:
        (out / "index.html").write_text(rendered_html, encoding="utf-8")
        # Синхронизируем вычисленный :root со style.css сайта
        m_root = re.search(r"(:root\s*\{[\s\S]*?\})", rendered_html)
        if m_root:
            rendered_root = m_root.group(1)
            base_css = (TPL / "style.css").read_text(encoding="utf-8")
            out_css = re.sub(r":root\s*\{[\s\S]*?\}", lambda _: rendered_root, base_css, count=1)
            (out / "style.css").write_text(out_css, encoding="utf-8")
        else:
            shutil.copy(TPL / "style.css", out / "style.css")

    # запрет индексации: robots.txt + заголовок для Netlify/Cloudflare Pages
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", encoding="utf-8")
    print(f"OK {slug} ({theme['theme_name']})")


def build_catalog():
    """Генерирует сводный каталог сайтов sites/index.html с фильтрами, статусами и переключателями (✓/✗)"""
    statuses = load_statuses()
    raw_dir = ROOT / "data" / "raw"
    raw_files = sorted(raw_dir.glob("*.csv"))

    kem_items = []
    tom_items = []

    total_active = 0
    total_hidden = 0
    kem_active = 0
    tom_active = 0
    hot_leads = 0

    for rf in raw_files:
        slug = rf.stem
        try:
            line = rf.read_text(encoding="utf-8").splitlines()[1]
            parts = line.split(";")
        except Exception:
            continue

        city = parts[2].strip()
        name = parts[3].strip()
        address = parts[5].strip()
        phone = parts[6].strip()
        site_status_raw = parts[8].strip()
        rating = parts[10].strip()
        reviews_count = parts[11].strip()

        status_info = statuses.get(slug, {"status": "active"})
        is_hidden = (status_info.get("status") == "hidden")
        reason = status_info.get("reason", "По обращению представителя компании")

        is_kem = "кемерово" in city.lower() or slug.startswith("kem")
        city_key = "kem" if is_kem else "tom"

        if is_hidden:
            total_hidden += 1
        else:
            total_active += 1
            if is_kem:
                kem_active += 1
            else:
                tom_active += 1
            if site_status_raw.lower() in ("нет", "нет сайта"):
                hot_leads += 1

        theme = THEMES.get(slug, DEFAULT_THEME)
        theme_name = theme.get("theme_name", "Amber Gold")
        theme_accent = theme.get("theme_accent", "#f5a800")

        item = {
            "slug": slug,
            "city": city,
            "city_key": city_key,
            "name": name,
            "address": address,
            "phone": phone,
            "site_status_raw": site_status_raw,
            "rating": rating,
            "reviews_count": reviews_count,
            "is_hidden": is_hidden,
            "reason": reason,
            "theme_name": theme_name,
            "theme_accent": theme_accent
        }

        if is_kem:
            kem_items.append(item)
        else:
            tom_items.append(item)

    total_count = len(kem_items) + len(tom_items)

    def render_card(it):
        slug = it["slug"]
        name = html.escape(it["name"])
        address = html.escape(it["address"])
        phone = html.escape(it["phone"])
        accent = it["theme_accent"]
        theme_name = html.escape(it["theme_name"])
        city_key = it["city_key"]
        is_hidden = it["is_hidden"]

        st_raw = it["site_status_raw"].lower()
        if st_raw in ("нет", "нет сайта"):
            badge_class = "badge-red"
            badge_text = "Нет сайта"
        elif "не работает" in st_raw:
            badge_class = "badge-yellow"
            badge_text = "не работает"
        elif "микросайт" in st_raw:
            badge_class = "badge-yellow"
            badge_text = "микросайт 2gis.biz"
        elif "taplink" in st_raw:
            badge_class = "badge-yellow"
            badge_text = "только taplink"
        else:
            badge_class = "badge-green"
            badge_text = "есть сайт"

        featured_class = " featured-site-card" if slug == "tom-01" else ""
        top_leader_badge = ""
        if slug == "tom-01":
            top_leader_badge = '<span class="badge" style="background:#f5a623;color:#000;font-weight:800;margin-bottom:8px;display:inline-block;">★ ТОП-ЛИДЕР (5.0★ • 367 отзывов)</span> '

        rating_str = f"{it['rating']}★ ({it['reviews_count']})" if it["rating"] else ""

        checked_attr = "" if is_hidden else "checked"
        hidden_card_class = " is-card-hidden" if is_hidden else ""
        initial_status = "hidden" if is_hidden else "active"

        return f"""
        <div class="site-card{featured_class}{hidden_card_class}" data-slug="{slug}" data-city="{city_key}" data-status="{initial_status}" data-name="{name}">
            {top_leader_badge}<div class="site-card-header">
                <div>
                    <span class="badge {badge_class}">{badge_text}</span>
                    <span class="slug-tag">{slug}</span>
                </div>
                <div class="rating">{rating_str}</div>
            </div>

            <!-- Интерактивный блок переключателя (галочка ✓ / крестик ✗) -->
            <div class="card-toggle-wrap">
                <label class="toggle-status-box" title="Нажмите, чтобы включить (✓) или скрыть (✗) этот бизнес в каталоге">
                    <input type="checkbox" class="business-toggle" data-slug="{slug}" {checked_attr}>
                    <span class="toggle-indicator">
                        <span class="toggle-glyph toggle-glyph-check">✓</span>
                        <span class="toggle-glyph toggle-glyph-cross">✗</span>
                    </span>
                    <span class="toggle-label-wrap">
                        <span class="toggle-state-text state-active">✓ Сайт активен (показывается)</span>
                        <span class="toggle-state-text state-hidden">✗ Сайт скрыт (отключён)</span>
                    </span>
                </label>
            </div>

            <div class="card-hidden-banner">
                <span class="hidden-banner-icon">✗</span>
                <span class="hidden-banner-text">Сайт скрыт (нажмите галочку выше, чтобы вернуть)</span>
            </div>

            <div class="theme-badge" style="background: {accent}1a; color: {accent}; border: 1px solid {accent}44;">
                <span class="theme-dot" style="background: {accent};"></span> {theme_name}
            </div>
            <h3 class="site-title">{name}</h3>
            <p class="site-address">{address}</p>
            <p class="site-phone">{phone}</p>
            <div class="site-actions">
                <a href="{slug}/index.html" class="btn btn-primary btn-open-site" target="_blank">Открыть премиум-сайт →</a>
            </div>
        </div>"""

    kem_cards_html = "".join(render_card(it) for it in kem_items)
    tom_cards_html = "".join(render_card(it) for it in tom_items)

    default_statuses_dict = {
        it["slug"]: ("hidden" if it["is_hidden"] else "active")
        for it in (kem_items + tom_items)
    }
    default_statuses_json = json.dumps(default_statuses_dict, ensure_ascii=False)

    catalog_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive">
    <title>Каталог демо-сайтов чип-тюнинга | Кемерово и Томск</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --border: #334155;
            --badge-red-bg: #450a0a;
            --badge-red-text: #f87171;
            --badge-yellow-bg: #422006;
            --badge-yellow-text: #facc15;
            --badge-green-bg: #064e3b;
            --badge-green-text: #4ade80;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.5;
            padding: 24px 16px 110px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .disclaimer-banner {{
            background: #1e1b4b;
            border: 1px solid #4338ca;
            color: #c7d2fe;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 24px;
            text-align: center;
        }}
        header {{
            text-align: center;
            margin-bottom: 28px;
        }}
        header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }}
        header p {{
            color: var(--text-muted);
            font-size: 15px;
        }}
        .stats-bar {{
            display: flex;
            gap: 14px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0 28px;
        }}
        .stat-item {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
        }}
        .stat-item strong {{
            color: var(--primary);
        }}
        .stat-item-hidden {{
            border-color: rgba(239, 68, 68, 0.4);
            background: rgba(239, 68, 68, 0.1);
        }}
        .badge-hidden-count {{
            color: #f87171 !important;
        }}
        .tabs-filter {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 32px;
        }}
        .tab-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 600;
            padding: 8px 18px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .tab-btn:hover {{
            color: var(--text);
            border-color: var(--primary);
        }}
        .tab-btn.active {{
            background: var(--primary);
            color: #0f172a;
            border-color: var(--primary);
        }}
        .tab-btn-hidden {{
            border-color: rgba(239, 68, 68, 0.45);
            color: #f87171;
        }}
        .tab-btn-hidden:hover {{
            border-color: #ef4444;
            color: #fca5a5;
        }}
        .tab-btn-hidden.active {{
            background: #ef4444;
            color: #ffffff;
            border-color: #ef4444;
        }}
        .city-section {{
            margin-bottom: 40px;
        }}
        .city-title {{
            font-size: 22px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .city-count {{
            font-size: 14px;
            color: var(--text-muted);
            font-weight: normal;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }}
        .site-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            transition: transform 0.15s, border-color 0.15s, opacity 0.2s, background 0.2s;
            position: relative;
        }}
        .site-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
        }}
        .featured-site-card {{
            border: 2px solid #f5a623 !important;
            background: linear-gradient(180deg, #1b212f 0%, #0e1117 100%) !important;
            box-shadow: 0 4px 20px rgba(245, 166, 35, 0.15);
        }}
        .site-card.is-card-hidden {{
            border-color: rgba(239, 68, 68, 0.35);
            background: #111827;
            opacity: 0.65;
        }}
        .site-card.is-card-hidden:hover {{
            opacity: 0.92;
            border-color: rgba(239, 68, 68, 0.6);
        }}
        .site-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        .badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .badge-red {{ background: var(--badge-red-bg); color: var(--badge-red-text); }}
        .badge-yellow {{ background: var(--badge-yellow-bg); color: var(--badge-yellow-text); }}
        .badge-green {{ background: var(--badge-green-bg); color: var(--badge-green-text); }}
        .badge-gray {{
            background: #334155;
            color: #cbd5e1;
            border: 1px solid #475569;
        }}
        .slug-tag {{
            font-size: 11px;
            color: var(--text-muted);
            margin-left: 6px;
            font-family: monospace;
        }}
        .rating {{
            font-size: 13px;
            color: #facc15;
            font-weight: bold;
        }}

        /* Интерактивный переключатель статуса на карточке (галочка ✓ / крестик ✗) */
        .card-toggle-wrap {{
            margin-bottom: 12px;
        }}
        .toggle-status-box {{
            display: flex;
            align-items: center;
            gap: 12px;
            min-height: 44px;
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
            transition: all 0.2s ease;
            background: rgba(16, 185, 129, 0.12);
            border: 1.5px solid rgba(16, 185, 129, 0.45);
        }}
        .toggle-status-box:hover {{
            filter: brightness(1.12);
        }}
        .toggle-status-box input.business-toggle {{
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
            pointer-events: none;
        }}
        .toggle-indicator {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 16px;
            flex-shrink: 0;
            transition: all 0.2s ease;
            background: #10b981;
            color: #ffffff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
        }}
        .toggle-glyph {{
            line-height: 1;
        }}
        .toggle-glyph-check {{
            display: inline-block;
        }}
        .toggle-glyph-cross {{
            display: none;
        }}
        .toggle-label-wrap {{
            font-size: 13px;
            font-weight: 600;
            line-height: 1.25;
        }}
        .toggle-state-text.state-active {{
            display: inline-block;
            color: #34d399;
        }}
        .toggle-state-text.state-hidden {{
            display: none;
            color: #f87171;
        }}

        /* Состояние переключателя, когда карточка скрыта */
        .site-card.is-card-hidden .toggle-status-box {{
            background: rgba(239, 68, 68, 0.14);
            border-color: rgba(239, 68, 68, 0.55);
        }}
        .site-card.is-card-hidden .toggle-indicator {{
            background: #ef4444;
        }}
        .site-card.is-card-hidden .toggle-glyph-check {{
            display: none;
        }}
        .site-card.is-card-hidden .toggle-glyph-cross {{
            display: inline-block;
        }}
        .site-card.is-card-hidden .toggle-state-text.state-active {{
            display: none;
        }}
        .site-card.is-card-hidden .toggle-state-text.state-hidden {{
            display: inline-block;
        }}

        .card-hidden-banner {{
            display: none;
            align-items: center;
            gap: 8px;
            background: rgba(239, 68, 68, 0.12);
            border: 1px dashed rgba(239, 68, 68, 0.45);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
            color: #fca5a5;
            margin-bottom: 12px;
        }}
        .site-card.is-card-hidden .card-hidden-banner {{
            display: flex;
        }}
        .hidden-banner-icon {{
            font-weight: bold;
            color: #ef4444;
        }}

        .theme-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
            width: fit-content;
        }}
        .theme-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }}
        .site-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #fff;
        }}
        .site-address {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        .site-phone {{
            font-size: 13px;
            color: #cbd5e1;
            font-family: monospace;
            margin-bottom: 14px;
        }}
        .site-actions {{
            margin-top: auto;
            display: flex;
            gap: 8px;
        }}
        .btn {{
            display: inline-block;
            text-decoration: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            flex: 1;
            transition: background 0.15s, border-color 0.15s;
        }}
        .btn-primary {{
            background: var(--primary);
            color: #0f172a;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
        }}
        .site-card.is-card-hidden .btn-primary {{
            background: #334155;
            color: #cbd5e1;
            border: 1px solid #475569;
        }}
        footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }}

        /* Компактный плавающий бар управления внизу страницы */
        .floating-bar {{
            position: fixed;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 24px);
            max-width: 880px;
            background: rgba(15, 23, 42, 0.94);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(56, 189, 248, 0.15);
            border-radius: 14px;
            padding: 8px 14px;
            z-index: 9999;
        }}
        .fb-content {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .fb-stats {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .fb-stat-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
        }}
        .fb-stat-check {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}
        .fb-stat-cross {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.35);
        }}
        .fb-filters {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .fb-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .fb-btn {{
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            min-height: 38px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .fb-btn:hover {{
            background: var(--surface-hover);
            border-color: var(--primary);
        }}
        .fb-filter.active {{
            background: var(--primary);
            color: #0f172a;
            border-color: var(--primary);
            font-weight: 700;
        }}
        .fb-btn-copy {{
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.35);
        }}
        .fb-btn-copy:hover {{
            background: rgba(56, 189, 248, 0.22);
        }}

        /* Toast уведомление */
        .toast-notification {{
            position: fixed;
            bottom: 84px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #0f172a;
            border: 1px solid #38bdf8;
            color: #f8fafc;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13.5px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
            opacity: 0;
            pointer-events: none;
            transition: all 0.25s ease;
            z-index: 10000;
            max-width: 90vw;
            text-align: center;
        }}
        .toast-notification.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}

        @media (max-width: 768px) {{
            body {{
                padding-bottom: 130px !important;
            }}
            .floating-bar {{
                bottom: 8px;
                padding: 8px 10px;
            }}
            .fb-content {{
                justify-content: center;
            }}
            .fb-stats, .fb-filters, .fb-actions {{
                justify-content: center;
            }}
            .fb-btn {{
                min-height: 42px;
                padding: 6px 10px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="disclaimer-banner">
            ⚠️ Демо-концепт для демонстрации возможностей. Не официальный каталог. Все данные взяты из открытых источников 2ГИС. Индексация запрещена (noindex).
        </div>
        
        <header>
            <h1>Чип-тюнинг сервисы: Демо-лендинги</h1>
            <p>Готовые мобильные сайты для автосервисов чип-тюнинга Кемерово и Томска</p>
            <div class="stats-bar">
                <div class="stat-item">Активных сайтов: <strong id="stat-active-count">{total_active}</strong></div>
                <div class="stat-item">Кемерово: <strong id="stat-kem-count">{kem_active}</strong></div>
                <div class="stat-item">Томск: <strong id="stat-tom-count">{tom_active}</strong></div>
                <div class="stat-item">Горячих лидов (без сайта): <strong>{hot_leads}</strong></div>
                <div class="stat-item stat-item-hidden" id="stat-hidden-box" style="{'display: none;' if total_hidden == 0 else ''}">
                    Скрыто (с крестиком): <strong class="badge-hidden-count" id="stat-hidden-count">{total_hidden}</strong>
                </div>
            </div>
        </header>

        <div class="tabs-filter">
            <button type="button" class="tab-btn active" data-filter="active">Все активные (✓ <span id="tab-active-cnt">{total_active}</span>)</button>
            <button type="button" class="tab-btn" data-filter="kem">Кемерово (<span id="tab-kem-cnt">{kem_active}</span>)</button>
            <button type="button" class="tab-btn" data-filter="tom">Томск (<span id="tab-tom-cnt">{tom_active}</span>)</button>
            <button type="button" class="tab-btn tab-btn-hidden" data-filter="hidden">Скрытые (✗ <span id="tab-hidden-cnt">{total_hidden}</span>)</button>
            <button type="button" class="tab-btn" data-filter="all">Все (<span id="tab-all-cnt">{total_count}</span>)</button>
        </div>

        <section class="city-section" id="section-kem">
            <h2 class="city-title">г. Кемерово <span class="city-count" id="count-kem">({kem_active} объектов)</span></h2>
            <div class="grid">
                {kem_cards_html}
            </div>
        </section>

        <section class="city-section" id="section-tom">
            <h2 class="city-title">г. Томск <span class="city-count" id="count-tom">({tom_active} объектов)</span></h2>
            <div class="grid">
                {tom_cards_html}
            </div>
        </section>

        <footer>
            Демо-концепт сайтов чип-тюнинга | Проект Antigravity | Собрано на чистом HTML/CSS без сторонних фреймворков
        </footer>
    </div>

    <!-- Плавающая панель управления со счётчиками и кнопками -->
    <div class="floating-bar" id="floating-bar">
        <div class="fb-content">
            <div class="fb-stats">
                <span class="fb-stat-pill fb-stat-check" title="Активных бизнесов с галочкой">
                    <span class="fb-badge-icon">✓</span> <span id="fb-active-cnt">{total_active}</span>
                </span>
                <span class="fb-stat-pill fb-stat-cross" title="Скрытых бизнесов с крестиком">
                    <span class="fb-badge-icon">✗</span> <span id="fb-hidden-cnt">{total_hidden}</span>
                </span>
            </div>
            <div class="fb-filters">
                <button type="button" class="fb-btn fb-filter active" data-fb-filter="active">✓ Активные</button>
                <button type="button" class="fb-btn fb-filter" data-fb-filter="all">Все</button>
                <button type="button" class="fb-btn fb-filter" data-fb-filter="hidden">✗ Скрытые</button>
            </div>
            <div class="fb-actions">
                <button type="button" class="fb-btn fb-action" id="fb-reset-btn" title="Восстановить все галочки по умолчанию">
                    <span class="btn-icon">🔄</span> <span class="btn-text">Сбросить</span>
                </button>
                <button type="button" class="fb-btn fb-action fb-btn-copy" id="fb-copy-btn" title="Скопировать список скрытых бизнесов в буфер обмена">
                    <span class="btn-icon">📋</span> <span class="btn-text">Скопировать скрытые</span>
                </button>
            </div>
        </div>
    </div>
    <div class="toast-notification" id="toast-notification"></div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {{
        const STORAGE_KEY = 'chip_tuning_sites_status';
        const defaultStatuses = {default_statuses_json};
        
        let savedStatuses = {{}};
        try {{
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) savedStatuses = JSON.parse(raw);
        }} catch (e) {{
            console.error('Failed to parse localStorage', e);
        }}

        const tabs = document.querySelectorAll('.tab-btn');
        const cards = document.querySelectorAll('.site-card');
        const secKem = document.getElementById('section-kem');
        const secTom = document.getElementById('section-tom');
        const countKem = document.getElementById('count-kem');
        const countTom = document.getElementById('count-tom');

        const statActive = document.getElementById('stat-active-count');
        const statHidden = document.getElementById('stat-hidden-count');
        const statKem = document.getElementById('stat-kem-count');
        const statTom = document.getElementById('stat-tom-count');
        const statHiddenBox = document.getElementById('stat-hidden-box');

        const tabActiveCnt = document.getElementById('tab-active-cnt');
        const tabKemCnt = document.getElementById('tab-kem-cnt');
        const tabTomCnt = document.getElementById('tab-tom-cnt');
        const tabHiddenCnt = document.getElementById('tab-hidden-cnt');
        const tabAllCnt = document.getElementById('tab-all-cnt');

        const fbActiveCnt = document.getElementById('fb-active-cnt');
        const fbHiddenCnt = document.getElementById('fb-hidden-cnt');
        const fbFilters = document.querySelectorAll('.fb-filter');
        const btnReset = document.getElementById('fb-reset-btn');
        const btnCopy = document.getElementById('fb-copy-btn');
        const toast = document.getElementById('toast-notification');

        let toastTimer = null;
        function showToast(message) {{
            if (!toast) return;
            toast.textContent = message;
            toast.classList.add('show');
            if (toastTimer) clearTimeout(toastTimer);
            toastTimer = setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2600);
        }}

        // Инициализация карточек из сохранённого состояния или значений по умолчанию
        cards.forEach(card => {{
            const slug = card.dataset.slug;
            const saved = savedStatuses[slug];
            let isActive = true;
            if (saved !== undefined) {{
                isActive = (saved === 'active' || saved === true);
            }} else if (defaultStatuses[slug] !== undefined) {{
                isActive = (defaultStatuses[slug] === 'active');
            }}

            const checkbox = card.querySelector('.business-toggle');
            if (checkbox) {{
                checkbox.checked = isActive;
            }}
            card.classList.toggle('is-card-hidden', !isActive);
            card.dataset.status = isActive ? 'active' : 'hidden';

            if (checkbox) {{
                checkbox.addEventListener('change', (e) => {{
                    const isChecked = e.target.checked;
                    const businessName = card.dataset.name || slug;

                    // Сохраняем в localStorage
                    savedStatuses[slug] = isChecked ? 'active' : 'hidden';
                    try {{
                        localStorage.setItem(STORAGE_KEY, JSON.stringify(savedStatuses));
                    }} catch (err) {{
                        console.error('LocalStorage error', err);
                    }}

                    card.classList.toggle('is-card-hidden', !isChecked);
                    card.dataset.status = isChecked ? 'active' : 'hidden';

                    updateAllCounts();

                    if (isChecked) {{
                        showToast(`✓ «${{businessName}}» включён в показ`);
                    }} else {{
                        showToast(`✗ «${{businessName}}» скрыт из каталога`);
                    }}
                }});
            }}
        }});

        let currentFilter = 'active';

        function applyFilter(filter) {{
            currentFilter = filter;

            tabs.forEach(t => t.classList.toggle('active', t.dataset.filter === filter));
            fbFilters.forEach(f => f.classList.toggle('active', f.dataset.fbFilter === filter));

            let visibleKem = 0;
            let visibleTom = 0;

            cards.forEach(card => {{
                const isHidden = card.dataset.status === 'hidden';
                const city = card.dataset.city;
                let show = false;

                if (filter === 'active') {{
                    show = !isHidden;
                }} else if (filter === 'kem') {{
                    show = !isHidden && (city === 'kem');
                }} else if (filter === 'tom') {{
                    show = !isHidden && (city === 'tom');
                }} else if (filter === 'hidden') {{
                    show = isHidden;
                }} else if (filter === 'all') {{
                    show = true;
                }}

                card.style.display = show ? '' : 'none';
                if (show) {{
                    if (city === 'kem') visibleKem++;
                    if (city === 'tom') visibleTom++;
                }}
            }});

            if (secKem) {{
                secKem.style.display = visibleKem > 0 ? '' : 'none';
                if (countKem) countKem.textContent = '(' + visibleKem + ' объектов)';
            }}
            if (secTom) {{
                secTom.style.display = visibleTom > 0 ? '' : 'none';
                if (countTom) countTom.textContent = '(' + visibleTom + ' объектов)';
            }}

            let emptyMsg = document.getElementById('catalog-empty-msg');
            if (!emptyMsg && secTom && secTom.parentNode) {{
                emptyMsg = document.createElement('div');
                emptyMsg.id = 'catalog-empty-msg';
                emptyMsg.style.cssText = 'text-align:center; padding:48px 16px; color:#94a3b8; font-size:16px; background:rgba(30,41,59,0.5); border-radius:12px; margin:24px 0; border:1px dashed #334155;';
                secTom.parentNode.insertBefore(emptyMsg, secTom.nextSibling);
            }}

            if (emptyMsg) {{
                if (visibleKem === 0 && visibleTom === 0) {{
                    emptyMsg.style.display = '';
                    if (filter === 'hidden') {{
                        emptyMsg.innerHTML = '<div style="font-size:32px; margin-bottom:12px;">🎉</div><strong>Скрытых сайтов нет!</strong><br><span style="font-size:14px; color:#64748b;">Все 21 сайт активны и отмечены галочкой ✓.</span>';
                    }} else {{
                        emptyMsg.innerHTML = '<div style="font-size:32px; margin-bottom:12px;">🔍</div><strong>Нет сайтов в выбранной категории</strong>';
                    }}
                }} else {{
                    emptyMsg.style.display = 'none';
                }}
            }}
        }}

        function updateAllCounts() {{
            let totalActive = 0;
            let totalHidden = 0;
            let kemActive = 0;
            let tomActive = 0;
            const totalAll = cards.length;

            cards.forEach(card => {{
                const isHidden = card.dataset.status === 'hidden';
                const city = card.dataset.city;
                if (isHidden) {{
                    totalHidden++;
                }} else {{
                    totalActive++;
                    if (city === 'kem') kemActive++;
                    if (city === 'tom') tomActive++;
                }}
            }});

            if (statActive) statActive.textContent = totalActive;
            if (statHidden) statHidden.textContent = totalHidden;
            if (statKem) statKem.textContent = kemActive;
            if (statTom) statTom.textContent = tomActive;
            if (statHiddenBox) {{
                statHiddenBox.style.display = totalHidden > 0 ? '' : 'none';
            }}

            if (tabActiveCnt) tabActiveCnt.textContent = totalActive;
            if (tabHiddenCnt) tabHiddenCnt.textContent = totalHidden;
            if (tabKemCnt) tabKemCnt.textContent = kemActive;
            if (tabTomCnt) tabTomCnt.textContent = tomActive;
            if (tabAllCnt) tabAllCnt.textContent = totalAll;

            if (fbActiveCnt) fbActiveCnt.textContent = totalActive;
            if (fbHiddenCnt) fbHiddenCnt.textContent = totalHidden;

            applyFilter(currentFilter);
        }}

        tabs.forEach(tab => {{
            tab.addEventListener('click', () => {{
                applyFilter(tab.dataset.filter);
            }});
        }});

        fbFilters.forEach(f => {{
            f.addEventListener('click', () => {{
                applyFilter(f.dataset.fbFilter);
            }});
        }});

        if (btnReset) {{
            btnReset.addEventListener('click', () => {{
                if (confirm('Восстановить все галочки по умолчанию (вернуть все сайты в показ)?')) {{
                    try {{
                        localStorage.removeItem(STORAGE_KEY);
                    }} catch (e) {{}}
                    savedStatuses = {{}};

                    cards.forEach(card => {{
                        const slug = card.dataset.slug;
                        const defStatus = defaultStatuses[slug] || 'active';
                        const isActive = (defStatus === 'active');
                        const checkbox = card.querySelector('.business-toggle');
                        if (checkbox) checkbox.checked = isActive;
                        card.classList.toggle('is-card-hidden', !isActive);
                        card.dataset.status = defStatus;
                    }});

                    updateAllCounts();
                    showToast('🔄 Все сайты возвращены в активный показ (✓)');
                }}
            }});
        }}

        if (btnCopy) {{
            btnCopy.addEventListener('click', () => {{
                const hiddenCards = Array.from(cards).filter(c => c.dataset.status === 'hidden');
                if (hiddenCards.length === 0) {{
                    showToast('✓ Все сайты активны — скрытых сайтов нет');
                    return;
                }}
                const slugs = hiddenCards.map(c => c.dataset.slug);
                const textToCopy = slugs.join(', ');

                const copyDone = () => {{
                    const spanText = btnCopy.querySelector('.btn-text');
                    const origText = spanText ? spanText.textContent : 'Скопировать скрытые';
                    if (spanText) spanText.textContent = `✓ Скопировано (${{slugs.length}})!`;
                    showToast(`📋 Скопировано (${{slugs.length}}): ${{textToCopy}}`);
                    setTimeout(() => {{
                        if (spanText) spanText.textContent = origText;
                    }}, 2200);
                }};

                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(textToCopy).then(copyDone).catch(() => {{
                        fallbackCopy(textToCopy, copyDone);
                    }});
                }} else {{
                    fallbackCopy(textToCopy, copyDone);
                }}
            }});
        }}

        function fallbackCopy(text, callback) {{
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try {{
                document.execCommand('copy');
                if (callback) callback();
            }} catch (e) {{
                showToast('Ошибка при копировании в буфер');
            }}
            document.body.removeChild(ta);
        }}

        // Первоначальный расчёт счётчиков и отображение
        updateAllCounts();
        applyFilter('active');
    }});
    </script>
</body>
</html>
"""
    (ROOT / "sites" / "index.html").write_text(catalog_html, encoding="utf-8")
    (ROOT / "sites" / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (ROOT / "sites" / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", encoding="utf-8")
    print(f"OK catalog sites/index.html (Активных: {total_active}, Скрытых: {total_hidden})")



def show_status():
    """Выводит в консоль аккуратную таблицу статусов всех 21 сайтов"""
    statuses = load_statuses()
    raw_files = sorted((ROOT / "data" / "raw").glob("*.csv"))

    col_slug = "Слаг"
    col_city = "Город"
    col_name = "Название"
    col_stat = "Статус"
    col_reas = "Причина / Детали"

    rows = []
    active_count = 0
    hidden_count = 0

    for rf in raw_files:
        slug = rf.stem
        info = statuses.get(slug, {"status": "active"})
        st = info.get("status", "active")
        if st == "hidden":
            hidden_count += 1
            st_display = "HIDDEN"
            reason = info.get("reason", "По обращению")
        else:
            active_count += 1
            st_display = "active"
            reason = "—"

        city = ""
        name = slug
        try:
            line = rf.read_text(encoding="utf-8").splitlines()[1]
            parts = line.split(";")
            city = parts[2].strip()
            name = parts[3].strip()
        except Exception:
            pass

        rows.append((slug, city, name, st_display, reason))

    w_slug = max(len(col_slug), max(len(r[0]) for r in rows))
    w_city = max(len(col_city), max(len(r[1]) for r in rows))
    w_name = max(len(col_name), max(len(r[2]) for r in rows))
    w_stat = max(len(col_stat), max(len(r[3]) for r in rows))
    w_reas = max(len(col_reas), max(len(r[4]) for r in rows))

    sep = f"+-{'-'*w_slug}-+-{'-'*w_city}-+-{'-'*w_name}-+-{'-'*w_stat}-+-{'-'*w_reas}-+"

    print("\nСтатусы сайтов чип-тюнинга:")
    print(sep)
    print(f"| {col_slug:<{w_slug}} | {col_city:<{w_city}} | {col_name:<{w_name}} | {col_stat:<{w_stat}} | {col_reas:<{w_reas}} |")
    print(sep)
    for r in rows:
        print(f"| {r[0]:<{w_slug}} | {r[1]:<{w_city}} | {r[2]:<{w_name}} | {r[3]:<{w_stat}} | {r[4]:<{w_reas}} |")
    print(sep)
    print(f"Всего: {len(rows)} | Активных: {active_count} | Скрытых: {hidden_count}\n")


def hide_site(slug, reason=None):
    """Переводит сайт в hidden, генерирует заглушку, обновляет каталог и zip"""
    statuses = load_statuses()
    raw_file = ROOT / "data" / "raw" / f"{slug}.csv"
    if slug not in statuses and not raw_file.exists():
        print(f"Ошибка: слаг '{slug}' не найден среди бизнесов проекта.")
        sys.exit(1)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reason_text = reason.strip() if reason and reason.strip() else "По обращению представителя компании"
    statuses[slug] = {
        "status": "hidden",
        "reason": reason_text,
        "updated_at": now_str
    }
    save_statuses(statuses)
    print(f"Сайт '{slug}' переведён в статус HIDDEN (причина: '{reason_text}')")
    build(slug)
    build_catalog()
    update_sites_zip()


def show_site(slug):
    """Восстанавливает сайт в active, генерирует полный сайт, обновляет каталог и zip"""
    statuses = load_statuses()
    raw_file = ROOT / "data" / "raw" / f"{slug}.csv"
    if slug not in statuses and not raw_file.exists():
        print(f"Ошибка: слаг '{slug}' не найден среди бизнесов проекта.")
        sys.exit(1)

    statuses[slug] = {
        "status": "active"
    }
    save_statuses(statuses)
    print(f"Сайт '{slug}' восстановлен в статус ACTIVE")
    build(slug)
    build_catalog()
    update_sites_zip()


def deploy():
    """Публикует изменения на GitHub Pages (ветка gh-pages) с обходом локального прокси"""
    print("Подготовка к деплою на GitHub Pages (ветка gh-pages)...")
    build_catalog()
    update_sites_zip()

    subprocess.run(["git", "add", "-A", "sites"], cwd=ROOT, check=True)

    res = subprocess.run(["git", "write-tree", "--prefix=sites/"], cwd=ROOT, capture_output=True, text=True, check=True)
    tree_sha = res.stdout.strip()

    res_parent = subprocess.run(["git", "rev-parse", "gh-pages"], cwd=ROOT, capture_output=True, text=True)
    parent_commit = res_parent.stdout.strip() if res_parent.returncode == 0 else None

    if parent_commit:
        res_old_tree = subprocess.run(["git", "rev-parse", "gh-pages:"], cwd=ROOT, capture_output=True, text=True)
        old_tree = res_old_tree.stdout.strip() if res_old_tree.returncode == 0 else None
        if old_tree == tree_sha:
            print("Ветка gh-pages уже синхронизирована с sites/ (дерево не изменилось).")
            push_cmd = ["git", "-c", "http.proxy=", "-c", "https.proxy=", "push", "origin", "gh-pages"]
            push_proc = subprocess.run(push_cmd, cwd=ROOT, capture_output=True, text=True)
            if push_proc.returncode == 0:
                print("GitHub Pages актуален:", push_proc.stdout.strip() or "Everything up-to-date")
            else:
                print("Ошибка при отправке в origin gh-pages:", push_proc.stderr)
            return

    commit_msg = "deploy: синхронизация сайтов и каталога [build.py --deploy]"
    commit_cmd = ["git", "commit-tree", tree_sha, "-m", commit_msg]
    if parent_commit:
        commit_cmd.extend(["-p", parent_commit])

    commit_proc = subprocess.run(commit_cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    new_commit_sha = commit_proc.stdout.strip()

    subprocess.run(["git", "update-ref", "refs/heads/gh-pages", new_commit_sha], cwd=ROOT, check=True)
    print(f"Локальная ветка gh-pages обновлена: {new_commit_sha[:7]}")

    push_cmd = ["git", "-c", "http.proxy=", "-c", "https.proxy=", "push", "origin", "gh-pages"]
    push_proc = subprocess.run(push_cmd, cwd=ROOT, capture_output=True, text=True)
    if push_proc.returncode == 0:
        print("Успешно опубликовано на GitHub Pages:")
        print(push_proc.stdout.strip() or push_proc.stderr.strip())
    else:
        print("Ошибка при отправке на GitHub Pages:", push_proc.stderr)
        sys.exit(1)


def sync_template_inline_css():
    """Синхронизирует общие стили из template/style.css в <style id="site-inline-css"> в template/index.html"""
    css_content = (TPL / "style.css").read_text(encoding="utf-8")
    m_css = re.search(r"(\*\s*\{[\s\S]*)$", css_content)
    if not m_css:
        return
    common_css = m_css.group(1).strip()

    tpl_file = TPL / "index.html"
    tpl_content = tpl_file.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(<style id=\"site-inline-css\">[\s\S]*?:root\s*\{[\s\S]*?\}\n\n)([\s\S]*?)(</style>)",
        re.DOTALL
    )
    if pattern.search(tpl_content):
        new_tpl = pattern.sub(lambda m: m.group(1) + common_css + "\n" + m.group(3), tpl_content)
        if new_tpl != tpl_content:
            tpl_file.write_text(new_tpl, encoding="utf-8")
            print("Synchronized inline CSS in template/index.html")


def update_sites_zip():
    """Упаковывает все собранные сайты из sites/ в архив sites.zip"""
    import zipfile
    zip_path = ROOT / "sites.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in sorted((ROOT / "sites").rglob("*")):
            if file.is_file():
                arcname = file.relative_to(ROOT / "sites").as_posix()
                z.write(file, arcname)
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"OK sites.zip ({size_mb:.1f} MB)")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        # python template/build.py — полная пересборка сайтов, каталога и архива sites.zip
        sync_template_inline_css()
        slugs = [p.stem for p in sorted((ROOT / "content").glob("*.json")) if p.stem != "sample"]
        for s in slugs:
            build(s)
        build_catalog()
        update_sites_zip()
    elif args[0] == "--status":
        # python template/build.py --status — таблица статусов всех 21 сайтов
        show_status()
    elif args[0] == "--hide":
        # python template/build.py --hide <slug> ["причина"]
        if len(args) < 2:
            print("Использование: python template/build.py --hide <slug> [\"причина\"]")
            sys.exit(1)
        slug = args[1]
        reason = args[2] if len(args) > 2 else "По обращению представителя компании"
        hide_site(slug, reason)
    elif args[0] == "--show":
        # python template/build.py --show <slug>
        if len(args) < 2:
            print("Использование: python template/build.py --show <slug>")
            sys.exit(1)
        slug = args[1]
        show_site(slug)
    elif args[0] == "--deploy":
        # python template/build.py --deploy
        deploy()
    else:
        # python template/build.py [slug ...] — пересборка указанных слагов + каталога + sites.zip
        sync_template_inline_css()
        slugs = [s for s in args if not s.startswith("--")]
        for s in slugs:
            build(s)
        build_catalog()
        update_sites_zip()
