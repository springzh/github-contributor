#!/usr/bin/env python3
"""
Test script for GitHub API connectivity
"""

import requests
import ssl
import socket
from urllib.parse import urlparse

def test_github_api():
    """Test GitHub API connectivity with SSL configuration"""
    print("Testing GitHub API connectivity...")
    
    try:
        # Test basic connectivity
        url = "https://api.github.com/rate_limit"
        
        # Configure session with SSL settings
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Blockchain-Contributors-Extractor-Test'
        })
        session.timeout = 30
        
        print(f"Connecting to: {url}")
        response = session.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Rate limit info: {data.get('rate', {})}")
            print("✅ GitHub API connection successful!")
            return True
        else:
            print(f"❌ GitHub API connection failed: {response.text}")
            return False
            
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("This might be due to SSL/TLS configuration issues")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("This might be due to network connectivity issues")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        print("The request took too long to complete")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_ssl_context():
    """Test SSL context configuration"""
    print("\nTesting SSL context...")
    
    try:
        # Test SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Test connection to GitHub
        hostname = "api.github.com"
        port = 443
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"✅ SSL connection to {hostname} successful!")
                print(f"SSL Version: {ssock.version()}")
                print(f"Cipher: {ssock.cipher()}")
                return True
                
    except Exception as e:
        print(f"❌ SSL context test failed: {e}")
        return False

if __name__ == "__main__":
    print("GitHub API Connectivity Test")
    print("=" * 50)
    
    # Test basic API connectivity
    api_success = test_github_api()
    
    # Test SSL context
    ssl_success = test_ssl_context()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"GitHub API: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"SSL Context: {'✅ PASS' if ssl_success else '❌ FAIL'}")
    
    if api_success and ssl_success:
        print("\n🎉 All tests passed! The GitHub API is accessible.")
    else:
        print("\n⚠️  Some tests failed. Check your network connection and SSL configuration.")