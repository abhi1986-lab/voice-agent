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

    def _run_session(self, destination: str, joined_event: Event, startup_errors: list[str]) -> None:
        try:
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

                # Signal that we've attempted to join, then keep the session alive
                # so the meeting is not torn down immediately.
                joined_event.set()
                page.wait_for_timeout(8 * 60 * 60 * 1_000)
                browser.close()
        except Exception as exc:
            startup_errors.append(str(exc))
            joined_event.set()

    def join(self, destination: str) -> None:
        joined_event = Event()
        startup_errors: list[str] = []
        Thread(target=self._run_session, args=(destination, joined_event, startup_errors), daemon=True).start()

        # Wait briefly so callers get immediate failures (bad URL, browser launch, etc.)
        # before continuing, but return without closing the Teams session.
        joined_event.wait(timeout=15)
        if startup_errors:
            raise RuntimeError(startup_errors[0])


class SipPhoneJoiner(CallJoiner):
    """Join/dial a phone endpoint via local SIP stack (baresip).

    destination: SIP URI like sip:+15551234567@sip.example.com
    """

    def join(self, destination: str) -> None:
        subprocess.run(["baresip", "-e", f"dial {destination}"], check=True)
