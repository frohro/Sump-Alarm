"""
ESP32-C3 Ntfy Test
Tests sending push notifications via ntfy.sh (free service)
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

def test_ntfy():
    """Test ntfy.sh notification"""
    print("\nNtfy.sh Test")
    print("============")
    print("Make sure you have the Ntfy app installed and")
    print("subscribed to topic: frohne-sump-alarm")
    print()
    
    gc.collect()
    
    # Your unique topic
    topic = config.NTFY_TOPIC
    url = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "SUMP ALARM! (TEST)",
        "Priority": "urgent",
        "Tags": "warning,rotating_light"
    }
    
    message = "This is a TEST. Water level is high! Check the sump pump immediately!"
    
    try:
        print(f"Sending to ntfy.sh/{topic}...")
        response = urequests.post(url, headers=headers, data=message, timeout=15)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Ntfy notification sent successfully!")
            response.close()
            return True
        else:
            print(f"Failed: {response.text}")
            response.close()
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

# Run test
if connect_wifi():
    test_ntfy()
else:
    print("Cannot test - WiFi failed")

print("\nTest complete")
