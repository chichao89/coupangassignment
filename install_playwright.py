#!/usr/bin/env python3
"""
Script to install Playwright browsers
Run this after installing the package to download browser binaries
"""

import sys
import subprocess
import logging

def install_playwright_browsers():
    """Install Playwright browser binaries"""
    print("🚀 Installing Playwright browsers...")
    print("This may take a few minutes as it downloads browser binaries.")
    print("-" * 60)
    
    try:
        # Install Playwright browsers
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Playwright browsers installed successfully!")
        print(result.stdout)
        
        # Install system dependencies (Linux)
        if sys.platform.startswith('linux'):
            print("\n🔧 Installing system dependencies for Linux...")
            deps_result = subprocess.run([
                sys.executable, "-m", "playwright", "install-deps"
            ], capture_output=True, text=True)
            
            if deps_result.returncode == 0:
                print("✅ System dependencies installed successfully!")
            else:
                print("⚠️  System dependencies installation completed with warnings:")
                print(deps_result.stderr)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    success = install_playwright_browsers()
    
    if success:
        print("\n🎉 Setup complete! You can now use the Playwright scraper.")
        print("\nTo test the installation, run:")
        print("  python main.py example quotes_toscrape --scraper-type playwright")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        print("You may need to install Playwright manually:")
        print("  pip install playwright")
        print("  playwright install")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())