# Configuration Template for Sump Alarm System
# Copy this file to config.py and fill in your actual credentials
# DO NOT commit config.py to GitHub - it contains sensitive information

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Telegram Bot Configuration
# Get these from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Gmail Configuration (for email alerts)
# Use an App Password, not your regular Gmail password
GMAIL_USER = "your_email@gmail.com"
GMAIL_APP_PASSWORD = "16_CHARACTER_APP_PASSWORD"

# Ntfy Configuration (free push notifications)
# Create your own unique topic at https://ntfy.sh
NTFY_TOPIC = "your_unique_topic"

# Email Recipients (includes SMS via email-to-SMS gateways)
EMAIL_RECIPIENTS = [
    "your_email@example.com",
    "another_email@example.com",
    # SMS gateways (example for T-Mobile):
    # "1234567890@tmomail.net"
]