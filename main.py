# This program in MicroPython for the ESP32-C3 Super Mini is for sounding the
# alarm if the sump pump fails. It sounds a local alarm through an H-bridge
# connected speaker and sends notifications through Gmail and Telegram.
#
# Rob Frohne, Updated March 2025

from machine import Pin, Timer
import time
import gc
import network
import socket
import config  # Import configuration with credentials

# Configure garbage collection
gc.enable()
gc.threshold(gc.mem_free() // 4)

# Memory monitoring functions
def get_free_memory():
    """Return amount of free memory in bytes"""
    gc.collect()
    return gc.mem_free()

def print_memory_status(label="Current"):
    """Print memory status with a label"""
    free_mem = get_free_memory()
    print(f"=== {label} Memory: {free_mem} bytes free ===")

# GPIO pin definitions for ESP32-C3 Super Mini
LED_PIN = 8           # Built-in LED
SENSOR_GND_PIN = 3    # Virtual GND for float switch (set LOW)
WATER_SENSOR_PIN = 4  # Water sensor input (with pull-up)
SPEAKER_IN_A = 6      # H-Bridge input A
SPEAKER_IN_B = 7      # H-Bridge input B

# Speaker control functions
def toggle(p):
    """Toggle pin value"""
    p.value(not p.value())

def alarmSound(t):
    """This is to vibrate the speaker via H-bridge"""
    global in_a
    global in_b
    a = in_a.value()
    a = 0 if a else 1  # Toggle a
    b = 0 if a else 1  # b = not a
    in_a.value(a)
    in_b.value(b)

def blink_led(times=1):
    """Blink the LED a specified number of times"""
    for _ in range(times):
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)

