"""Canary Token Exfiltration Detection Sentinel.
100% Python Standard Library.
"""

import hmac
import hashlib

class CanaryTokenSentinel:
    """HMAC-authenticated canary token generator and leak detector."""
    def __init__(self, secret_key="alpha_canary_secret"):
        self.secret_key = secret_key.encode("utf-8")

    def generate_canary(self, session_id):
        tag = f"CANARY_{session_id}".encode("utf-8")
        sig = hmac.new(self.secret_key, tag, hashlib.sha256).hexdigest()[:16]
        return f"CANARY_TOKEN_{session_id}_{sig}"

    def detect_leak(self, text, canary_token):
        return canary_token in text
