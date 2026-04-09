import os
from dataclasses import dataclass

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


DEFAULT_TIMEOUT = 10


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class UiConfig:
    user_base_url: str = os.getenv("RICE_USER_BASE_URL", "http://localhost:3000").rstrip("/")
    admin_base_url: str = os.getenv("RICE_ADMIN_BASE_URL", "http://localhost:3002").rstrip("/")
    user_username: str = os.getenv("RICE_UI_USER_USERNAME", "")
    user_password: str = os.getenv("RICE_UI_USER_PASSWORD", "")
    expert_username: str = os.getenv("RICE_UI_EXPERT_USERNAME", "")
    expert_password: str = os.getenv("RICE_UI_EXPERT_PASSWORD", "")
    merchant_username: str = os.getenv("RICE_UI_MERCHANT_USERNAME", "")
    merchant_password: str = os.getenv("RICE_UI_MERCHANT_PASSWORD", "")
    admin_username: str = os.getenv("RICE_UI_ADMIN_USERNAME", "")
    admin_password: str = os.getenv("RICE_UI_ADMIN_PASSWORD", "")
    chromedriver_path: str = os.getenv("CHROMEDRIVER_PATH", "")
    headless: bool = _is_truthy(os.getenv("UI_HEADLESS"))


CONFIG = UiConfig()


def _build_driver() -> webdriver.Chrome:
    options = Options()
    if CONFIG.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,960")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=zh-CN")

    service = Service(CONFIG.chromedriver_path) if CONFIG.chromedriver_path else Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(2)
    return driver


@pytest.fixture(scope="session")
def ui_config() -> UiConfig:
    return CONFIG


@pytest.fixture(scope="function")
def driver():
    driver = _build_driver()
    try:
        yield driver
    finally:
        driver.quit()


def open_page(driver: webdriver.Chrome, url: str) -> None:
    driver.get(url)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    driver.get(url)


def wait_for_url_contains(driver: webdriver.Chrome, text: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    try:
        WebDriverWait(driver, timeout).until(lambda d: text in d.current_url)
        return True
    except TimeoutException:
        return False


def wait_for_text(driver: webdriver.Chrome, by: By, locator: str, text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element((by, locator), text))


def wait_for_visible(driver: webdriver.Chrome, by: By, locator: str, timeout: int = DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, locator)))


def click_by_text(driver: webdriver.Chrome, tag: str, text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    xpath = f"//{tag}[normalize-space()='{text}']"
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def click_primary_button(driver: webdriver.Chrome, text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    xpath = (
        f"//section[contains(@class,'login-box')]"
        f"//button[contains(@class,'btn-primary') and normalize-space()='{text}']"
    )
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def fill_by_placeholder(driver: webdriver.Chrome, placeholder: str, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    element = wait_for_visible(driver, By.XPATH, f"//input[@placeholder='{placeholder}']", timeout)
    element.clear()
    element.send_keys(value)


def get_alert_text_and_accept(driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT) -> str:
    alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
    text = alert.text
    alert.accept()
    return text


def get_alert_text_and_dismiss(driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT) -> str:
    alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
    text = alert.text
    alert.dismiss()
    return text


def has_alert(driver: webdriver.Chrome) -> bool:
    try:
        driver.switch_to.alert
        return True
    except NoAlertPresentException:
        return False


def require_credentials(username: str, password: str, reason: str) -> None:
    if not username or not password:
        pytest.skip(reason)


def login_user_front(driver: webdriver.Chrome, base_url: str, username: str, password: str) -> None:
    open_page(driver, f"{base_url}/login")
    fill_by_placeholder(driver, "请输入用户名", username)
    fill_by_placeholder(driver, "请输入密码", password)
    click_primary_button(driver, "登录")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        lambda d: "/login" not in d.current_url or bool(d.execute_script("return localStorage.getItem('token')"))
    )


def login_admin_front(driver: webdriver.Chrome, base_url: str, username: str, password: str) -> None:
    open_page(driver, f"{base_url}/login")
    fill_by_placeholder(driver, "请输入用户名", username)
    fill_by_placeholder(driver, "请输入密码", password)
    click_primary_button(driver, "登录")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        lambda d: "/login" not in d.current_url or bool(d.execute_script("return localStorage.getItem('token')"))
    )
