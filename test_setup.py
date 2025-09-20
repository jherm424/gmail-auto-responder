#!/usr/bin/env python3
"""
Basic setup test without dependencies
Tests the project structure and configuration files
"""

import os
import sys

def test_project_structure():
    """Test that all required files and directories exist"""
    print("🔍 Testing project structure...")

    required_files = [
        'README.md',
        'requirements.txt',
        '.env.example',
        'config/response_rules.yaml',
        'templates/general.txt',
        'templates/business_inquiry.txt',
        'templates/job_application.txt',
        'src/main.py',
        'src/gmail_auth.py',
        'src/email_monitor.py',
        'src/response_generator.py',
        'setup_instructions.md'
    ]

    required_dirs = [
        'src',
        'config',
        'templates',
        'logs',
        'tests'
    ]

    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Missing directory: {directory}")
            return False

    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False

    return True

def test_configuration():
    """Test configuration file format"""
    print("\n🔍 Testing configuration...")

    try:
        # Test YAML configuration (basic parsing without PyYAML)
        with open('config/response_rules.yaml', 'r') as f:
            content = f.read()
            if 'rules:' in content and 'exclusions:' in content:
                print("✅ Configuration file format looks correct")
            else:
                print("❌ Configuration file missing required sections")
                return False

    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

    return True

def test_templates():
    """Test template files"""
    print("\n🔍 Testing templates...")

    templates = ['general', 'business_inquiry', 'job_application']

    for template in templates:
        template_path = f'templates/{template}.txt'
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                if content.strip().startswith('Subject:'):
                    print(f"✅ Template format correct: {template}")
                else:
                    print(f"❌ Template missing Subject line: {template}")
                    return False
        except Exception as e:
            print(f"❌ Error reading template {template}: {e}")
            return False

    return True

def test_python_syntax():
    """Test Python files for syntax errors"""
    print("\n🔍 Testing Python syntax...")

    python_files = [
        'src/main.py',
        'src/gmail_auth.py',
        'src/email_monitor.py',
        'src/response_generator.py'
    ]

    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                # Basic compile test
                compile(content, py_file, 'exec')
                print(f"✅ Syntax OK: {py_file}")
        except SyntaxError as e:
            print(f"❌ Syntax error in {py_file}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error checking {py_file}: {e}")
            return False

    return True

def main():
    """Run all tests"""
    print("🚀 Gmail Auto-Responder Setup Test")
    print("=" * 40)

    tests = [
        ("Project Structure", test_project_structure),
        ("Configuration", test_configuration),
        ("Templates", test_templates),
        ("Python Syntax", test_python_syntax)
    ]

    all_passed = True

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        if not test_func():
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Project setup is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Get Gmail API credentials from Google Cloud Console")
        print("3. Place credentials.json in config/ directory")
        print("4. Copy .env.example to .env and configure")
        print("5. Run: python src/main.py --validate")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()