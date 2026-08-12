import logging
import psutil
from typing import Dict, Any, Callable, List

logger = logging.getLogger(__name__)

class MobileMonitor:
    """
    Monitor system status mimicking mobile/embedded device metrics.
    Supports alert callbacks.
    """
    def __init__(self) -> None:
        self.alert_callbacks: List[Callable[[str, str], None]] = []

    def register_alert_callback(self, callback: Callable[[str, str], None]) -> None:
        """Register a callback to handle alerts (e.g. low battery)."""
        self.alert_callbacks.append(callback)

    def trigger_alert(self, level: str, message: str) -> None:
        """Trigger all registered alerts."""
        logger.warning(f"ALERT [{level}]: {message}")
        for callback in self.alert_callbacks:
            try:
                callback(level, message)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_battery_status(self) -> Dict[str, Any]:
        """
        Get battery status using psutil.
        """
        battery = psutil.sensors_battery()
        if battery is None:
            return {"status": "Unknown", "percent": None, "power_plugged": None}
        
        status = {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "time_left_secs": battery.secsleft
        }
        
        if battery.percent < 15 and not battery.power_plugged:
            self.trigger_alert("WARNING", "Battery is below 15%.")
            
        return status

    def get_network_status(self) -> Dict[str, Any]:
        """
        Get network I/O status using psutil.
        """
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }

    def get_storage_status(self) -> Dict[str, Any]:
        """
        Get storage status using psutil.
        """
        disk = psutil.disk_usage('/')
        
        if disk.percent > 90.0:
            self.trigger_alert("CRITICAL", "Storage usage exceeds 90%.")

        return {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "percent_used": disk.percent
        }
