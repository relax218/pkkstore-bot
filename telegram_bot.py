import os
import json
import base64
import urllib.request
import urllib.error
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" # Replace with your actual bot token
OWNER_ID = 123456789 # Replace with your actual Telegram User ID

# Web App URL - Mini App ကို host လုပ်ထားတဲ့ URL ထည့်ပါ (e.g. GitHub Pages URL)
WEBAPP_URL = "https://relax218.github.io/pkkstore-bot/webapp/index.html"

# File to store mapping rules
RULES_FILE = "mapping_rules.json"

# Load mapping rules from file
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    # Default rules as requested
    return {
        "vpn.domain": "pkk1.domain",
        "zmt.domain": "pkk.domain"
    }

# Save mapping rules to file
def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

# Global variable to hold rules
mapping_rules = load_rules()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "👋 မင်္ဂလာပါ။ **PKKStore** Sub Link Changer Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "🔗 Sub link တစ်ခုကို ပို့ပေးပါ၊ သတ်မှတ်ထားတဲ့ စည်းမျဉ်းတွေအတိုင်း ပြောင်းပြီး ပြန်ပို့ပေးပါမယ်။\n\n"
        "🔑 Key များကို ခွဲထုတ်လိုပါက အောက်ပါ 'Extract Keys' ခလုတ်ကို နှိပ်ပါ။"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔑 Extract Keys (PKKStore)", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Simple replacement based on mapping rules
    new_text = text
    changed = False
    
    for old_domain, new_domain in mapping_rules.items():
        if old_domain in new_text:
            new_text = new_text.replace(old_domain, new_domain)
            changed = True
            
    # Create a safe base64 version of the new link to pass to WebApp via startapp param
    safe_b64 = base64.b64encode(new_text.encode()).decode().replace('+', '-').replace('/', '_')
    
    keyboard = [
        [InlineKeyboardButton("🔑 Extract Keys from this Link", web_app=WebAppInfo(url=f"{WEBAPP_URL}?startapp={safe_b64}"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if changed:
        await update.message.reply_text(f"✅ ပြောင်းလဲထားသော link:\n\n`{new_text}`", reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text("ℹ️ ပြောင်းလဲရန် မလိုအပ်ပါ သို့မဟုတ် သတ်မှတ်ထားသော domain များ မပါဝင်ပါ။\n\nအောက်ပါခလုတ်ကိုနှိပ်၍ Key များကို ထုတ်ယူနိုင်ပါသည်။", reply_markup=reply_markup)

# Owner Commands
async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if len(context.args) != 2:
        await update.message.reply_text("ℹ️ အသုံးပြုပုံ: /addrule <old_domain> <new_domain>\nဥပမာ: /addrule vpn.domain pkk1.domain")
        return
        
    old_domain, new_domain = context.args
    mapping_rules[old_domain] = new_domain
    save_rules(mapping_rules)
    
    await update.message.reply_text(f"✅ စည်းမျဉ်းအသစ် ထည့်သွင်းပြီးပါပြီ:\n{old_domain} -> {new_domain}")

async def remove_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if len(context.args) != 1:
        await update.message.reply_text("ℹ️ အသုံးပြုပုံ: /delrule <old_domain>\nဥပမာ: /delrule vpn.domain")
        return
        
    old_domain = context.args[0]
    if old_domain in mapping_rules:
        del mapping_rules[old_domain]
        save_rules(mapping_rules)
        await update.message.reply_text(f"✅ စည်းမျဉ်းကို ဖျက်လိုက်ပါပြီ: {old_domain}")
    else:
        await update.message.reply_text(f"❌ ရှာမတွေ့ပါ: {old_domain}")

async def get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("ℹ️ အသုံးပြုပုံ: /getkeys <sub_link>\nဥပမာ: /getkeys https://vpn.domain/sub/123")
        return
        
    sub_link = context.args[0]
    
    # Optional: If the user provides an old link, we can auto-convert it first
    for old_domain, new_domain in mapping_rules.items():
        if old_domain in sub_link:
            sub_link = sub_link.replace(old_domain, new_domain)
            
    processing_msg = await update.message.reply_text("⏳ Server ဘက်မှ fetch လုပ်နေပါသည်...")
    
    try:
        req = urllib.request.Request(sub_link, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            
        # Try to decode base64 if it's base64 encoded
        try:
            # Add padding if needed
            padded = content + '=' * (-len(content) % 4)
            decoded = base64.b64decode(padded).decode('utf-8')
            content = decoded
        except Exception:
            pass # Not base64, use raw content
            
        keys = [line.strip() for line in content.split('\n') if line.strip() and ('://' in line)]
        
        if not keys:
            await processing_msg.edit_text("❌ Link ထဲတွင် key များ မတွေ့ပါ။")
            return
            
        # Limit to first 20 keys if too many to avoid Telegram message length limit
        display_keys = keys[:20]
        msg = f"✅ တွေ့ရှိသော Key များ ({len(keys)} ခု):\n\n"
        for i, key in enumerate(display_keys, 1):
            msg += f"`{key}`\n\n"
            
        if len(keys) > 20:
            msg += f"... အခြား key {len(keys) - 20} ခု ကျန်သေးသည်။"
            
        await processing_msg.edit_text(msg, parse_mode="Markdown")
        
    except urllib.error.URLError as e:
        await processing_msg.edit_text(f"❌ Fetch လုပ်၍မရပါ (CORS ပြဿနာမဟုတ်ပါ၊ Server သို့ ဆက်သွယ်၍မရပါ):\n{str(e)}")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error ဖြစ်ပေါ်နေပါသည်:\n{str(e)}")

async def list_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if not mapping_rules:
        await update.message.reply_text("ℹ️ လက်ရှိတွင် စည်းမျဉ်းများ မရှိပါ။")
        return
        
    msg = "📋 လက်ရှိ စည်းမျဉ်းများ:\n\n"
    for old, new in mapping_rules.items():
        msg += f"- `{old}` ➡️ `{new}`\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addrule", add_rule))
    app.add_handler(CommandHandler("delrule", remove_rule))
    app.add_handler(CommandHandler("rules", list_rules))
    app.add_handler(CommandHandler("getkeys", get_keys))
    
    # Handle normal messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("PKKStore Bot is running...")
    app.run_polling()
