import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_and_open_shop(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置商城测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/shop")


@pytest.mark.ui
def test_shop_page_default_sections_visible(driver, ui_config):
    _login_and_open_shop(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h1", "一条搜索栏切换商品搜索或店铺搜索")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='重置筛选']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='搜索']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='店铺筛选']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='全部商品']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='猜你喜欢']")


@pytest.mark.ui
def test_shop_search_mode_switch_updates_placeholder(driver, ui_config):
    _login_and_open_shop(driver, ui_config)

    select_el = wait_for_visible(driver, By.XPATH, "(//section[contains(@class,'search-card')]//select)[1]")
    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='输入商品名称搜索']")
    assert search_input.get_attribute("placeholder") == "输入商品名称搜索"

    Select(select_el).select_by_value("SHOP")
    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='输入店铺名称搜索']")
    assert search_input.get_attribute("placeholder") == "输入店铺名称搜索"


@pytest.mark.ui
def test_shop_recommendation_mode_switches_section_title(driver, ui_config):
    _login_and_open_shop(driver, ui_config)

    click_by_text(driver, "button", "猜你喜欢")
    wait_for_visible(driver, By.XPATH, "//section[contains(@class,'product-card-wrapper')]//h3[normalize-space()='猜你喜欢']")


@pytest.mark.ui
def test_shop_reset_button_restores_default_search_mode(driver, ui_config):
    _login_and_open_shop(driver, ui_config)

    select_el = wait_for_visible(driver, By.XPATH, "(//section[contains(@class,'search-card')]//select)[1]")
    Select(select_el).select_by_value("SHOP")
    click_by_text(driver, "button", "重置筛选")

    wait_for_visible(driver, By.XPATH, "//input[@placeholder='输入商品名称搜索']")


@pytest.mark.ui
def test_shop_can_open_product_detail_when_products_exist(driver, ui_config):
    _login_and_open_shop(driver, ui_config)

    detail_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='查看详情']")
    if not detail_buttons:
        pytest.skip("当前商城页无商品数据，跳过商品详情跳转测试。")

    detail_buttons[0].click()

    assert wait_for_url_contains(driver, "/product/"), f"点击查看详情后未跳转商品详情页，当前 URL: {driver.current_url}"
