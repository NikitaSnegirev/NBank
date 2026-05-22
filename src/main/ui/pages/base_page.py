from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

from playwright.sync_api import Page, Dialog

from src.main.api.configs.config import Config

T = TypeVar("T", bound="BasePage")


class BasePage(ABC):
    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(Config.get("UI_BASE_URL", "http://localhost:3000")).rstrip("/")

    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    @property
    def username_input(self):
        return self.page.get_by_placeholder("Username")

    @property
    def password_input(self):
        return self.page.get_by_placeholder("Password")

    def open(self: T) -> T:
        target = self.url()
        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"
        self.page.goto(target, wait_until="domcontentloaded")
        return self

    def get_page(self, page_cls: Type[T]) -> T:
        return page_cls(self.page)

    def check_alert_message_and_accept(self: T, expected_text: str) -> T:
        def _handler(d: Dialog) -> None:
            assert expected_text in d.message, f"Alert text mismatch: {d.message!r}"
            d.accept()
        self.page.once("dialog", _handler)
        return self
