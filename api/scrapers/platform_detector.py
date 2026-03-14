"""Platform detector by URL."""
from urllib.parse import urlparse


class PlatformDetector:
    def detect(self, url: str) -> str:
        host = (urlparse(url).netloc or "").lower()
        if "amazon." in host:
            return "amazon"
        if "ebay." in host:
            return "ebay"
        if "walmart." in host:
            return "walmart"
        return "generic"
