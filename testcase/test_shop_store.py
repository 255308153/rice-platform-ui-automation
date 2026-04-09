import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_and_open_store_from_shop(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置店铺页测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/shop")

    shop_chips = driver.find_elements(By.XPATH, "//button[contains(@class,'shop-chip') and not(normalize-space()='全部商品') and not(normalize-space()='猜你喜欢')]")
    if not shop_chips:
        pytest.skip("当前商城没有可进入的店铺数据，跳过店铺页测试。")

    shop_chips[0].click()
    click_by_text(driver, "button", "进入当前店铺")
    assert wait_for_url_contains(driver, "/shop/store/"), f"未跳转到店铺详情页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_shop_store_page_default_sections_visible(driver, ui_config):
    _login_and_open_store_from_shop(driver, ui_config)

    wait_for_visible(driver, By.CSS_SELECTOR, ".store-hero")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='联系店铺客服']")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索该店铺商品']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='筛选']")


@pytest.mark.ui
def test_shop_store_search_input_accepts_text(driver, ui_config):
    _login_and_open_store_from_shop(driver, ui_config)

    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索该店铺商品']")
    search_input.send_keys("大米")

    assert search_input.get_attribute("value") == "大米"


@pytest.mark.ui
def test_shop_store_sort_select_can_switch(driver, ui_config):
    _login_and_open_store_from_shop(driver, ui_config)

    sort_select = Select(wait_for_visible(driver, By.TAG_NAME, "select"))
    sort_select.select_by_value("hot")

    assert sort_select.first_selected_option.text.strip() == "热销优先"


@pytest.mark.ui
def test_shop_store_show_products_or_empty_state(driver, ui_config):
    _login_and_open_store_from_shop(driver, ui_config)

    product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='该店铺暂无符合条件的商品']")

    assert product_cards or empty_state, "店铺页既没有商品卡片，也没有显示空状态提示。"
