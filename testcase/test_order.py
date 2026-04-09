import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    get_alert_text_and_accept,
    has_alert,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_and_open_orders(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置订单测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/orders")


def _find_status_button(driver, text):
    return driver.find_element(By.XPATH, f"//div[contains(@class,'status-filter')]//button[normalize-space()='{text}']")


@pytest.mark.ui
def test_orders_page_default_sections_visible(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "订单管理")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='全部']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='待支付']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='待发货']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='待收货']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='已完成']")


@pytest.mark.ui
def test_orders_status_filter_buttons_can_switch(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "订单管理")

    for status_text in ["待支付", "待发货", "待收货", "已完成", "全部"]:
        button = _find_status_button(driver, status_text)
        button.click()
        assert "active" in _find_status_button(driver, status_text).get_attribute("class"), f"点击 `{status_text}` 后未高亮对应状态按钮。"


@pytest.mark.ui
def test_orders_show_empty_state_or_order_cards(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "订单管理")
    order_cards = driver.find_elements(By.CSS_SELECTOR, ".order-card")
    empty_blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无订单']")

    assert order_cards or empty_blocks, "订单页既没有订单卡片，也没有显示暂无订单提示。"


@pytest.mark.ui
def test_orders_can_expand_detail_when_orders_exist(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    detail_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='查看详情']")
    if not detail_buttons:
        pytest.skip("当前账号没有订单数据，跳过订单详情展开测试。")

    detail_buttons[0].click()

    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'order-detail')]")
    wait_for_text(driver, By.TAG_NAME, "h4", "订单信息")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='收起']")


@pytest.mark.ui
def test_orders_can_open_product_detail_when_order_items_exist(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    order_products = driver.find_elements(By.CSS_SELECTOR, ".order-product")
    if not order_products:
        pytest.skip("当前订单列表中没有可点击的商品，跳过订单商品详情跳转测试。")

    order_products[0].click()

    assert wait_for_url_contains(driver, "/product/"), f"点击订单商品后未跳转商品详情页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_orders_refund_modal_validates_empty_reason(driver, ui_config):
    _login_and_open_orders(driver, ui_config)

    refund_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='申请退款']")
    if not refund_buttons:
        pytest.skip("当前账号没有可申请退款的订单，跳过退款弹窗校验测试。")

    refund_buttons[0].click()
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='申请退款']")
    click_by_text(driver, "button", "提交申请")

    assert has_alert(driver), "点击提交申请后未弹出退款原因校验提示。"
    assert get_alert_text_and_accept(driver) == "请填写退款原因"
