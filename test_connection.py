"""
Connection test utility for ESP32-C3
Tests basic network connectivity to various services
"""

import network
import socket
import time
import gc
import config

def run_connection_tests():
    """Run comprehensive connection tests"""
    print("ESP32-C3 Connection Test Utility")
    print("================================")
    
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(0.5)
    
    if wlan.isconnected():
        print("WiFi connected!")
        print(f"IP address: {wlan.ifconfig()[0]}")
        print(f"Subnet mask: {wlan.ifconfig()[1]}")
        print(f"Gateway: {wlan.ifconfig()[2]}")
        print(f"DNS server: {wlan.ifconfig()[3]}")
    else:
        print("WiFi connection failed!")
        return
    
    # DNS resolution test
    print("\n1. Testing DNS Resolution")
    print("------------------------")
    hosts = [
        "google.com",
        "api.telegram.org",
        "smtp.gmail.com"
    ]
    
    for host in hosts:
        try:
            print(f"Looking up {host}...")
            addr_info = socket.getaddrinfo(host, 0)
            print(f"Success! {host} resolves to {addr_info[0][-1][0]}")
        except Exception as e:
            print(f"Failed to resolve {host}: {e}")
    
    # HTTP connection test (port 80)
    print("\n2. Testing HTTP Connection")
    print("------------------------")
    http_hosts = [
        ("google.com", 80),
        ("api.telegram.org", 80)
    ]
    
    for host, port in http_hosts:
        try:
            print(f"Connecting to {host}:{port}...")
            s = socket.socket()
            s.settimeout(5)
            s.connect((host, port))
            print(f"Connected to {host}:{port} successfully!")
            s.close()
        except Exception as e:
            print(f"Failed to connect to {host}:{port}: {e}")
    
    # HTTPS connection test (port 443)
    print("\n3. Testing HTTPS Connection")
    print("-------------------------")
    https_hosts = [
        ("google.com", 443),
        ("api.telegram.org", 443),
        ("smtp.gmail.com", 465)
    ]
    
    for host, port in https_hosts:
        try:
            print(f"Connecting to {host}:{port}...")
            s = socket.socket()
            s.settimeout(5)
            
            # Try to establish SSL connection
            print(f"Setting up SSL for {host}:{port}...")
            import ssl
            ss = ssl.wrap_socket(s, server_hostname=host)
            
            print(f"Connecting to {host}:{port}...")
            ss.connect((host, port))
            print(f"Connected to {host}:{port} successfully!")
            ss.close()
        except Exception as e:
            print(f"Failed to connect to {host}:{port}: {e}")
    
    print("\nTest completed!")
    gc.collect()

# Run the tests when imported
run_connection_tests()
