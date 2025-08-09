#!/usr/bin/env python
"""
Simple test script to verify the Django backend is working
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from streams.models import Stream
from streams.serializers import StreamSerializer

def test_basic_setup():
    """Test basic Django setup"""
    print("Testing basic Django setup...")
    
    # Test that we can import and create a Stream object
    try:
        stream = Stream(
            url="rtsp://test.example.com/stream",
            label="Test Stream"
        )
        print(f"✓ Successfully created Stream object: {stream}")
        return True
    except Exception as e:
        print(f"✗ Error creating Stream object: {e}")
        return False

def test_serializer():
    """Test serializer functionality"""
    print("\nTesting serializer...")
    
    try:
        data = {
            'url': 'rtsp://test.example.com/stream',
            'label': 'Test Stream'
        }
        serializer = StreamSerializer(data=data)
        if serializer.is_valid():
            print("✓ Serializer validation successful")
            return True
        else:
            print(f"✗ Serializer validation failed: {serializer.errors}")
            return False
    except Exception as e:
        print(f"✗ Error testing serializer: {e}")
        return False

def test_settings():
    """Test Django settings"""
    print("\nTesting Django settings...")
    
    try:
        from django.conf import settings
        
        # Check essential settings
        required_settings = [
            'SECRET_KEY',
            'DEBUG',
            'INSTALLED_APPS',
            'DATABASES',
            'ASGI_APPLICATION',
            'CHANNEL_LAYERS'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                print(f"✓ {setting} is configured")
            else:
                print(f"✗ {setting} is missing")
                return False
        
        # Check that streams app is in INSTALLED_APPS
        if 'streams' in settings.INSTALLED_APPS:
            print("✓ streams app is in INSTALLED_APPS")
        else:
            print("✗ streams app is not in INSTALLED_APPS")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Error testing settings: {e}")
        return False

if __name__ == '__main__':
    print("RTSP Stream Viewer Backend Test")
    print("=" * 40)
    
    tests = [
        test_settings,
        test_basic_setup,
        test_serializer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
