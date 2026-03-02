from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from threading import Event, Thread

from playwright.sync_api import sync_playwright


class CallJoiner(ABC):
    @abstractmethod
    def join(self, destination: str) -> None:
        raise NotImplementedError


class TeamsJoiner(CallJoiner):
    """Join a Teams meeting using browser automation.

    destination: Teams meeting URL.
    """

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless

    def join(self, destination: str) -> None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(destination, wait_until="domcontentloaded")
            # Best-effort selectors for Teams web UX.
            for selector in [
                'button:has-text("Continue on this browser")',
                'button:has-text("Continue")',
                'button:has-text("Join on the web")',
                'button:has-text("Join")',
                'button:has-text("Join now")',
            ]:
                locator = page.locator(selector)
                if locator.count() > 0:
                    locator.first.click()
                    page.wait_for_timeout(400)
            page.wait_for_timeout(5_000)
            browser.close()


class SipPhoneJoiner(CallJoiner):
    """Join/dial a phone endpoint via local SIP stack (baresip).

    destination: SIP URI like sip:+15551234567@sip.example.com
    """

    def join(self, destination: str) -> None:
        subprocess.run(["baresip", "-e", f"dial {destination}"], check=True)
