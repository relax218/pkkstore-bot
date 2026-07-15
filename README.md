# Telegram Sub Link Changer Bot

ဒီ Bot ဟာ user တွေပို့လိုက်တဲ့ sub link တွေထဲက domain တွေကို owner သတ်မှတ်ထားတဲ့အတိုင်း ပြောင်းလဲပြီး ပြန်ပို့ပေးမယ့် bot ဖြစ်ပါတယ်။

## ပါဝင်တဲ့ Feature များ

1. **User များအတွက်:**
   - Link တစ်ခုပို့လိုက်တာနဲ့ သတ်မှတ်ထားတဲ့ domain တွေပါရင် အလိုအလျောက် ပြောင်းလဲပြီး ပြန်ပို့ပေးပါမယ်။
   - ဥပမာ: `https://vpn.kiwihub.top:8000/...` လို့ ပို့လိုက်ရင် `https://pkk1.kiwihub.top:8000/...` လို့ ပြောင်းပေးပါမယ်။

2. **Owner အတွက်:**
   - Telegram ကနေပဲ rule တွေကို အလွယ်တကူ ပြင်ဆင်နိုင်ပါတယ်။
   - `/addrule <old> <new>` - Rule အသစ်ထည့်ရန် (သို့) ရှိပြီးသားကို ပြင်ရန်
   - `/delrule <old>` - Rule ကို ဖျက်ရန်
   - `/rules` - လက်ရှိ rule အားလုံးကို ကြည့်ရန်

## အသုံးပြုရန် ပြင်ဆင်ခြင်း

1. BotFather (`@BotFather`) ဆီကနေ Bot token အသစ်တစ်ခု တောင်းပါ။
2. `telegram_bot.py` ဖိုင်ကို ဖွင့်ပြီး အောက်ပါအချက်တွေကို ပြင်ပါ:
   - `BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"` နေရာမှာ BotFather ပေးတဲ့ token ကို ထည့်ပါ။
   - `OWNER_ID = 123456789` နေရာမှာ သင့်ရဲ့ Telegram User ID ကို ထည့်ပါ။ (ID ကို `@userinfobot` ကနေ ကြည့်နိုင်ပါတယ်)
3. လိုအပ်တဲ့ library တွေကို install လုပ်ပါ:
   ```bash
   pip install -r requirements.txt
   ```
4. Bot ကို run ပါ:
   ```bash
   python telegram_bot.py
   ```

## Default Rules

စတင် run တဲ့အခါ အောက်ပါ rule တွေ အလိုအလျောက် ပါဝင်နေပါမယ်:
- `vpn.kiwihub.top` -> `pkk1.kiwihub.top`
- `zmt.hiddenvpn.beer` -> `pkk.hiddenvpn.beer`

Rule တွေကို ပြောင်းလဲလိုက်ရင် `mapping_rules.json` ဖိုင်ထဲမှာ အလိုအလျောက် သိမ်းဆည်းသွားမှာ ဖြစ်တဲ့အတွက် bot ကို ပိတ်ပြီး ပြန်ဖွင့်လည်း rule တွေ ပျောက်မသွားပါဘူး။
