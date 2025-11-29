"""
Telegram connectivity test for NodeMCU ESP8266
This tool helps diagnose and test Telegram API connectivity issues
"""

import network
import time
import urequests
import gc
import config

# Connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected")
        return True
        
    print(f"Connecting to {ssid}...")
    wlan.connect(ssid, password)
    
    # Wait with timeout
    for _ in range(20):
        if wlan.isconnected():
            print("WiFi connected:", wlan.ifconfig()[0])
            return True
        time.sleep(0.5)
    
    print("WiFi connection failed")
    return False

# Test Telegram with direct IP
def test_telegram_direct_ip():
    print("Testing Telegram with direct IP...")
    
    try:
        bot_token = config.TELEGRAM_BOT_TOKEN
        chat_id = config.TELEGRAM_CHAT_ID
        message = "Test message from ESP8266"
        
        # Hardcoded IP for api.telegram.org
        telegram_ip = "149.154.167.220"
        
        url = f"http://{telegram_ip}/bot{bot_token}/sendMessage"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.telegram.org',
            'Connection': 'close'
        }
        post_data = f"chat_id={chat_id}&text={message}"
        
        print(f"Sending request to URL: {url}")
        gc.collect()  # Free memory before request
        
        response = urequests.post(url, headers=headers, data=post_data)
        status = response.status_code
        body = response.text
        response.close()
        
        print(f"Status: {status}")
        print(f"Response: {body[:100]}...")  # Print first 100 chars
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Main function
def main():
    print("=== Telegram API Test ===")
    
    if not connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        print("WiFi connection failed. Cannot continue.")
        return
    
    # First test with direct IP
    if test_telegram_direct_ip():
        print("Direct IP test successful!")
    else:
        print("Direct IP test failed.")

if __name__ == "__main__":
    main()
