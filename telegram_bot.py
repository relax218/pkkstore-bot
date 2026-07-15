import os
import json
import base64
import urllib.request
import urllib.error
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ─── Configuration ────────────────────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather ကနေ ရပါ
OWNER_ID  = 123456789               # @userinfobot ကနေ ရပါ

WEBAPP_URL = "https://relax218.github.io/pkkstore-bot/webapp/index.html"
RULES_FILE = "mapping_rules.json"

# ─── Deep Link URL Schemes ────────────────────────────────────────────────────
# v2rayNG  : v2rayng://install-config?url=<encoded_url>
# v2rayTun : v2raytun://import/<url>
# Clash Meta: clash://install-config?url=<encoded_url>
#             clashmeta://install-config?url=<encoded_url>

def make_import_buttons(sub_url: str) -> list:
    """Generate one-tap import inline buttons for all major VPN apps."""
    encoded = urllib.parse.quote(sub_url, safe='')
    
    v2rayng_url   = f"v2rayng://install-config?url={encoded}"
    v2raytun_url  = f"v2raytun://import/{sub_url}"
    clash_url     = f"clash://install-config?url={encoded}"
    clashmeta_url = f"clashmeta://install-config?url={encoded}"

    buttons = [
        [
            InlineKeyboardButton("📲 v2rayNG", url=v2rayng_url),
            InlineKeyboardButton("📲 v2rayTun", url=v2raytun_url),
        ],
        [
            InlineKeyboardButton("📲 Clash", url=clash_url),
            InlineKeyboardButton("📲 ClashMeta", url=clashmeta_url),
        ],
    ]
    return buttons

# ─── Rules ────────────────────────────────────────────────────────────────────
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "vpn.domain": "pkk1.domain",
        "zmt.domain": "pkk.domain"
    }

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

mapping_rules = load_rules()

# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "👋 မင်္ဂလာပါ။ **PKKStore** Sub Link Changer Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "🔗 Sub link တစ်ခုကို ပို့ပေးပါ၊ သတ်မှတ်ထားတဲ့ စည်းမျဉ်းတွေအတိုင်း ပြောင်းပြီး ပြန်ပို့ပေးပါမယ်။\n\n"
        "🔑 Key များကို ခွဲထုတ်လိုပါက 'Extract Keys' ခလုတ်ကို နှိပ်ပါ။\n\n"
        "📲 Sub link ကို VPN app ထဲ တစ်ချက်နှိပ်ရုံနဲ့ import လုပ်နိုင်ပါတယ်။\n\n"
        "📋 *Commands:*\n"
        "`/getkeys <link>` — Key တွေ ထုတ်ကြည့်ရန်\n"
        "`/import <link>` — VPN app ထဲ one-tap import\n"
        "`/addrule <old> <new>` — Rule ထည့်ရန် *(Owner)*\n"
        "`/delrule <old>` — Rule ဖျက်ရန် *(Owner)*\n"
        "`/rules` — Rule တွေ ကြည့်ရန် *(Owner)*"
    )
    keyboard = [
        [InlineKeyboardButton("🔑 Extract Keys (PKKStore)", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ─── Handle plain sub link messages ──────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    new_text = text
    changed = False

    for old_domain, new_domain in mapping_rules.items():
        if old_domain in new_text:
            new_text = new_text.replace(old_domain, new_domain)
            changed = True

    safe_b64 = base64.b64encode(new_text.encode()).decode().replace('+', '-').replace('/', '_')

    # Build keyboard: Extract Keys + one-tap import buttons (if it's a URL)
    keyboard = [
        [InlineKeyboardButton("🔑 Extract Keys", web_app=WebAppInfo(url=f"{WEBAPP_URL}?startapp={safe_b64}"))]
    ]

    is_url = new_text.startswith("http://") or new_text.startswith("https://")
    if is_url:
        keyboard += make_import_buttons(new_text)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if changed:
        await update.message.reply_text(
            f"✅ ပြောင်းလဲထားသော link:\n\n`{new_text}`\n\n"
            f"📲 အောက်ပါ button တစ်ခုကို နှိပ်ပြီး VPN app ထဲ တစ်ချက်နဲ့ import လုပ်နိုင်ပါတယ်:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "ℹ️ ပြောင်းလဲရန် မလိုအပ်ပါ သို့မဟုတ် သတ်မှတ်ထားသော domain များ မပါဝင်ပါ။\n\n"
            "📲 VPN app ထဲ import လုပ်ချင်ရင် button တစ်ခုကို နှိပ်ပါ:",
            reply_markup=reply_markup
        )

# ─── /import <sub_link> ───────────────────────────────────────────────────────
async def import_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "ℹ️ အသုံးပြုပုံ: `/import <sub_link>`\n"
            "ဥပမာ: `/import https://vpn.domain/sub/123`",
            parse_mode="Markdown"
        )
        return

    sub_link = context.args[0]

    # Auto-convert domain if rule matches
    converted = sub_link
    for old_domain, new_domain in mapping_rules.items():
        if old_domain in converted:
            converted = converted.replace(old_domain, new_domain)

    changed_note = ""
    if converted != sub_link:
        changed_note = f"✅ Domain ပြောင်းထားသည်: `{sub_link}` → `{converted}`\n\n"

    keyboard = make_import_buttons(converted)
    # Add Extract Keys button too
    safe_b64 = base64.b64encode(converted.encode()).decode().replace('+', '-').replace('/', '_')
    keyboard.append([
        InlineKeyboardButton("🔑 Extract Keys", web_app=WebAppInfo(url=f"{WEBAPP_URL}?startapp={safe_b64}"))
    ])

    await update.message.reply_text(
        f"{changed_note}"
        f"📲 **One-Tap Import** — ဖွင့်ထားသော VPN app ကို ရွေးပြီး နှိပ်ပါ:\n\n"
        f"• **v2rayNG** — Android အတွက် အသုံးအများဆုံး\n"
        f"• **v2rayTun** — iOS/Android နှစ်မျိုးလုံး support\n"
        f"• **Clash / ClashMeta** — Rule-based proxy\n\n"
        f"_App မဖွင့်ရင် ဦးစွာ app ကို install လုပ်ပြီး ပြန်နှိပ်ပါ_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ─── /getkeys <sub_link> ──────────────────────────────────────────────────────
async def get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "ℹ️ အသုံးပြုပုံ: `/getkeys <sub_link>`\n"
            "ဥပမာ: `/getkeys https://vpn.domain/sub/123`",
            parse_mode="Markdown"
        )
        return

    sub_link = context.args[0]

    for old_domain, new_domain in mapping_rules.items():
        if old_domain in sub_link:
            sub_link = sub_link.replace(old_domain, new_domain)

    processing_msg = await update.message.reply_text("⏳ Server ဘက်မှ fetch လုပ်နေပါသည်...")

    try:
        req = urllib.request.Request(sub_link, headers={'User-Agent': 'v2rayNG/1.8.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')

        # Try base64 decode
        try:
            padded = content.strip() + '=' * (-len(content.strip()) % 4)
            decoded = base64.b64decode(padded).decode('utf-8')
            if any(p in decoded for p in ('vmess://', 'vless://', 'trojan://', 'ss://')):
                content = decoded
        except Exception:
            pass

        keys = [line.strip() for line in content.split('\n')
                if line.strip() and '://' in line and
                any(line.strip().startswith(p) for p in ('vmess://', 'vless://', 'trojan://', 'ss://', 'ssr://'))]

        if not keys:
            await processing_msg.edit_text("❌ Link ထဲတွင် key များ မတွေ့ပါ။")
            return

        # Count by protocol
        proto_counts = {}
        for k in keys:
            proto = k.split('://')[0]
            proto_counts[proto] = proto_counts.get(proto, 0) + 1

        proto_summary = "  ".join([f"{p.upper()}: {c}" for p, c in proto_counts.items()])

        display_keys = keys[:20]
        msg = f"✅ တွေ့ရှိသော Key များ ({len(keys)} ခု)\n"
        msg += f"📊 {proto_summary}\n\n"
        for key in display_keys:
            msg += f"`{key}`\n\n"

        if len(keys) > 20:
            msg += f"_... အခြား key {len(keys) - 20} ခု ကျန်သေးသည်_"

        context.user_data['last_keys'] = keys
        context.user_data['last_sub_link'] = sub_link

        # Buttons: Copy All + one-tap import
        keyboard = [
            [InlineKeyboardButton(f"📋 Copy All Keys ({len(keys)} ခု)", callback_data="copy_all_keys")],
        ]
        keyboard += make_import_buttons(sub_link)

        await processing_msg.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    except urllib.error.URLError as e:
        await processing_msg.edit_text(
            f"❌ Fetch လုပ်၍မရပါ:\n`{str(e)}`\n\n"
            f"Server ကို ဆက်သွယ်၍မရပါ။ Link မှန်မမှန် စစ်ပါ။",
            parse_mode="Markdown"
        )
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")

# ─── Copy All Keys callback ───────────────────────────────────────────────────
async def copy_all_keys_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keys = context.user_data.get('last_keys', [])
    if not keys:
        await query.answer("❌ Key များ မရှိပါ။ /getkeys ကို ပြန်သုံးပါ။", show_alert=True)
        return

    all_keys_text = "\n".join(keys)

    if len(all_keys_text) <= 3800:
        await query.message.reply_text(
            f"📋 All Keys ({len(keys)} ခု) — long-press ပြီး copy လုပ်ပါ:\n\n`{all_keys_text}`",
            parse_mode="Markdown"
        )
    else:
        chunk = ""
        part = 1
        for key in keys:
            if len(chunk) + len(key) + 1 > 3800:
                await query.message.reply_text(
                    f"📋 Keys Part {part}:\n\n`{chunk.strip()}`",
                    parse_mode="Markdown"
                )
                chunk = ""
                part += 1
            chunk += key + "\n"
        if chunk:
            await query.message.reply_text(
                f"📋 Keys Part {part}:\n\n`{chunk.strip()}`",
                parse_mode="Markdown"
            )

# ─── Owner Commands ───────────────────────────────────────────────────────────
async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
    if len(context.args) != 2:
        await update.message.reply_text("ℹ️ အသုံးပြုပုံ: /addrule <old_domain> <new_domain>")
        return
    old_domain, new_domain = context.args
    mapping_rules[old_domain] = new_domain
    save_rules(mapping_rules)
    await update.message.reply_text(f"✅ Rule ထည့်ပြီး:\n`{old_domain}` ➡️ `{new_domain}`", parse_mode="Markdown")

async def remove_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
    if len(context.args) != 1:
        await update.message.reply_text("ℹ️ အသုံးပြုပုံ: /delrule <old_domain>")
        return
    old_domain = context.args[0]
    if old_domain in mapping_rules:
        del mapping_rules[old_domain]
        save_rules(mapping_rules)
        await update.message.reply_text(f"✅ Rule ဖျက်ပြီး: `{old_domain}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ ရှာမတွေ့ပါ: `{old_domain}`", parse_mode="Markdown")

async def list_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
    if not mapping_rules:
        await update.message.reply_text("ℹ️ လက်ရှိတွင် Rule များ မရှိပါ။")
        return
    msg = "📋 လက်ရှိ Rule များ:\n\n"
    for old, new in mapping_rules.items():
        msg += f"• `{old}` ➡️ `{new}`\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("import",  import_cmd))
    app.add_handler(CommandHandler("getkeys", get_keys))
    app.add_handler(CommandHandler("addrule", add_rule))
    app.add_handler(CommandHandler("delrule", remove_rule))
    app.add_handler(CommandHandler("rules",   list_rules))
    app.add_handler(CallbackQueryHandler(copy_all_keys_callback, pattern="^copy_all_keys$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ PKKStore Bot is running...")
    app.run_polling()
