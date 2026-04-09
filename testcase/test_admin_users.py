import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from common import (
    get_alert_text_and_dismiss,
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_admin_users(driver, ui_config):
    require_credentials(
        ui_config.admin_username,
        ui_config.admin_password,
        "未设置管理员用户管理测试账号环境变量 `RICE_UI_ADMIN_USERNAME/RICE_UI_ADMIN_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.admin_username, ui_config.admin_password)
    driver.get(f"{ui_config.admin_base_url}/admin/users")


@pytest.mark.ui
def test_admin_users_page_default_sections_visible(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "用户管理")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='查询']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='导出数据']")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索用户名/手机号']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='全部角色']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='普通用户']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='商户']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='全部状态']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='正常']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='禁用']")


@pytest.mark.ui
def test_admin_users_filters_can_switch(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    selects = driver.find_elements(By.TAG_NAME, "select")
    assert len(selects) >= 2, "用户管理页筛选下拉框数量不符合预期。"

    role_select = Select(selects[0])
    status_select = Select(selects[1])

    role_select.select_by_value("MERCHANT")
    assert role_select.first_selected_option.text.strip() == "商户"

    status_select.select_by_value("0")
    assert status_select.first_selected_option.text.strip() == "禁用"


@pytest.mark.ui
def test_admin_users_search_input_accepts_text(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索用户名/手机号']")
    search_input.send_keys("测试账号")

    assert search_input.get_attribute("value") == "测试账号"


@pytest.mark.ui
def test_admin_users_show_items_or_empty_state(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    user_items = driver.find_elements(By.CSS_SELECTOR, ".user-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无用户数据']")

    assert user_items or empty_state, "用户管理页既没有用户项，也没有显示空状态提示。"


@pytest.mark.ui
def test_admin_users_disable_confirm_dialog_can_be_cancelled(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    toggle_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='禁用' or normalize-space()='启用']")
    if not toggle_buttons:
        pytest.skip("当前没有可操作的用户状态按钮，跳过状态切换确认框测试。")

    toggle_buttons[0].click()
    alert_text = get_alert_text_and_dismiss(driver)
    assert "确认" in alert_text and ("禁用用户" in alert_text or "启用用户" in alert_text)


@pytest.mark.ui
def test_admin_users_reset_password_confirm_dialog_can_be_cancelled(driver, ui_config):
    _login_and_open_admin_users(driver, ui_config)

    reset_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='重置密码']")
    if not reset_buttons:
        pytest.skip("当前没有可操作的重置密码按钮，跳过重置密码确认框测试。")

    reset_buttons[0].click()
    alert_text = get_alert_text_and_dismiss(driver)
    assert "确认重置用户" in alert_text and "123456" in alert_text
