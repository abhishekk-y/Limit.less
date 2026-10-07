import pytest

pytest.importorskip("playwright")
pytest.importorskip("reportlab")

from app.runtime import browser_apply
from playwright import async_api


@pytest.mark.asyncio
@pytest.mark.parametrize("confirmation,expected", [(True, "submitted"), (False, "outcome_unknown")])
async def test_browser_fills_uploads_and_requires_employer_confirmation(monkeypatch, confirmation, expected):
    original = async_api.async_playwright
    submitted = {"value": False}
    uploaded = {"value": False}
    html = '''<html><body><form onsubmit="event.preventDefault();document.body.innerHTML=\'RESPONSE\'">
    <label>Your name<input name="name" required></label>
    <label>Resume<input type="file" name="resume" required></label>
    <button type="submit">Submit application</button></form></body></html>'''.replace(
        "RESPONSE", "Thank you for your application" if confirmation else "Processing your request")

    class Manager:
        async def __aenter__(self):
            self.manager = original()
            playwright = await self.manager.__aenter__()
            launch = playwright.chromium.launch
            async def instrumented_launch(**kwargs):
                try:
                    browser = await launch(**kwargs)
                except Exception:
                    pytest.skip("Installed Edge browser is unavailable")
                new_context = browser.new_context
                async def instrumented_context(**options):
                    context = await new_context(**options)
                    new_page = context.new_page
                    async def instrumented_page():
                        page = await new_page()
                        await page.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=html))
                        return page
                    context.new_page = instrumented_page
                    return context
                browser.new_context = instrumented_context
                return browser
            playwright.chromium.launch = instrumented_launch
            return playwright
        async def __aexit__(self, *args):
            return await self.manager.__aexit__(*args)

    monkeypatch.setattr(async_api, "async_playwright", Manager)
    async def public_url(_): pass
    monkeypatch.setattr(browser_apply, "public_url", public_url)
    async def choose(values, state, applicant, source, history):
        controls = state["frames"][0]["controls"]
        for control in controls:
            if control["label"] == "Your name" and not control["text"]:
                return browser_apply.Action(action="fill", element=control["id"], value=applicant["full_name"])
        if not uploaded["value"]:
            uploaded["value"] = True
            return browser_apply.Action(action="upload", element=next(c["id"] for c in controls if c["type"] == "file"))
        if not submitted["value"]:
            submitted["value"] = True
            return browser_apply.Action(action="submit", element=next(c["id"] for c in controls if c["tag"] == "button"))
        return browser_apply.Action(action="done")
    monkeypatch.setattr(browser_apply, "choose_action", choose)
    async def cancelled(): return False
    result = await browser_apply.apply_to_job({"url": "https://employer.example.org/apply"},
                                              {"full_name": "Example Applicant"}, "Source résumé", "Example Applicant\nPython developer",
                                              {}, "msedge", cancelled)
    assert submitted["value"] and uploaded["value"]
    assert result["status"] == expected, result
    if confirmation:
        assert len(result["receipt_sha256"]) == 64
