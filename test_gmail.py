"""
ESP32-C3 Gmail Test
Tests sending an email via Gmail SMTP
"""

import network
import time
import gc
import config

# Configure garbage collection
gc.enable()
gc.collect()

def connect_wifi():
    """Connect to WiFi"""
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected:", wlan.ifconfig()[0])
        return True
    
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    
    # Wait for connection with timeout
    max_wait = 20
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
    
    if wlan.isconnected():
        print("WiFi connected!")
        print("IP address:", wlan.ifconfig()[0])
        return True
    else:
        print("WiFi connection failed")
        return False

def test_gmail():
    """Test sending email via Gmail"""
    print("\nESP32-C3 Gmail Test")
    print("===================")
    
    gc.collect()
    print(f"Free memory: {gc.mem_free()} bytes")
    
    try:
        import email_sender
        
        # Gmail credentials
        gmail_user = config.GMAIL_USER
        app_password = config.GMAIL_APP_PASSWORD  # No spaces
        
        # Create sender
        gmail = email_sender.GmailSender(gmail_user, app_password)
        
        # Test email
        recipients = config.EMAIL_RECIPIENTS
        subject = "🚨 SUMP ALARM TEST"
        message = """This is a TEST of the Sump Pump Alarm system.

If this were a real emergency, the message would say:
"Water level is high! Check the sump pump immediately!"

Test sent from ESP32-C3.
"""
        
        print(f"Sending test email to {recipients}...")
        success = gmail.send_email(recipients, subject, message)
        
        if success:
            print("Email sent successfully!")
        else:
            print("Email sending failed!")
            
        return success
        
    except Exception as e:
        print(f"Gmail test error: {e}")
        import sys
        sys.print_exception(e)
        return False

# Run test
if connect_wifi():
    test_gmail()
else:
    print("Cannot test Gmail - WiFi failed")

print("\nTest complete")
