import contextlib
import random
import string
from time import time_ns, sleep
from playwright.sync_api import TimeoutError, expect


def login_nextcloud(page, username='nextcloud', password='nextcloud', domain='https://ncs'):
    page.goto(f"{domain}/index.php/login")
    page.locator('#user').fill(username)
    page.locator('#password').fill(password)
    page.locator('#password').press("Enter")


def get_random_text(size_in_bytes)  -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size_in_bytes))

def log_note(message: str) -> None:
    timestamp = str(time_ns())[:16]
    print(f"{timestamp} {message}")


def close_modal(page) -> None:
    with contextlib.suppress(TimeoutError):
        user_sleep() # Sleep to make sure the modal has time to appear before continuing navigation
        page.locator('#firstrunwizard .modal-container__content button[aria-label=Close]').click(timeout=15_000)


def close_toasts(page, timeout=5_000) -> None:
    # Toasts stack in the top right corner and intercept pointer events for anything
    # underneath them. Some, like the calendar timezone warning, linger for 60s, which
    # outlasts the default 30s click timeout, so they must be clicked away.
    with contextlib.suppress(TimeoutError, AssertionError):
        toasts = page.locator('.toastify.on')
        while (count := toasts.count()) > 0:
            # Collapse to one line: read-notes-stdout expects a single note per line
            text = ' '.join(toasts.first.inner_text().replace('✖', '').split())
            log_note(f"Closing toast: {text}")
            toasts.first.locator('.toast-close').click(timeout=timeout)
            expect(toasts).to_have_count(count - 1, timeout=timeout)


def timeout_handler(signum, frame):
    raise TimeoutError("Page.content() timed out")

def user_sleep(delay=5):
    log_note(f"Sleeping for {delay}s")
    sleep(delay)