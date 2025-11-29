"""
ESP32-C3 Telegram Test
This simple program tests the ESP32-C3's ability to connect to WiFi
and send a Telegram notification.

Instructions:
1. Upload this file to your ESP32-C3
2. Run it using "import esp32_telegram_test"
"""

import network
import time
import gc
import urequests
import machine
import config

# Configure garbage collection
gc.enable()
gc.collect()

# LED for visual feedback - try common ESP32-C3 Super Mini LED pins
led = None
for pin_num in [8, 10, 2, 3]:  # Try common LED pins
    try:
        led = machine.Pin(pin_num, machine.Pin.OUT)
        print(f"LED initialized on GPIO {pin_num}")
        break
    except:
        pass

if led is None:
    print("No LED pin found - continuing without LED feedback")

def blink_led(times=3):
    """Blink LED to indicate status"""
    if led is None:
        return
    for _ in range(times):
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)

def connect_wifi():
    """Connect to WiFi"""
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected:", wlan.ifconfig()[0])
        return True
    
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)  # Using your existing WiFi credentials
    
    # Wait for connection with timeout
    max_wait = 20
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Waiting for connection...")
        blink_led(1)  # Single blink while waiting
        time.sleep(1)
    
    if wlan.isconnected():
        print("WiFi connected!")
        print("IP address:", wlan.ifconfig()[0])
        blink_led(2)  # Double blink for success
        return True
    else:
        print("WiFi connection failed")
        blink_led(5)  # Five blinks for failure
        return False

def send_telegram_message():
    """Send a test message via Telegram"""
    print("Preparing to send Telegram message...")
    
    # Free up memory before request
    gc.collect()
    free_memory = gc.mem_free()
    print(f"Free memory before request: {free_memory} bytes")
    
    # Telegram bot details
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    message = "🚨 SUMP ALARM! (TEST) Water level is high! Check the sump pump immediately!"
    
    # URL encode the message
    message = message.replace(" ", "%20")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    
    try:
        print("Sending HTTP request to Telegram...")
        response = urequests.get(url, timeout=20)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Message sent successfully!")
            text = response.text
            print("Response:", text[:100], "..." if len(text) > 100 else "")
            blink_led(3)  # Triple blink for success
            response.close()
            return True
        else:
            print(f"Failed with status code: {response.status_code}")
            print("Response:", response.text)
            response.close()
            blink_led(4)  # Four blinks for API error
            return False
            
    except Exception as e:
        print(f"Error sending message: {e}")
        blink_led(5)  # Five blinks for exception
        return False
    finally:
        # Memory after request
        gc.collect()
        print(f"Free memory after request: {gc.mem_free()} bytes")

def main():
    """Main function"""
    print("\nESP32-C3 Telegram Test")
    print("=====================")
    
    # Testing device information
    print(f"Machine: {machine.unique_id()}")
    print(f"Frequency: {machine.freq()/1000000} MHz")
    
    # Memory at start
    gc.collect()
    print(f"Free memory at start: {gc.mem_free()} bytes")
    
    # Connect to WiFi
    if connect_wifi():
        # Send test message
        if send_telegram_message():
            print("Test completed successfully!")
        else:
            print("Failed to send Telegram message")
    else:
        print("WiFi connection failed, cannot test Telegram")
    
    print("Test complete")
    
# Run the test
main()