def connect_wifi(ssid, password, max_retries=3):
    """Connect to WiFi with retries"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi:", wlan.ifconfig()[0])
        return True
        
    for attempt in range(max_retries):
        print(f"WiFi connection attempt {attempt+1}/{max_retries}")
        wlan.connect(ssid, password)
        
        # Wait with timeout
        for _ in range(20):
            if wlan.isconnected():
                print("WiFi connected:", wlan.ifconfig()[0])
                blink_led(2)  # Signal connection success
                return True
            time.sleep(0.5)
            blink_led(1)  # Signal waiting
    
    print("WiFi connection failed after retries")
    return False

def make_http_request(url, method="GET", headers=None, data=None, timeout=30):
    """General HTTP request function with optimized memory usage"""
    import urequests  # Import only when needed to save memory
    
    gc.collect()  # Force garbage collection before request
    print_memory_status("Before HTTP request")
    
    try:
        if method.upper() == "GET":
            response = urequests.get(url, timeout=timeout)
        else:  # POST
            response = urequests.post(url, headers=headers, data=data, timeout=timeout)
        
        status = response.status_code
        if status == 200:
            print(f"HTTP {method} request successful")
            result = True
        else:
            print(f"HTTP {method} request failed with status: {status}")
            result = False
            
        response.close()
        return result, status
    except OSError as e:
        print(f"Network error: {e}")
        return False, -1
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return False, -1
    finally:
        # Clean up
        gc.collect()
        print_memory_status(f"After HTTP {method} request")

def send_telegram_alert():
    """Send alert through Telegram using urequests with fallback to direct socket"""
    print("Preparing Telegram alert...")
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    message = "🚨 SUMP ALARM! Water level is high! Check the sump pump immediately!"
    
    # Simpler approach first - use urequests with simplified parameters
    try:
        import urequests
        print("Trying urequests with simplified parameters...")
        
        # Encode message for URL
        encoded_message = message.replace(" ", "%20")
        
        # Simple URL with minimum parameters
        simple_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_message}"
        
        # Attempt the request with generous timeout
        print("Sending request via urequests...")
        response = urequests.get(simple_url, timeout=30)
        
        # Check response
        if response.status_code == 200:
            print("Telegram message sent successfully via urequests")
            response.close()
            return True
        else:
            print(f"urequests failed with status code: {response.status_code}")
            response.close()
    except Exception as e:
        print(f"urequests approach failed: {e}")
    
    # Telegram Web API backup approach - no TLS, just HTTP
    try:
        print("Trying Telegram Bot API via HTTP (backup method)...")
        
        import socket
        import json
        
        # Create a plain socket (no SSL)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.settimeout(5)  # Short timeout
        
        # Connect to the Telegram API server on port 80 (HTTP)
        print("Connecting to api.telegram.org:80...")
        sock.connect(("api.telegram.org", 80))
        
        # URL-encode the message for HTTP
        encoded_message = message.replace(" ", "%20").replace("!", "%21")
        
        # Construct HTTP GET request
        request = (
            f"GET /bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_message} HTTP/1.1\r\n"
            "Host: api.telegram.org\r\n"
            "Connection: close\r\n\r\n"
        )
        
        # Send the request
        print("Sending HTTP request...")
        sock.send(request.encode())
        
        # Read the response
        print("Reading response...")
        response = b""
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                response += data
            except:
                break
        
        # Close the socket
        sock.close()
        
        # Process the response
        response_str = response.decode()
        
        # Check if the response contains a success indicator
        if "200 OK" in response_str and "true" in response_str:
            print("Telegram alert sent successfully via HTTP")
            return True
        else:
            print("HTTP method failed")
            print(response_str[:200] + "...")
            return False
            
    except Exception as e:
        print(f"HTTP method failed: {e}")
        return False
        
    # All methods failed
    return False

def send_ntfy_alert():
    """Send push notification via ntfy.sh (free service)"""
    print("Preparing Ntfy alert...")
    try:
        import urequests
        
        # Your unique topic - subscribe to this in the Ntfy app
        topic = config.NTFY_TOPIC
        url = f"https://ntfy.sh/{topic}"
        
        headers = {
            "Title": "SUMP ALARM!",
            "Priority": "urgent",
            "Tags": "warning,rotating_light"
        }
        
        message = "Water level is high! Check the sump pump immediately!"
        
        response = urequests.post(url, headers=headers, data=message, timeout=15)
        
        if response.status_code == 200:
            print("Ntfy alert sent successfully")
            response.close()
            return True
        else:
            print(f"Ntfy failed with status: {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"Ntfy alert failed: {e}")
        return False

def send_gmail_alert(recipients):
    """Send email alert using Gmail's SMTP server with App Password"""
    print("Preparing Gmail alert...")
    
    try:
        import email_sender
        
        # Force garbage collection before email send
        gc.collect()
        
        # Gmail credentials - replace with your own
        gmail_user = config.GMAIL_USER
        # App password (NOT your regular Gmail password)
        app_password = config.GMAIL_APP_PASSWORD  # No spaces
        
        # Create Gmail sender
        gmail = email_sender.GmailSender(gmail_user, app_password)
        
        # Email content
        subject = "URGENT: Sump Pump Alert!"
        message = "The water level in your sump is high! Please check the sump immediately!\n\n"
        message += f"Alert Time: {time.localtime()}\n"
        message += "Do not flush the toilet or run the water downstairs!\n\n"
        message += "This is an automated message from your Sump Pump Alarm system."
        
        print("Sending email via Gmail SMTP...")
        success = gmail.send_email(recipients, subject, message)
        
        if success:
            print(f"Email alert sent to {', '.join(recipients)}")
            return True
        else:
            print("Email alert failed")
            return False
            
    except Exception as e:
        print(f"Email alert error: {e}")
        return False

def send_notifications():
    """Send notifications through all configured channels"""
    success = False
    
    print_memory_status("Start of notifications")
    
    # Try to connect to WiFi first
    print("Connecting to WiFi...")
    if not connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        print("WiFi connection failed, cannot send notifications")
        return False
        
    print("WiFi connected")
    gc.collect()
    
    # Try Telegram first
    try:
        telegram_success = send_telegram_alert()
        if telegram_success:
            success = True
            print("Telegram notification succeeded")
    except Exception as e:
        print(f"Telegram module failure: {e}")
    
    # Force garbage collection between notification methods
    gc.collect()
    
    # Try Gmail next
    try:
        # List of email recipients (includes SMS via email gateway)
        recipients = config.EMAIL_RECIPIENTS
        email_success = send_gmail_alert(recipients)
        if email_success:
            success = True
            print("Gmail notification succeeded")
    except Exception as e:
        print(f"Gmail module failure: {e}")
    
    # Force garbage collection between notification methods
    gc.collect()
    
    # Try Ntfy (free push notification)
    try:
        ntfy_success = send_ntfy_alert()
        if ntfy_success:
            success = True
            print("Ntfy notification succeeded")
    except Exception as e:
        print(f"Ntfy module failure: {e}")
    
    print_memory_status("End of notifications")
    return success

