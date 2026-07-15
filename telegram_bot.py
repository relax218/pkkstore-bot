import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" # Replace with your actual bot token
OWNER_ID = 123456789 # Replace with your actual Telegram User ID

# File to store mapping rules
RULES_FILE = "mapping_rules.json"

# Load mapping rules from file
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "vpn.kiwihub.top": "pkk1.kiwihub.top",
        "zmt.hiddenvpn.beer": "pkk.hiddenvpn.beer"
    }

# Save mapping rules to file
def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

# Global variable to hold rules
mapping_rules = load_rules()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "မင်္ဂလာပါ။ Sub link များကို ပြောင်းလဲပေးမယ့် Bot ပါ။\n\n"
        "Sub link တစ်ခုကို ပို့ပေးပါ၊ သတ်မှတ်ထားတဲ့ စည်းမျဉ်းတွေအတိုင်း ပြောင်းပြီး ပြန်ပို့ပေးပါမယ်။"
    )
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Simple replacement based on mapping rules
    new_text = text
    changed = False
    
    for old_domain, new_domain in mapping_rules.items():
        if old_domain in new_text:
            new_text = new_text.replace(old_domain, new_domain)
            changed = True
            
    if changed:
        await update.message.reply_text(f"ပြောင်းလဲထားသော link:\n{new_text}")
    else:
        await update.message.reply_text("ပြောင်းလဲရန် မလိုအပ်ပါ သို့မဟုတ် သတ်မှတ်ထားသော domain များ မပါဝင်ပါ။")

# Owner Commands
async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if len(context.args) != 2:
        await update.message.reply_text("အသုံးပြုပုံ: /addrule <old_domain> <new_domain>\nဥပမာ: /addrule vpn.kiwihub.top pkk1.kiwihub.top")
        return
        
    old_domain, new_domain = context.args
    mapping_rules[old_domain] = new_domain
    save_rules(mapping_rules)
    
    await update.message.reply_text(f"စည်းမျဉ်းအသစ် ထည့်သွင်းပြီးပါပြီ:\n{old_domain} -> {new_domain}")

async def remove_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if len(context.args) != 1:
        await update.message.reply_text("အသုံးပြုပုံ: /delrule <old_domain>\nဥပမာ: /delrule vpn.kiwihub.top")
        return
        
    old_domain = context.args[0]
    if old_domain in mapping_rules:
        del mapping_rules[old_domain]
        save_rules(mapping_rules)
        await update.message.reply_text(f"စည်းမျဉ်းကို ဖျက်လိုက်ပါပြီ: {old_domain}")
    else:
        await update.message.reply_text(f"ရှာမတွေ့ပါ: {old_domain}")

async def list_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("ဒီ command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။")
        return
        
    if not mapping_rules:
        await update.message.reply_text("လက်ရှိတွင် စည်းမျဉ်းများ မရှိပါ။")
        return
        
    msg = "လက်ရှိ စည်းမျဉ်းများ:\n"
    for old, new in mapping_rules.items():
        msg += f"- {old} -> {new}\n"
        
    await update.message.reply_text(msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addrule", add_rule))
    app.add_handler(CommandHandler("delrule", remove_rule))
    app.add_handler(CommandHandler("rules", list_rules))
    
    # Handle normal messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
