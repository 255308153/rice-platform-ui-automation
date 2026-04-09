import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_admin_dashboard(driver, ui_config):
    require_credentials(
        ui_config.admin_username,
        ui_config.admin_password,
        "未设置管理员后台测试账号环境变量 `RICE_UI_ADMIN_USERNAME/RICE_UI_ADMIN_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.admin_username, ui_config.admin_password)
    wait_for_url_contains(driver, "/admin/dashboard")


def _login_merchant_dashboard(driver, ui_config):
    require_credentials(
        ui_config.merchant_username,
        ui_config.merchant_password,
        "未设置商户后台测试账号环境变量 `RICE_UI_MERCHANT_USERNAME/RICE_UI_MERCHANT_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.merchant_username, ui_config.merchant_password)
    wait_for_url_contains(driver, "/merchant/dashboard")


@pytest.mark.ui
def test_admin_dashboard_default_sections_visible(driver, ui_config):
    _login_admin_dashboard(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "数据监控")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='待审核商户']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='待审核专家']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='总订单数']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='总交易额']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='AI 调用总次数']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='用户活跃度']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='热销商品 TOP5']")


@pytest.mark.ui
def test_admin_dashboard_pending_merchant_entry_navigates_to_audits(driver, ui_config):
    _login_admin_dashboard(driver, ui_config)

    click_by_text(driver, "button", "查看")

    assert wait_for_url_contains(driver, "/admin/audits"), f"点击查看后未跳转审核页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_merchant_dashboard_default_sections_visible(driver, ui_config):
    _login_merchant_dashboard(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "商户后台")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='今日订单']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='待处理订单']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='今日销售额']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='商品总数']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='近7日销售趋势']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='订单状态分布']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='热销商品TOP5']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='待处理订单']")


@pytest.mark.ui
def test_merchant_dashboard_shows_pending_orders_or_empty_state(driver, ui_config):
    _login_merchant_dashboard(driver, ui_config)

    order_items = driver.find_elements(By.CSS_SELECTOR, ".order-item")
    empty_orders = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无待处理订单']")

    assert order_items or empty_orders, "商户后台待处理订单区域既没有订单项，也没有显示空状态提示。"
