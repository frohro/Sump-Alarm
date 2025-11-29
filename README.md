# Sump Pump Alarm System

A MicroPython-based sump pump alarm system for ESP32-C3 that monitors water levels and sends notifications through multiple channels.

## Features

- **Local Alarm**: Sounds a speaker through H-bridge when water is detected
- **Visual Indicator**: LED blinks normally, stays solid during alarm
- **Multiple Notifications**:
  - Telegram messages
  - Email alerts via Gmail
  - Push notifications via Ntfy.sh
  - SMS via email-to-SMS gateways

## Setup Instructions

### 1. Clone or Download the Repository

```bash

git clone https://github.com/yourusername/sump-alarm.git
cd sump-alarm
```

### 2. Configure Credentials

**SECURITY WARNING**: Never commit sensitive credentials to GitHub! The `config.py` file is automatically excluded by `.gitignore`.

1. **Copy the configuration template**:
   ```bash
   cp config_template.py config.py
   ```

2. **Edit `config.py` with your actual credentials**:
   ```python
   # WiFi Configuration
   WIFI_SSID = "Your_WiFi_Name"
   WIFI_PASSWORD = "your_wifi_password"

   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   TELEGRAM_CHAT_ID = "123456789"

   # Gmail Configuration (use App Password, not regular password)
   GMAIL_USER = "your_email@gmail.com"
   GMAIL_APP_PASSWORD = "abcd-efgh-ijkl-mnop"  # 16-character App Password

   # Ntfy Configuration
   NTFY_TOPIC = "your_unique_topic_name"

   # Email Recipients
   EMAIL_RECIPIENTS = [
       "your_email@example.com",
       "another_person@example.com",
       "1234567890@tmomail.net"  # SMS via carrier gateway
   ]
   ```

#### Setting Up Each Service

**Telegram Setup:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot` command
3. Copy the bot token to `TELEGRAM_BOT_TOKEN`
4. Start a chat with your bot and send a message
5. Get your chat ID: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. Copy the chat ID to `TELEGRAM_CHAT_ID`

**Gmail Setup:**
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Select "App" → "Other (custom name)" → Enter "ESP32 Sump Alarm"
4. Use the 16-character password in `GMAIL_APP_PASSWORD`

**Ntfy Setup:**
1. Choose a unique topic name (e.g., "yourname-sump-alarm")
2. Install Ntfy app on your phone
3. Subscribe to your topic in the app

**SMS via Email:**
- T-Mobile: `number@tmomail.net`
- Verizon: `number@vtext.com`
- AT&T: `number@txt.att.net`
- Add these to `EMAIL_RECIPIENTS` for SMS alerts

### 3. Upload to ESP32-C3

Use your preferred tool (ampy, mpremote, Thonny, etc.):

```bash
# Install required packages
pip install adafruit-ampy

# Upload files
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put email_sender.py
ampy --port /dev/ttyUSB0 put mybase64.py
```

### 4. Test the System

Upload and run the test files to verify each notification method:

```bash
ampy --port /dev/ttyUSB0 put test_all.py
# Then on ESP32: import test_all
```

## Hardware Requirements

- ESP32-C3 Super Mini
- L9110S H-Bridge
- Speaker (8 ohm)
- Water level sensor (float switch)
- Power supply (5V USB)

## Pin Configuration

| GPIO | Function |
|------|----------|
| 3    | Sensor GND |
| 4    | Water sensor input |
| 6    | H-Bridge IN_A |
| 7    | H-Bridge IN_B |
| 8    | LED |

## Files Overview

- `main.py` - Main alarm program
- `config.py` - Your credentials (not in repo)
- `config_template.py` - Template for credentials
- `email_sender.py` - Gmail SMTP implementation
- `mybase64.py` - Base64 encoder for MicroPython
- `test_*.py` - Individual test scripts
- `.gitignore` - Excludes sensitive files

## Troubleshooting

- Check WiFi connection with `test_connection.py`
- Test each notification method individually
- Monitor memory usage - ESP32-C3 has limited RAM
- Use garbage collection: `gc.collect()`

## License

MIT License - see the [LICENSE](LICENSE) file for details

## Contributing

Please ensure all credentials are properly separated before contributing.