import pytest
from selenium.webdriver.common.by import By

from common import (
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_and_open_product_detail(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置商品详情测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/shop")

    detail_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='查看详情']")
    if not detail_buttons:
        pytest.skip("当前商城没有商品数据，跳过商品详情页测试。")

    detail_buttons[0].click()
    assert wait_for_url_contains(driver, "/product/"), f"点击后未跳转商品详情页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_product_detail_page_default_sections_visible(driver, ui_config):
    _login_and_open_product_detail(driver, ui_config)

    wait_for_visible(driver, By.CSS_SELECTOR, ".product-detail")
    wait_for_visible(driver, By.TAG_NAME, "h1")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='规格参数']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='加入购物车']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='立即购买']")


@pytest.mark.ui
def test_product_detail_show_specs_items(driver, ui_config):
    _login_and_open_product_detail(driver, ui_config)

    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='产地']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='等级']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='净含量']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='口感']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='保质期']")


@pytest.mark.ui
def test_product_detail_show_image_or_placeholder(driver, ui_config):
    _login_and_open_product_detail(driver, ui_config)

    images = driver.find_elements(By.XPATH, "//div[contains(@class,'product-img')]//img")
    placeholders = driver.find_elements(By.XPATH, "//div[contains(@class,'img-placeholder') and normalize-space()='暂无商品图片']")
    assert images or placeholders, "商品详情页既没有主图，也没有显示占位提示。"
