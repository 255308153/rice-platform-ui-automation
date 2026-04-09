import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from common import (
    click_by_text,
    fill_by_placeholder,
    get_alert_text_and_accept,
    open_page,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def click_login_primary_button(driver, text: str) -> None:
    wait_for_visible(
        driver,
        By.XPATH,
        f"//section[contains(@class,'login-box')]//button[contains(@class,'btn-primary') and normalize-space()='{text}']",
    ).click()


@pytest.mark.ui
def test_user_login_page_default_view(driver, ui_config):
    open_page(driver, f"{ui_config.user_base_url}/login")

    wait_for_text(driver, By.TAG_NAME, "h2", "账号登录")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='登录']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='注册']")


@pytest.mark.ui
def test_user_login_requires_username_and_password(driver, ui_config):
    open_page(driver, f"{ui_config.user_base_url}/login")

    click_login_primary_button(driver, "登录")

    assert get_alert_text_and_accept(driver) == "请输入用户名和密码"


@pytest.mark.ui
def test_user_register_requires_matching_password(driver, ui_config):
    open_page(driver, f"{ui_config.user_base_url}/login")

    click_by_text(driver, "button", "注册")
    wait_for_text(driver, By.TAG_NAME, "h2", "用户注册")
    fill_by_placeholder(driver, "请输入用户名", "ui_auto_user")
    fill_by_placeholder(driver, "请设置密码（至少6位）", "123456")
    fill_by_placeholder(driver, "请再次输入密码", "654321")
    click_login_primary_button(driver, "注册")

    assert get_alert_text_and_accept(driver) == "两次输入的密码不一致"


@pytest.mark.ui
def test_user_login_success_redirects_to_home(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置前台登录账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )

    open_page(driver, f"{ui_config.user_base_url}/login")
    fill_by_placeholder(driver, "请输入用户名", ui_config.user_username)
    fill_by_placeholder(driver, "请输入密码", ui_config.user_password)
    click_login_primary_button(driver, "登录")

    WebDriverWait(driver, 5).until(lambda d: "/login" not in d.current_url)
    assert "/login" not in driver.current_url


@pytest.mark.ui
def test_admin_login_page_default_view(driver, ui_config):
    open_page(driver, f"{ui_config.admin_base_url}/login")

    wait_for_text(driver, By.TAG_NAME, "h2", "后台登录")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='登录']")


@pytest.mark.ui
def test_admin_login_requires_username_and_password(driver, ui_config):
    open_page(driver, f"{ui_config.admin_base_url}/login")

    click_login_primary_button(driver, "登录")

    assert get_alert_text_and_accept(driver) == "请输入用户名和密码"


@pytest.mark.ui
def test_admin_login_success_redirects_to_dashboard(driver, ui_config):
    require_credentials(
        ui_config.admin_username,
        ui_config.admin_password,
        "未设置后台登录账号环境变量 `RICE_UI_ADMIN_USERNAME/RICE_UI_ADMIN_PASSWORD`。",
    )

    open_page(driver, f"{ui_config.admin_base_url}/login")
    fill_by_placeholder(driver, "请输入用户名", ui_config.admin_username)
    fill_by_placeholder(driver, "请输入密码", ui_config.admin_password)
    click_login_primary_button(driver, "登录")

    WebDriverWait(driver, 5).until(
        lambda d: any(path in d.current_url for path in ("/admin/dashboard", "/merchant/dashboard"))
    )
    assert any(
        path in driver.current_url
        for path in ("/admin/dashboard", "/merchant/dashboard")
    ), f"后台登录后未跳转到预期首页，当前 URL: {driver.current_url}"
