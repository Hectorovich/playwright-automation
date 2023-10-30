import logging
import os

import pytest
from _pytest.fixtures import fixture
from playwright.sync_api import sync_playwright

from page_objects.application import App
from settings import *


@fixture(scope="session")
def preconditions():
    logging.info("preconditions started")
    yield
    logging.info("preconditions started")


@fixture(scope="session")
def get_playwright():
    with sync_playwright() as playwright:
        yield playwright


@fixture(scope="session", params=["chromium", "firefox"], ids=["chromium", "firefox"])
def get_browser(get_playwright, request):
    browser = request.param
    os.environ["PWBROWSER"] = browser
    headless = request.config.getini("headless")
    if headless == "True":
        headless = True
    else:
        headless = False

    if browser == "chromium":
        bro = get_playwright.chromium.launch(headless=headless)
    elif browser == "firefox":
        bro = get_playwright.firefox.launch(headless=headless)
    elif browser == "webkit":
        bro = get_playwright.webkit.launch(headless=headless)
    else:
        assert False, "unsupported browser type"

    yield bro
    bro.close()
    del os.environ["PWBROWSER"]


@fixture(scope="session")
def desktop_app(get_browser, request):
    base_url = request.config.getini("base_url")
    app = App(get_browser, base_url=base_url, **BROWSER_OPTIONS)
    app.goto("/")
    yield app
    app.close()


@fixture(scope="session")
def desktop_app_auth(desktop_app):
    app = desktop_app
    app.goto("/login")
    # app.login(os.environ.get("LOGIN"), os.environ.get("PASSWORD"))
    app.login("alice", "Qamania123")
    yield app


@fixture(scope="session", params=["iPhone 11", "Pixel 2"])
def mobile_app(get_playwright, get_browser, request):
    if os.environ.get("PWBROWSER") == "firefox":
        pytest.skip()
    base_url = request.config.getini("base_url")
    device = request.param
    device_config = get_playwright.devices.get(device)
    if device_config is not None:
        device_config.update(BROWSER_OPTIONS)
    else:
        device_config = BROWSER_OPTIONS
    app = App(get_browser, base_url=base_url, **device_config)
    app.goto("/")
    yield app
    app.close()


@fixture(scope="session")
def mobile_app_auth(mobile_app):
    app = mobile_app
    app.goto("/login")
    # app.login(os.environ.get("LOGIN"), os.environ.get("PASSWORD"))
    app.login("alice", "Qamania123")
    yield app


def pytest_addoption(parser):
    parser.addini("device", help="device for test", default="")
    parser.addini("browser", help="browser to launch tests", default="chromium")
    parser.addini("base_url", help="base url for site under test", default="")
    parser.addini("headless", help="run browser in headless mode", default="True")
