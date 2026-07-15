# PKKStore Sub Link Changer & Key Extractor Bot

This is a Telegram Bot combined with a Mini Web App designed for PKKStore. It automatically replaces specific subdomains in subscription links and provides a beautiful UI to extract and copy individual VPN keys (VMess, VLESS, Trojan, Shadowsocks).

## Features

1. **Subdomain Replacement:**
   - Users send a subscription link to the bot.
   - The bot checks if the link contains specific domains (e.g., `vpn.domain`) and replaces them (e.g., `pkk1.domain`).
   - The bot replies with the modified link and an inline button to open the Mini Web App.

2. **Owner Commands:**
   - `/addrule <old> <new>` - Add or update a mapping rule.
   - `/delrule <old>` - Delete a mapping rule.
   - `/rules` - List all current mapping rules.

3. **PKKStore Mini Web App:**
   - Extracts keys from standard subscription links or base64 encoded strings.
   - Supports **VMess, VLESS, Trojan, Shadowsocks (SS), and SSR**.
   - Clean, dark-themed UI branded for PKKStore.
   - Filter keys by protocol.
   - Copy individual keys or bulk copy by protocol.

## Setup Instructions

### 1. Bot Setup
1. Get a Bot Token from [@BotFather](https://t.me/BotFather) on Telegram.
2. Get your Telegram User ID from [@userinfobot](https://t.me/userinfobot).
3. Open `telegram_bot.py` and replace:
   - `BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"` with your actual token.
   - `OWNER_ID = 123456789` with your actual User ID.

### 2. Hosting the Mini Web App
Since this repository is hosted on GitHub Pages, the Mini Web App is automatically available at:
`https://relax218.github.io/pkkstore-bot/webapp/index.html`

*(Note: Ensure GitHub Pages is enabled in the repository settings: Settings > Pages > Source: Deploy from a branch > Branch: main, /root)*

### 3. Running the Bot
Install the required dependencies:
```bash
pip install -r requirements.txt
```

Run the bot:
```bash
python telegram_bot.py
```

## Deployment Options for the Bot
You can run the `telegram_bot.py` script on:
- A VPS (Ubuntu, Debian, etc.)
- Heroku / Render (with slight modifications for webhooks if needed)
- Your local computer (for testing)