# Debouncing configuration
DEBOUNCE_SECONDS = 15      # Switch must be on for this many seconds before alarm
SAMPLE_INTERVAL_MS = 100   # Sample interval in milliseconds for debouncing
SAMPLES_REQUIRED = 10      # Number of consecutive samples required to confirm state

def read_sensor_debounced(samples=SAMPLES_REQUIRED, interval_ms=SAMPLE_INTERVAL_MS):
    """Read sensor with debouncing - requires multiple consistent readings"""
    consistent_count = 0
    last_value = pin.value()
    
    for _ in range(samples):
        time.sleep_ms(interval_ms)
        current_value = pin.value()
        if current_value == last_value:
            consistent_count += 1
        else:
            consistent_count = 0
            last_value = current_value
    
    # Return the value only if we got consistent readings
    if consistent_count >= samples - 1:
        return last_value
    else:
        # Inconsistent readings - assume no water (fail-safe)
        return 0

# Initialization
print_memory_status("Startup")
notificationSent = False
notBuzzingYet = True
secondsFlooded = 0
alarmTriggered = False  # Track if we've already triggered the alarm

# Initialize GPIO
led = Pin(LED_PIN, Pin.OUT)

# Float switch: GPIO3 acts as virtual GND, GPIO4 is sensor input
# Switch is NORMALLY CLOSED (no water) and OPEN when water is HIGH
# - No water: switch closed, GPIO4 pulled to GND via GPIO3 → reads 0
# - Water HIGH: switch open, GPIO4 pulled HIGH by internal pull-up → reads 1
sensor_gnd = Pin(SENSOR_GND_PIN, Pin.OUT)
sensor_gnd.value(0)  # Set GPIO3 LOW to act as GND
pin = Pin(WATER_SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Water sensor input

tim = Timer(0)  # Use timer 0
in_a = Pin(SPEAKER_IN_A, Pin.OUT)  # To H-Bridge IN_A
in_b = Pin(SPEAKER_IN_B, Pin.OUT)  # To H-Bridge IN_B

print('ESP32-C3 Sump Alarm System Starting')
print('Version 2.2 - November 2025 (with debouncing)')
print(f'Debounce threshold: {DEBOUNCE_SECONDS} seconds')
blink_led(3)  # Signal startup
print_memory_status("After initialization")

# Forever loop
while True:
    time.sleep(1)
    
    # Use debounced sensor reading to filter out noise
    sensor_value = read_sensor_debounced()
    
    if sensor_value == 1:  # Water detected (adjust based on your sensor logic)
        secondsFlooded += 1
        print(f"Water detected for {secondsFlooded} seconds (alarm at {DEBOUNCE_SECONDS}s)")
        
        # Start alarm after DEBOUNCE_SECONDS of continuous detection
        if secondsFlooded == DEBOUNCE_SECONDS and not alarmTriggered:
            print('ALERT: Water level is high! (confirmed after debounce)')
            led.value(1)  # Solid LED to indicate alarm
            alarmTriggered = True
            
            # Start the buzzer
            notBuzzingYet = False
            tim.init(period=1, mode=Timer.PERIODIC, callback=alarmSound)
            
            # Try to send notifications
            try:
                notificationSent = send_notifications()
            except Exception as e:
                print("Notification error but alarm continues:", e)
        
        # Keep alarm on and retry notification every 10 minutes if first attempt failed
        elif secondsFlooded > DEBOUNCE_SECONDS:
            print('ALERT: Water level is high!')
            led.value(1)  # Solid LED for alarm
    
            # Ensure buzzer is on
            if notBuzzingYet:
                notBuzzingYet = False
                tim.init(period=1, mode=Timer.PERIODIC, callback=alarmSound)
                
            # Retry notification every 10 minutes if it failed before
            if not notificationSent and secondsFlooded % 600 == 0:
                try:
                    gc.collect()
                    notificationSent = send_notifications()
                except Exception as e:
                    print(f"Retry notification error: {e}")
    else:
        toggle(led)  # Blink LED in normal operation
        if secondsFlooded > 0:
            print(f"Water level restored (was high for {secondsFlooded}s, alarm triggered: {alarmTriggered})")
        
        secondsFlooded = 0
        notificationSent = False
        notBuzzingYet = True
        alarmTriggered = False  # Reset alarm state when water level returns to normal
        tim.deinit()  # Stop alarm sound


