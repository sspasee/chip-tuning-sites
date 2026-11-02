#!/usr/bin/env python3
"""Единый скрипт сборки. Python 3, только стандартная библиотека.
Запуск из корня проекта:  python template/build.py [slug ...]
Берёт content/{slug}.json + photos/{slug}/ и пишет sites/{slug}/.
Пустое поле или пустой список -> блок скрывается. Ничего не подставляется."""
import html, json, re, shutil, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "template"
TOK = re.compile(r"\{\{(#if|#each|/if|/each) ?(\w*)\}\}")
VAR = re.compile(r"\{\{(\w+)\}\}")

THEMES = {
    # КЕМЕРОВО
    "kem-01": {
        "theme_name": "Revo Racing Orange",
        "theme_accent": "#ff5500",
        "theme_accent_dark": "#cc4400",
        "theme_accent_soft": "rgba(255, 85, 0, 0.12)",
        "theme_accent_text": "#0f1a24",
        "theme_hero_ink": "#12100e",
        "theme_hero_grad": "linear-gradient(rgba(18,16,14,0.85),rgba(18,16,14,0.92))",
        "theme_bg": "#f6f2ee",
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
        "theme_name": "Cyber Violet Stage",
        "theme_accent": "#8b5cf6",
        "theme_accent_dark": "#6d28d9",
        "theme_accent_soft": "rgba(139, 92, 246, 0.12)",
        "theme_accent_text": "#ffffff",
        "theme_hero_ink": "#151020",
        "theme_hero_grad": "linear-gradient(rgba(21,16,32,0.85),rgba(21,16,32,0.92))",
        "theme_bg": "#f3f0f8",
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
    "theme_accent_text": "#0f1a24",
    "theme_hero_ink": "#0f1a24",
    "theme_hero_grad": "linear-gradient(rgba(15,26,36,0.80),rgba(15,26,36,0.88))",
    "theme_bg": "#edf1f4",
}

SOCIALS_MAP = {
    # КЕМЕРОВО
    "kem-01": [
        {"name": "Telegram", "url": "https://t.me/+79069839530"},
        {"name": "ВКонтакте", "url": "https://vk.com"},
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
            out.append(VAR.sub(lambda m: html.escape(str(ctx.get(m.group(1)) or ""), quote=True), n))
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


def build(slug):
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
    theme = THEMES.get(slug, DEFAULT_THEME)
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

    out = ROOT / "sites" / slug

    # Сохраняем флагманский эталон tom-01, если он уже существует
    custom_index = None
    custom_css = None
    if slug == "tom-01":
        idx_file = out / "index.html"
        css_file = out / "style.css"
        if idx_file.exists():
            content = idx_file.read_text(encoding="utf-8")
            if "tom01-inline-css" in content or "Автокат-Делит" in content:
                custom_index = content
        if css_file.exists():
            content_css = css_file.read_text(encoding="utf-8")
            if len(content_css) > 5000:
                custom_css = content_css

    shutil.rmtree(out, ignore_errors=True)
    (out / "img").mkdir(parents=True)
    photos_dir = ROOT / "photos" / slug
    photos = sorted(photos_dir.glob("*.[jp][pn]g"))[:8] if photos_dir.exists() else []
    data["photos"] = []
    for p in photos:
        shutil.copy(p, out / "img" / p.name)
        data["photos"].append({"src": f"img/{p.name}"})
    if photos:
        data["hero_photo"] = f"img/{photos[0].name}"
    else:
        fallback_hero = TPL / "assets" / f"hero-business-{slug}.jpg"
        if fallback_hero.exists():
            shutil.copy(fallback_hero, out / "img" / "hero-business.jpg")
            data["hero_photo"] = "img/hero-business.jpg"

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
        shutil.copy(TPL / "style.css", out / "style.css")

    # запрет индексации: robots.txt + заголовок для Netlify/Cloudflare Pages
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", encoding="utf-8")
    print(f"OK {slug} ({theme['theme_name']})")


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
    sync_template_inline_css()
    slugs = sys.argv[1:] or [p.stem for p in sorted((ROOT / "content").glob("*.json")) if p.stem != "sample"]
    for s in slugs:
        build(s)
    update_sites_zip()
