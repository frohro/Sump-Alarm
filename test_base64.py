"""
Simple test for mybase64 module
"""

from mybase64 import b64encode

def test_base64():
    # Test cases
    print("Testing base64 encoding...")
    
    test_strings = [
        "hello",
        "test123",
        "kl7na.pskmail@gmail.com",
        "vcwr reyq ckve oobye"
    ]
    
    expected_outputs = [
        "aGVsbG8=",
        "dGVzdDEyMw==",
        "a2w3bmEucHNrbWFpbEBnbWFpbC5jb20=",
        "dmN3ciByZXlxIGNrdmUgb29ieWU="
    ]
    
    for i, test_str in enumerate(test_strings):
        encoded = b64encode(test_str)
        print(f"Input: {test_str}")
        print(f"Output: {encoded}")
        print(f"Expected: {expected_outputs[i]}")
        print(f"Match: {encoded == expected_outputs[i]}\n")
    
    print("Test completed")

# Run test when imported
test_base64()
