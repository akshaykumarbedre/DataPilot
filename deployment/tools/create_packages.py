"""
Deployment package creator for Dental Practice Manager.
Creates a zip package ready for distribution.
"""

import zipfile
import shutil
import os
from pathlib import Path
from datetime import datetime


class DeploymentPackager:
    """Creates deployment packages."""
    
    def __init__(self):
        self.deployment_root = Path(__file__).parent.parent
        self.app_dir = self.deployment_root / "ready_to_deploy" / "DentalPracticeManager"
        self.packages_dir = self.deployment_root / "packages"
        
    def create_package(self, package_type="standalone"):
        """Create deployment package."""
        print(f"📦 Creating {package_type} deployment package...")
        
        if not self.app_dir.exists():
            print("❌ Application not found! Please build first.")
            return False
        
        # Create packages directory
        self.packages_dir.mkdir(exist_ok=True)
        
        # Create timestamp for version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if package_type == "standalone":
            return self._create_standalone_package(timestamp)
        elif package_type == "portable":
            return self._create_portable_package(timestamp)
        else:
            print(f"❌ Unknown package type: {package_type}")
            return False
    
    def _create_standalone_package(self, timestamp):
        """Create standalone application package."""
        package_name = f"DentalPracticeManager_Standalone_{timestamp}.zip"
        package_path = self.packages_dir / package_name
        
        print(f"   Creating: {package_name}")
        
        try:
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all application files
                for file_path in self.app_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.app_dir.parent)
                        zipf.write(file_path, arcname)
                
                # Add documentation
                docs_dir = self.deployment_root / "docs"
                if docs_dir.exists():
                    for doc_file in docs_dir.glob("*.md"):
                        zipf.write(doc_file, f"docs/{doc_file.name}")
                
                # Add README for the package
                readme_content = f"""# Dental Practice Manager - Standalone Package
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Installation
1. Extract this ZIP file to your desired location
2. Run DentalPracticeManager\\launch.bat for best performance
3. Or run DentalPracticeManager\\DentalPracticeManager.exe directly

## Requirements
- Windows 8 or later
- No additional installation required

## Files
- DentalPracticeManager\\: Main application folder
- docs\\: Documentation files

For support and updates, contact: support@dentalsolutions.com
"""
                
                zipf.writestr("README.txt", readme_content)
            
            print(f"✅ Standalone package created: {package_path}")
            print(f"   Size: {package_path.stat().st_size / (1024*1024):.1f} MB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create package: {e}")
            return False
    
    def _create_portable_package(self, timestamp):
        """Create portable application package."""
        package_name = f"DentalPracticeManager_Portable_{timestamp}.zip"
        package_path = self.packages_dir / package_name
        
        print(f"   Creating: {package_name}")
        
        try:
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add application files with portable structure
                for file_path in self.app_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = f"DentalPracticeManager_Portable/{file_path.relative_to(self.app_dir)}"
                        zipf.write(file_path, arcname)
                
                # Create portable launcher
                portable_launcher = """@echo off
REM Dental Practice Manager Portable Launcher
cd /d "%~dp0"
set PORTABLE_MODE=1
start "Dental Practice Manager" /HIGH "DentalPracticeManager.exe"
"""
                zipf.writestr("DentalPracticeManager_Portable/run_portable.bat", portable_launcher)
                
                # Add portable README
                portable_readme = f"""# Dental Practice Manager - Portable Edition
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Running Portable Version
1. Extract this ZIP file to any location (USB drive, folder, etc.)
2. Run run_portable.bat to start the application
3. All data will be stored in the application folder

## Features
- No installation required
- Runs from USB drives
- Data stored locally with application
- Windows 8+ compatible

## Files
- DentalPracticeManager.exe: Main application
- run_portable.bat: Portable launcher (recommended)
- launch.bat: Optimized launcher
- data/: Database files (created on first run)

This is a portable version that can run from any location.
"""
                
                zipf.writestr("DentalPracticeManager_Portable/README_PORTABLE.txt", portable_readme)
            
            print(f"✅ Portable package created: {package_path}")
            print(f"   Size: {package_path.stat().st_size / (1024*1024):.1f} MB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create portable package: {e}")
            return False
    
    def create_all_packages(self):
        """Create all package types."""
        print("📦 Creating all deployment packages...")
        print("=" * 50)
        
        success_count = 0
        
        packages = [
            ("standalone", "Standalone Application"),
            ("portable", "Portable Application"),
        ]
        
        for package_type, description in packages:
            print(f"\n📋 {description}")
            print("-" * 30)
            
            if self.create_package(package_type):
                success_count += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Package Creation Summary: {success_count}/{len(packages)} successful")
        
        if success_count == len(packages):
            print("🎉 All packages created successfully!")
            print(f"📁 Packages folder: {self.packages_dir}")
        else:
            print("⚠️  Some packages failed to create.")
        
        return success_count == len(packages)


if __name__ == "__main__":
    packager = DeploymentPackager()
    success = packager.create_all_packages()
    
    print("\n" + "=" * 50)
    input("Press Enter to exit...")
    
    import sys
    sys.exit(0 if success else 1)
