#!/usr/bin/env python3
"""
Simple test script to check credentials and basic functionality
This version doesn't require external dependencies
"""

import json
import os
import sys

def test_credentials():
    """Test that credentials file exists and is valid JSON"""
    print("🔍 Testing Gmail API credentials...")

    credentials_path = 'config/credentials.json'

    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return False

    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)

        # Check for required fields
        if 'installed' in creds:
            client_info = creds['installed']
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']

            for field in required_fields:
                if field not in client_info:
                    print(f"❌ Missing required field in credentials: {field}")
                    return False

            print(f"✅ Credentials file is valid")
            print(f"   Client ID: {client_info['client_id'][:20]}...")
            return True
        else:
            print("❌ Credentials file format not recognized")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")

    env_path = '.env'

    if not os.path.exists(env_path):
        print(f"❌ Environment file not found: {env_path}")
        return False

    try:
        with open(env_path, 'r') as f:
            content = f.read()

        if 'DRAFT_MODE=true' in content:
            print("✅ Draft mode enabled (safe)")
        elif 'DRAFT_MODE=false' in content:
            print("⚠️  Draft mode disabled - will send emails directly")
        else:
            print("✅ Draft mode not explicitly set (defaults to safe mode)")

        print(f"✅ Environment file exists")
        return True

    except Exception as e:
        print(f"❌ Error reading environment file: {e}")
        return False

def check_missing_dependencies():
    """Check what dependencies are missing"""
    print("\n🔍 Checking Python dependencies...")

    required_modules = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'yaml',
        'dotenv'
    ]

    missing = []
    available = []

    for module in required_modules:
        try:
            __import__(module)
            available.append(module)
        except ImportError:
            missing.append(module)

    if available:
        print(f"✅ Available modules: {', '.join(available)}")

    if missing:
        print(f"❌ Missing modules: {', '.join(missing)}")
        print("\nTo install missing dependencies, you'll need to:")
        print("1. Install pip first")
        print("2. Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required modules are available!")
        return True

def provide_next_steps():
    """Provide next steps based on current status"""
    print("\n" + "="*50)
    print("📋 NEXT STEPS")
    print("="*50)

    print("\n1. 📦 Install Python dependencies:")
    print("   Try one of these methods:")
    print("   • flatpak install flathub org.freedesktop.Sdk.Extension.python3")
    print("   • Download dependencies manually")
    print("   • Use a Python virtual environment")

    print("\n2. 🧪 Test the application:")
    print("   python3 src/main.py --validate")

    print("\n3. 🏃 First run (test mode):")
    print("   python3 src/main.py --once --test-mode")

    print("\n4. 📝 Production run (draft mode):")
    print("   python3 src/main.py --once --draft-mode")

    print("\n5. 📧 Check Gmail drafts folder for generated responses")

def main():
    """Run all tests"""
    print("🚀 Gmail Auto-Responder Setup Validation")
    print("=" * 50)

    all_good = True

    # Test credentials
    if not test_credentials():
        all_good = False

    # Test environment
    if not test_environment():
        all_good = False

    # Check dependencies
    deps_available = check_missing_dependencies()
    if not deps_available:
        all_good = False

    print("\n" + "="*50)
    if all_good:
        print("🎉 SETUP COMPLETE! Ready to run Gmail Auto-Responder")
        print("\nTry: python3 src/main.py --once --test-mode")
    else:
        print("⚠️  SETUP PARTIALLY COMPLETE")
        print("Your credentials are ready, but dependencies need to be installed.")
        provide_next_steps()

if __name__ == '__main__':
    main()