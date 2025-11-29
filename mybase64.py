"""
Simple Base64 encoder implementation for MicroPython when base64 module is not available
"""

# Base64 encoding table
_b64_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def b64encode(data):
    """Encode bytes or string to base64 string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    result = []
    data_len = len(data)
    
    for i in range(0, data_len, 3):
        # Get up to 3 bytes
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < data_len else 0
        b3 = data[i + 2] if i + 2 < data_len else 0
        
        # Convert to 4 base64 characters
        result.append(_b64_alphabet[b1 >> 2])
        result.append(_b64_alphabet[((b1 & 0x03) << 4) | (b2 >> 4)])
        
        if i + 1 < data_len:
            result.append(_b64_alphabet[((b2 & 0x0F) << 2) | (b3 >> 6)])
        else:
            result.append('=')
            
        if i + 2 < data_len:
            result.append(_b64_alphabet[b3 & 0x3F])
        else:
            result.append('=')
    
    return ''.join(result)
