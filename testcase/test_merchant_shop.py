import pytest
from selenium.webdriver.common.by import By

from common import (
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_merchant_shop(driver, ui_config):
    require_credentials(
        ui_config.merchant_username,
        ui_config.merchant_password,
        "未设置商户经营助手测试账号环境变量 `RICE_UI_MERCHANT_USERNAME/RICE_UI_MERCHANT_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.merchant_username, ui_config.merchant_password)
    driver.get(f"{ui_config.admin_base_url}/merchant/shop")


@pytest.mark.ui
def test_merchant_shop_page_default_sections_visible(driver, ui_config):
    _login_and_open_merchant_shop(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "AI 助手销售建议")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='刷新数据']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='销售助手对话']")
    wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='例如：最近该主推哪类商品？需要怎么做组合促销？']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='发送']")

    overview_titles = driver.find_elements(By.XPATH, "//h3[normalize-space()='店铺经营概览']")
    custom_shop_titles = driver.find_elements(By.XPATH, "//section[contains(@class,'overview-panel')]//h3")
    assert overview_titles or custom_shop_titles, "经营概览区域标题未正常显示。"


@pytest.mark.ui
def test_merchant_shop_summary_area_shows_metrics_or_overview(driver, ui_config):
    _login_and_open_merchant_shop(driver, ui_config)

    stat_cards = driver.find_elements(By.CSS_SELECTOR, ".stat-card")
    overview_panel = driver.find_elements(By.CSS_SELECTOR, ".overview-panel")
    top_products = driver.find_elements(By.CSS_SELECTOR, ".product-item")
    empty_top_products = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无热销商品数据']")

    assert overview_panel, "经营概览区域未显示。"
    assert stat_cards or top_products or empty_top_products, "经营助手页既没有摘要卡片，也没有热销商品区域数据提示。"


@pytest.mark.ui
def test_merchant_shop_message_panel_shows_messages_or_empty_state(driver, ui_config):
    _login_and_open_merchant_shop(driver, ui_config)

    message_items = driver.find_elements(By.CSS_SELECTOR, ".message")
    empty_messages = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无会话内容']")

    assert message_items or empty_messages, "销售助手对话区域既没有消息，也没有显示空状态提示。"


@pytest.mark.ui
def test_merchant_shop_question_input_accepts_text(driver, ui_config):
    _login_and_open_merchant_shop(driver, ui_config)

    question_input = wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='例如：最近该主推哪类商品？需要怎么做组合促销？']")
    question_input.send_keys("最近适合主推哪类大米商品？")

    assert question_input.get_attribute("value") == "最近适合主推哪类大米商品？"


@pytest.mark.ui
def test_merchant_shop_empty_question_does_not_create_user_message(driver, ui_config):
    _login_and_open_merchant_shop(driver, ui_config)

    question_input = wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='例如：最近该主推哪类商品？需要怎么做组合促销？']")
    send_button = wait_for_visible(driver, By.XPATH, "//button[normalize-space()='发送']")
    user_messages_before = len(driver.find_elements(By.CSS_SELECTOR, ".message.user"))

    question_input.clear()
    send_button.click()

    user_messages_after = len(driver.find_elements(By.CSS_SELECTOR, ".message.user"))
    assert user_messages_after == user_messages_before, "空问题发送后不应新增用户消息。"
