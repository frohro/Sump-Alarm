"""
MicroPython Gmail SMTP Email Sender for ESP32
Uses Gmail's SMTP server with App Password authentication
"""

import socket
import ssl
import time
import gc
from mybase64 import b64encode  # Use our custom base64 implementation

class GmailSender:
    def __init__(self, gmail_user, app_password):
        """Initialize with Gmail username and App Password"""
        self.gmail_user = gmail_user
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # SSL port
        
    def _encode_base64(self, message):
        """Encode a string to base64"""
        return b64encode(message)
    
    def send_email(self, to_emails, subject, message):
        """Send email through Gmail SMTP"""
        # Convert single email address to list if needed
        if isinstance(to_emails, str):
            to_emails = [to_emails]
            
        # Format recipient list for SMTP
        recipients_str = ", ".join(to_emails)
        
        # Create socket and wrap with SSL
        print("Creating socket connection to Gmail...")
        server = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            
            # First resolve the hostname
            print(f"Resolving {self.smtp_server}...")
            addr_info = socket.getaddrinfo(self.smtp_server, self.smtp_port)[0]
            addr = addr_info[-1]
            print(f"Resolved to {addr}")
            
            # Connect the plain socket first
            print(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            sock.connect(addr)
            
            # Now wrap with SSL after connection
            print("Wrapping with SSL...")
            server = ssl.wrap_socket(sock, server_hostname=self.smtp_server)
            
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            if not response.startswith('220'):
                raise Exception("SMTP Server not ready")
            
            # Say HELLO
            print("Sending EHLO...")
            server.send(b'EHLO ESP32-C3-Sump-Alarm\r\n')
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Login: Authentication
            print("Authenticating...")
            server.send(b'AUTH LOGIN\r\n')
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Free memory before encoding
            gc.collect()
            
            # Send username (base64 encoded)
            server.send((self._encode_base64(self.gmail_user) + '\r\n').encode())
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Free memory before encoding
            gc.collect()
            
            # Send password (base64 encoded)
            server.send((self._encode_base64(self.app_password) + '\r\n').encode())
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            if not response.startswith('235'):
                raise Exception("Authentication failed")
            
            # Set sender
            print("Setting sender...")
            server.send(f'MAIL FROM: <{self.gmail_user}>\r\n'.encode())
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Set recipients
            print("Setting recipients...")
            for email in to_emails:
                server.send(f'RCPT TO: <{email}>\r\n'.encode())
                response = server.recv(1024).decode()
                print(f"Server response for {email}:", response)
                
                if not response.startswith('250'):
                    print(f"Warning: Recipient {email} not accepted")
            
            # Start data transmission
            print("Starting data transmission...")
            server.send(b'DATA\r\n')
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Construct email headers and content
            email_message = (
                f"From: Sump Alarm <{self.gmail_user}>\r\n"
                f"To: {recipients_str}\r\n"
                f"Subject: {subject}\r\n"
                f"Content-Type: text/plain; charset=utf-8\r\n"
                f"\r\n"
                f"{message}\r\n"
                f".\r\n"  # End of message indicator
            )
            
            # Send the email content
            server.send(email_message.encode())
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            if not response.startswith('250'):
                raise Exception("Email not accepted by server")
            
            # Quit the session
            print("Closing connection...")
            server.send(b'QUIT\r\n')
            response = server.recv(1024).decode()
            print("Server response:", response)
            
            # Close socket
            server.close()
            print("Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            if server:
                try:
                    server.close()
                except:
                    pass
            return False
