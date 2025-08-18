"""
Test script for Windows executable build.
Verifies that the application starts correctly and all components work.
"""

import sys
import os
import subprocess
import time
from pathlib import Path


class WindowsAppTester:
    """Test the Windows executable build."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.deployment_root = Path(__file__).parent.parent
        self.dist_dir = self.deployment_root / "ready_to_deploy" / "DentalPracticeManager"
        self.exe_path = self.dist_dir / "DentalPracticeManager.exe"
    
    def test_executable_exists(self):
        """Test if the executable was created."""
        print("🔍 Testing executable existence...")
        
        if not self.exe_path.exists():
            print(f"❌ Executable not found: {self.exe_path}")
            return False
        
        print(f"✅ Executable found: {self.exe_path}")
        
        # Check file size (should be reasonable)
        size_mb = self.exe_path.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.1f} MB")
        
        if size_mb < 10:
            print("⚠️  Warning: Executable seems too small, may be missing dependencies")
        elif size_mb > 500:
            print("⚠️  Warning: Executable is quite large, consider optimization")
        
        return True
    
    def test_dependencies(self):
        """Test if all required dependencies are included."""
        print("🔍 Testing dependencies...")
        
        required_files = [
            "DentalPracticeManager.exe",
            "launch.bat",
        ]
        
        # Check for PySide6 DLLs
        pyside_dlls = list(self.dist_dir.glob("*Qt*.dll"))
        if not pyside_dlls:
            print("❌ PySide6 DLLs not found")
            return False
        
        print(f"✅ Found {len(pyside_dlls)} PySide6 DLLs")
        
        # Check for Python runtime
        python_files = list(self.dist_dir.glob("python*.dll"))
        if not python_files:
            print("❌ Python runtime not found")
            return False
        
        print("✅ Python runtime found")
        
        # Check for required files
        missing_files = []
        for file_name in required_files:
            file_path = self.dist_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        print("✅ All required files present")
        return True
    
    def test_startup_time(self):
        """Test application startup time."""
        print("🔍 Testing startup performance...")
        
        if not self.exe_path.exists():
            print("❌ Cannot test startup - executable not found")
            return False
        
        try:
            # Start the application and measure time
            start_time = time.time()
            
            # Use the launcher script for optimized startup
            launcher_path = self.dist_dir / "launch.bat"
            if launcher_path.exists():
                cmd = [str(launcher_path)]
            else:
                cmd = [str(self.exe_path)]
            
            # Start process but don't wait for it to finish
            process = subprocess.Popen(
                cmd,
                cwd=self.dist_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a short time to see if it starts
            time.sleep(3)
            
            startup_time = time.time() - start_time
            
            # Check if process is still running (good sign)
            if process.poll() is None:
                print(f"✅ Application started successfully in {startup_time:.1f}s")
                
                # Terminate the test process
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
                
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Application failed to start")
                if stderr:
                    print(f"   Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Startup test failed: {e}")
            return False
    
    def test_windows_compatibility(self):
        """Test Windows compatibility features."""
        print("🔍 Testing Windows compatibility...")
        
        # Check for manifest file
        manifest_path = self.exe_path.with_suffix('.exe.manifest')
        if manifest_path.exists():
            print("✅ Windows compatibility manifest found")
            
            # Check manifest content
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
                
            if 'Windows 8' in manifest_content:
                print("✅ Windows 8+ compatibility declared")
            else:
                print("⚠️  Windows 8+ compatibility not declared")
                
            if 'dpiAware' in manifest_content:
                print("✅ DPI awareness configured")
            else:
                print("⚠️  DPI awareness not configured")
        else:
            print("⚠️  Windows compatibility manifest not found")
        
        return True
    
    def test_deployment_structure(self):
        """Test deployment folder structure."""
        print("🔍 Testing deployment structure...")
        
        # Check if deployment folder exists
        if not self.dist_dir.exists():
            print(f"❌ Deployment folder not found: {self.dist_dir}")
            return False
        
        print(f"✅ Deployment folder found: {self.dist_dir}")
        
        # List all files for verification
        files = list(self.dist_dir.rglob("*"))
        print(f"   Total files: {len([f for f in files if f.is_file()])}")
        print(f"   Total folders: {len([f for f in files if f.is_dir()])}")
        
        return True
    
    def run_tests(self):
        """Run all tests."""
        print("🧪 Testing Windows Application Build")
        print("=" * 50)
        
        tests = [
            ("Deployment Structure", self.test_deployment_structure),
            ("Executable Creation", self.test_executable_exists),
            ("Dependencies", self.test_dependencies),
            ("Windows Compatibility", self.test_windows_compatibility),
            ("Startup Performance", self.test_startup_time),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results:
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{status} - {test_name}")
            if passed_test:
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your Windows application is ready.")
            print(f"\n📁 Deployment folder: {self.dist_dir}")
            print(f"🚀 Run the application: {self.exe_path}")
            print(f"⚡ For best performance, use: {self.dist_dir / 'launch.bat'}")
        else:
            print("⚠️  Some tests failed. Please review the build.")
        
        return passed == total


if __name__ == "__main__":
    tester = WindowsAppTester()
    success = tester.run_tests()
    
    print("\n" + "=" * 50)
    input("Press Enter to exit...")
    
    sys.exit(0 if success else 1)
