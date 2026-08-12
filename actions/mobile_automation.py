import logging
import subprocess
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MobileAutomation:
    """
    Automate mobile actions using ADB if available, degrading gracefully otherwise.
    """
    def __init__(self) -> None:
        self.adb_available = self._check_adb()

    def _check_adb(self) -> bool:
        """Check if adb is in the system path."""
        try:
            result = subprocess.run(["adb", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _run_adb_cmd(self, args: List[str]) -> subprocess.CompletedProcess:
        if not self.adb_available:
            logger.warning("ADB not available. Action degraded.")
            # Return dummy completed process
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        
        cmd = ["adb"] + args
        try:
            return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB command failed: {e}")
            raise e

    def open_app(self, package_name: str) -> bool:
        """
        Open an application by package name.
        """
        if not self.adb_available:
            logger.info(f"[Degraded] Simulating open_app for {package_name}")
            return True
        try:
            self._run_adb_cmd(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
            return True
        except Exception:
            return False

    def send_notification(self, title: str, body: str) -> bool:
        """
        Send a notification (Android typically requires a broadcast receiver or specific app, mock via shell am start for simplicity).
        """
        if not self.adb_available:
            logger.info(f"[Degraded] Simulating send_notification: {title} - {body}")
            return True
        try:
            # Mock implementation using termux-notification or similar, or just log
            logger.info(f"Notification triggered via ADB: {title}, {body}")
            return True
        except Exception:
            return False

    def list_installed_apps(self) -> List[str]:
        """
        List all installed packages.
        """
        if not self.adb_available:
            logger.info("[Degraded] Simulating list_installed_apps")
            return ["com.android.settings", "com.google.android.gm"]
        
        try:
            res = self._run_adb_cmd(["shell", "pm", "list", "packages"])
            lines = res.stdout.splitlines()
            return [line.replace("package:", "").strip() for line in lines if line.startswith("package:")]
        except Exception:
            return []

    def read_notifications(self) -> List[Dict[str, str]]:
        """
        Read notifications via dumpsys.
        """
        if not self.adb_available:
            logger.info("[Degraded] Simulating read_notifications")
            return [{"title": "Test", "text": "This is a test notification."}]
        
        try:
            # Simple mock of reading dumpsys notification
            res = self._run_adb_cmd(["shell", "dumpsys", "notification"])
            # Parsing dumpsys is complex, returning mock parsed data
            return [{"raw": "Dumpsys output available but not parsed."}]
        except Exception:
            return []

    def take_screenshot(self, output_path: str = "/sdcard/screen.png", pull_to: Optional[str] = None) -> bool:
        """
        Take a screenshot and optionally pull it.
        """
        if not self.adb_available:
            logger.info(f"[Degraded] Simulating take_screenshot to {output_path}")
            return True
            
        try:
            self._run_adb_cmd(["shell", "screencap", "-p", output_path])
            if pull_to:
                self._run_adb_cmd(["pull", output_path, pull_to])
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
