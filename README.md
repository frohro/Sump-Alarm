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

**IMPORTANT**: Never commit sensitive credentials to GitHub!

1. Copy the configuration template:
   ```bash
   cp config_template.py config.py
   ```

2. Edit `config.py` with your actual credentials:
   - WiFi SSID and password
   - Telegram bot token and chat ID
   - Gmail credentials (use App Password)
   - Ntfy topic
   - Email recipients

### 3. Set Up Notification Services

#### Telegram Setup
1. Message @BotFather on Telegram to create a bot
2. Get your bot token
3. Start a chat with your bot and send a message
4. Use `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` to get your chat ID

#### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in `config.py` (not your regular password)

#### Ntfy Setup
1. Choose a unique topic name
2. Install the Ntfy app on your phone
3. Subscribe to your topic

### 4. Upload to ESP32-C3

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

### 5. Test the System

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

[Your License Here]

## Contributing

Please ensure all credentials are properly separated before contributing.