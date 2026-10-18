import json
import os
import urllib.parse
from copy import deepcopy
from importlib.metadata import version

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


load_dotenv()


CAPABILITIES = [
    {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "LT:Options": {
            "platform": "Windows 10",
            "build": "Playwright 101 Assignment",
            "name": "Chrome Windows - Playwright 101",
            "projectName": "Playwright 101 Certification",
            "network": True,
            "video": True,
            "console": True,
            "visual": True,
        },
    },
    {
        "browserName": "pw-firefox",
        "browserVersion": "latest",
        "LT:Options": {
            "platform": "macOS Sonoma",
            "build": "Playwright 101 Assignment",
            "name": "Firefox macOS - Playwright 101",
            "projectName": "Playwright 101 Certification",
            "network": True,
            "video": True,
            "console": True,
            "visual": True,
        },
    },
]


@pytest.fixture(params=CAPABILITIES)
def page(request):
    capabilities = deepcopy(request.param)

    username = os.getenv("LT_USERNAME")
    access_key = os.getenv("LT_ACCESS_KEY")

    if not username or not access_key:
        pytest.fail(
            "LT_USERNAME and LT_ACCESS_KEY must be configured "
            "in the .env file."
        )

    capabilities["LT:Options"]["user"] = username
    capabilities["LT:Options"]["accessKey"] = access_key
    capabilities["LT:Options"]["playwrightClientVersion"] = version(
        "playwright"
    )

    encoded_capabilities = urllib.parse.quote(
        json.dumps(capabilities)
    )

    ws_endpoint = (
        "wss://cdp.lambdatest.com/playwright"
        f"?capabilities={encoded_capabilities}"
    )

    with sync_playwright() as playwright:

        browser = playwright.chromium.connect(ws_endpoint)

        context = browser.new_context(
        viewport={"width": 1920, "height": 1080}
        )

        test_page = context.new_page()

        yield test_page

        context.close()
        browser.close()