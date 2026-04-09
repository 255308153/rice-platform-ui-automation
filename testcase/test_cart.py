import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_cart(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置购物车测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/cart")


@pytest.mark.ui
def test_cart_page_default_sections_visible(driver, ui_config):
    _login_and_open_cart(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "购物车")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索购物车内商品']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='结算明细']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='商品种类']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='商品件数']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='结算']")


@pytest.mark.ui
def test_cart_search_input_accepts_text(driver, ui_config):
    _login_and_open_cart(driver, ui_config)

    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索购物车内商品']")
    search_input.send_keys("测试商品")

    assert search_input.get_attribute("value") == "测试商品"


@pytest.mark.ui
def test_cart_can_clear_search_keyword(driver, ui_config):
    _login_and_open_cart(driver, ui_config)

    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索购物车内商品']")
    search_input.send_keys("大米")
    clear_button = wait_for_visible(driver, By.XPATH, "//button[contains(@class,'clear-btn') and normalize-space()='清空']")
    clear_button.click()

    assert search_input.get_attribute("value") == ""


@pytest.mark.ui
def test_cart_show_items_or_empty_state(driver, ui_config):
    _login_and_open_cart(driver, ui_config)

    cart_items = driver.find_elements(By.CSS_SELECTOR, ".cart-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and (normalize-space()='购物车为空' or normalize-space()='没有匹配的商品')]")

    assert cart_items or empty_state, "购物车页既没有商品项，也没有显示空状态提示。"


@pytest.mark.ui
def test_cart_checkout_button_disabled_when_empty(driver, ui_config):
    _login_and_open_cart(driver, ui_config)

    checkout_button = wait_for_visible(driver, By.XPATH, "//button[normalize-space()='结算']")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='购物车为空']")
    if not empty_state:
        pytest.skip("当前购物车存在商品数据，跳过空购物车结算按钮状态校验。")

    assert checkout_button.get_attribute("disabled") is not None, "购物车为空时，结算按钮应为禁用状态。"
