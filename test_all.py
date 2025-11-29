"""
ESP32-C3 Combined Notification Test
Tests all notification methods together (Telegram, Gmail, Ntfy)
"""

import network
import time
import gc
import urequests
import config

def connect_wifi():
    """Connect to WiFi"""
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected:", wlan.ifconfig()[0])
        return True
    
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    
    max_wait = 20
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Waiting...")
        time.sleep(1)
    
    if wlan.isconnected():
        print("WiFi connected:", wlan.ifconfig()[0])
        return True
    else:
        print("WiFi failed")
        return False

def test_telegram():
    """Send Telegram notification"""
    print("\n1. Testing Telegram...")
    
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    message = "🚨 SUMP ALARM! (COMBINED TEST) All notification systems are being tested."
    
    encoded_message = message.replace(" ", "%20")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_message}"
    
    try:
        response = urequests.get(url, timeout=20)
        if response.status_code == 200:
            print("   ✓ Telegram SUCCESS")
            response.close()
            return True
        else:
            print(f"   ✗ Telegram failed: {response.status_code}")
            response.close()
            return False
    except Exception as e:
        print(f"   ✗ Telegram error: {e}")
        return False

def test_gmail():
    """Send Gmail notification (only to rob.frohne, not wife!)"""
    print("\n2. Testing Gmail...")
    
    try:
        import email_sender
        
        gmail_user = config.GMAIL_USER
        app_password = config.GMAIL_APP_PASSWORD
        
        gmail = email_sender.GmailSender(gmail_user, app_password)
        
        # Only send to Rob for this test!
        recipients = ["rob.frohne@wallawalla.edu"]
        subject = "🚨 SUMP ALARM (COMBINED TEST)"
        message = "This is a COMBINED TEST of all notification systems.\n\nTelegram, Gmail, and Ntfy are all being tested together."
        
        success = gmail.send_email(recipients, subject, message)
        
        if success:
            print("   ✓ Gmail SUCCESS")
            return True
        else:
            print("   ✗ Gmail failed")
            return False
            
    except Exception as e:
        print(f"   ✗ Gmail error: {e}")
        return False

def test_ntfy():
    """Send Ntfy notification"""
    print("\n3. Testing Ntfy...")
    
    topic = config.NTFY_TOPIC
    url = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "SUMP ALARM! (COMBINED TEST)",
        "Priority": "urgent",
        "Tags": "warning,rotating_light"
    }
    
    message = "All notification systems are being tested together!"
    
    try:
        response = urequests.post(url, headers=headers, data=message, timeout=15)
        
        if response.status_code == 200:
            print("   ✓ Ntfy SUCCESS")
            response.close()
            return True
        else:
            print(f"   ✗ Ntfy failed: {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"   ✗ Ntfy error: {e}")
        return False

# Main test
print("=" * 40)
print("COMBINED NOTIFICATION TEST")
print("=" * 40)

if not connect_wifi():
    print("Cannot test - WiFi failed")
else:
    gc.collect()
    print(f"Free memory: {gc.mem_free()} bytes")
    
    results = []
    
    # Test each method
    results.append(("Telegram", test_telegram()))
    gc.collect()
    
    results.append(("Gmail", test_gmail()))
    gc.collect()
    
    results.append(("Ntfy", test_ntfy()))
    
    # Summary
    print("\n" + "=" * 40)
    print("RESULTS SUMMARY")
    print("=" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("ALL NOTIFICATIONS WORKING!")
    else:
        print("Some notifications failed - check above")
    print("=" * 40)

print("\nTest complete")
