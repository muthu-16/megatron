import logging
import hashlib
from typing import Optional

logger = logging.getLogger(__name__)

class SettingsController:
    """
    Manages sensitive system settings and requires password confirmation for critical actions.
    """
    def __init__(self, admin_password_hash: str = "", auth_manager=None, memory_manager=None, session_store=None) -> None:
        self.admin_password_hash = admin_password_hash
        self.auth_manager = auth_manager      # optional AuthManager for bcrypt-based verification
        self.memory_manager = memory_manager  # optional MemoryManager
        self.session_store = session_store    # optional SessionStore
        self.lock_mode = False

    def _verify_password(self, password: str) -> bool:
        """
        Verify the provided password against the stored hash.
        """
        if not password:
            return False
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        return pwd_hash == self.admin_password_hash

    def reset_to_factory(self, password: str) -> bool:
        if not self._verify_password(password):
            logger.error("Authentication failed for factory reset.")
            return False
        logger.warning("Performing factory reset...")
        # Mock logic
        return True

    def delete_all_memory(self, password: str) -> bool:
        if not self._verify_password(password):
            logger.error("Authentication failed for memory deletion.")
            return False
        logger.warning("Deleting all memory...")
        # Mock logic
        return True

    def delete_history(self, password: str) -> bool:
        if not self._verify_password(password):
            logger.error("Authentication failed for history deletion.")
            return False
        logger.info("Deleting history...")
        # Mock logic
        return True

    def unlink_device(self, password: str, device_id: str) -> bool:
        if not self._verify_password(password):
            logger.error("Authentication failed for unlinking device.")
            return False
        logger.info(f"Unlinking device: {device_id}...")
        # Mock logic
        return True

    def change_password(self, old_password: str, new_password: str) -> bool:
        if not self._verify_password(old_password):
            logger.error("Authentication failed for password change.")
            return False
        self.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        logger.info("Password changed successfully.")
        return True

    def toggle_lock_mode(self, password: str) -> bool:
        if not self._verify_password(password):
            logger.error("Authentication failed for toggling lock mode.")
            return False
        self.lock_mode = not self.lock_mode
        logger.info(f"Lock mode toggled. Now active: {self.lock_mode}")
        return True
