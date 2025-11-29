"""
DNS and API Connection Tester for ESP8266
This script helps diagnose network connectivity issues specifically for the Telegram API
"""

import network
import socket
import time
import urequests
import gc

def memory_status():
    """Print memory usage information"""
    gc.collect()
    free_mem = gc.mem_free()
    alloc_mem = gc.mem_alloc()
    total = free_mem + alloc_mem
    print(f"Memory - Free: {free_mem} bytes, Used: {alloc_mem} bytes, Total: {total} bytes")
    print(f"Percent used: {alloc_mem / total * 100:.2f}%")

def wifi_connect(ssid, password):
    """Connect to WiFi and report status"""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected")
        print("IP:", wlan.ifconfig()[0])
        return True
    
    print(f"Connecting to {ssid}")
    wlan.connect(ssid, password)
    
    # Wait with timeout
    max_wait = 20
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
    
    if wlan.isconnected():
        print("Connected successfully!")
        print("IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Connection failed!")
        return False

def test_dns(domain):
    """Test DNS resolution for a domain"""
    print(f"\nResolving {domain}...")
    try:
        # Get address info
        addr_info = socket.getaddrinfo(domain, 80)
        print(f"Address info: {addr_info}")
        
        # Extract IP address
        ip = addr_info[0][-1][0]
        print(f"Resolved IP: {ip}")
        return ip
    except Exception as e:
        print(f"DNS resolution failed: {e}")
        return None

def test_http_connection(url):
    """Test HTTP connection to URL"""
    print(f"\nTesting HTTP connection to {url}")
    try:
        response = urequests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content length: {len(response.text)}")
        response.close()
        return True
    except Exception as e:
        print(f"HTTP connection failed: {e}")
        return False

def run_diagnostics():
    """Run all diagnostic tests"""
    print("\n=== ESP8266 Network Diagnostics ===\n")
    
    # Memory check
    print("Memory before tests:")
    memory_status()
    
    # WiFi test
    if not wifi_connect("Frohne-2.4GHz", ""):
        print("WiFi connection failed, cannot continue tests")
        return
    
    # DNS tests
    domains = ["google.com", "api.telegram.org", "api.pushover.net"]
    ips = {}
    
    for domain in domains:
        ip = test_dns(domain)
        if ip:
            ips[domain] = ip
    
    # HTTP connection tests
    if "google.com" in ips:
        test_http_connection(f"http://{ips['google.com']}")
    
    if "api.telegram.org" in ips:
        test_http_connection(f"http://{ips['api.telegram.org']}/")
    
    # Final memory check
    print("\nMemory after tests:")
    memory_status()

if __name__ == "__main__":
    run_diagnostics()
    print("\nDiagnostics complete!")
