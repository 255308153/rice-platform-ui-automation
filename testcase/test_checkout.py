import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    get_alert_text_and_accept,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_checkout(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置结算测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/checkout")


@pytest.mark.ui
def test_checkout_page_default_sections_visible(driver, ui_config):
    _login_and_open_checkout(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "确认订单")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='收货地址']")
    wait_for_visible(driver, By.XPATH, "//button[contains(normalize-space(),'新增地址') or contains(normalize-space(),'取消新增')]")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='提交订单']")
    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'total') and contains(normalize-space(),'总计')]")


@pytest.mark.ui
def test_checkout_can_toggle_address_form(driver, ui_config):
    _login_and_open_checkout(driver, ui_config)

    toggle_button = wait_for_visible(
        driver,
        By.XPATH,
        "//button[contains(normalize-space(),'新增地址') or contains(normalize-space(),'取消新增')]",
    )
    is_form_visible_before = bool(driver.find_elements(By.XPATH, "//input[@placeholder='收货人姓名']"))

    toggle_button.click()
    is_form_visible_after = bool(driver.find_elements(By.XPATH, "//input[@placeholder='收货人姓名']"))

    assert is_form_visible_after != is_form_visible_before, "点击地址表单切换按钮后，表单显示状态未发生变化。"


@pytest.mark.ui
def test_checkout_address_form_inputs_accept_text(driver, ui_config):
    _login_and_open_checkout(driver, ui_config)

    if not driver.find_elements(By.XPATH, "//input[@placeholder='收货人姓名']"):
        click_by_text(driver, "button", "新增地址")

    name_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='收货人姓名']")
    phone_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='手机号']")
    detail_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='详细地址']")

    name_input.send_keys("测试收货人")
    phone_input.send_keys("13800138000")
    detail_input.send_keys("测试街道 88 号")

    assert name_input.get_attribute("value") == "测试收货人"
    assert phone_input.get_attribute("value") == "13800138000"
    assert detail_input.get_attribute("value") == "测试街道 88 号"


@pytest.mark.ui
def test_checkout_save_address_validates_empty_form(driver, ui_config):
    _login_and_open_checkout(driver, ui_config)

    if not driver.find_elements(By.XPATH, "//input[@placeholder='收货人姓名']"):
        click_by_text(driver, "button", "新增地址")

    click_by_text(driver, "button", "保存地址")
    assert get_alert_text_and_accept(driver) == "请完整填写收货地址信息"


@pytest.mark.ui
def test_checkout_show_items_or_empty_address_notice(driver, ui_config):
    _login_and_open_checkout(driver, ui_config)

    address_cards = driver.find_elements(By.CSS_SELECTOR, ".address-card")
    empty_address = driver.find_elements(By.XPATH, "//div[contains(@class,'empty-address') and contains(normalize-space(),'暂无收货地址')]")
    order_container = driver.find_elements(By.CSS_SELECTOR, ".order-items")

    assert address_cards or empty_address, "结算页既没有地址卡片，也没有显示地址空状态提示。"
    assert order_container, "结算商品列表区域未显示。"
