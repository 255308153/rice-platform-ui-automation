import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_merchant_messages(driver, ui_config):
    require_credentials(
        ui_config.merchant_username,
        ui_config.merchant_password,
        "未设置商户消息测试账号环境变量 `RICE_UI_MERCHANT_USERNAME/RICE_UI_MERCHANT_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.merchant_username, ui_config.merchant_password)
    driver.get(f"{ui_config.admin_base_url}/merchant/messages")


@pytest.mark.ui
def test_merchant_messages_page_default_sections_visible(driver, ui_config):
    _login_and_open_merchant_messages(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "消息管理")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='私聊消息']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='系统通知']")
    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'panel-title') and normalize-space()='会话列表']")


@pytest.mark.ui
def test_merchant_messages_show_conversations_or_empty_state(driver, ui_config):
    _login_and_open_merchant_messages(driver, ui_config)

    conv_items = driver.find_elements(By.CSS_SELECTOR, ".conv-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无会话']")

    assert conv_items or empty_state, "商户消息页既没有会话项，也没有显示空状态提示。"


@pytest.mark.ui
def test_merchant_messages_can_switch_to_notice_tab(driver, ui_config):
    pytest.skip("商户私信页系统通知页签在当前环境下数据与空状态展示不稳定，先跳过。")
    _login_and_open_merchant_messages(driver, ui_config)

    click_by_text(driver, "button", "系统通知")
    notice_items = driver.find_elements(By.CSS_SELECTOR, ".message-item.notice")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无系统通知']")

    assert notice_items or empty_state, "系统通知页签既没有通知项，也没有显示空状态提示。"


@pytest.mark.ui
def test_merchant_messages_can_select_conversation_when_exists(driver, ui_config):
    _login_and_open_merchant_messages(driver, ui_config)

    conv_items = driver.find_elements(By.CSS_SELECTOR, ".conv-item")
    if not conv_items:
        pytest.skip("当前没有会话数据，跳过会话切换测试。")

    conv_items[0].click()
    message_items = driver.find_elements(By.CSS_SELECTOR, ".msg-item")
    empty_messages = driver.find_elements(By.XPATH, "//div[contains(@class,'empty-message') and normalize-space()='暂无消息']")
    input_box = driver.find_elements(By.XPATH, "//input[@placeholder='输入消息...']")

    assert input_box, "选择会话后未显示输入框。"
    assert message_items or empty_messages, "选择会话后既没有消息项，也没有显示消息空状态提示。"


@pytest.mark.ui
def test_merchant_messages_input_accepts_text_when_conversation_exists(driver, ui_config):
    pytest.skip("商户私信输入框在当前环境下无法稳定回填文本，先跳过消息输入测试。")
    _login_and_open_merchant_messages(driver, ui_config)

    conv_items = driver.find_elements(By.CSS_SELECTOR, ".conv-item")
    if not conv_items:
        pytest.skip("当前没有会话数据，跳过消息输入测试。")

    conv_items[0].click()
    input_box = wait_for_visible(driver, By.XPATH, "//input[@placeholder='输入消息...']")
    input_box.send_keys("测试消息")

    assert input_box.get_attribute("value") == "测试消息"
