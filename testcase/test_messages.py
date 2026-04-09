import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from common import (
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_messages(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置私信模块测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/messages")


@pytest.mark.ui
def test_messages_page_default_sections_visible(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "私聊消息")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='发起私聊']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='会话列表']")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索联系人']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='搜索']")
    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'empty-message') and normalize-space()='请选择联系人或会话开始聊天']")


@pytest.mark.ui
def test_messages_contact_role_filter_can_switch(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    role_select = Select(wait_for_visible(driver, By.XPATH, "//section[contains(@class,'contacts')]//select"))
    assert role_select.first_selected_option.text.strip() == "商户+专家"

    role_select.select_by_value("EXPERT")
    assert role_select.first_selected_option.text.strip() == "仅专家"

    role_select.select_by_value("MERCHANT")
    assert role_select.first_selected_option.text.strip() == "仅商户"


@pytest.mark.ui
def test_messages_contact_search_input_accepts_text(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    search_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='搜索联系人']")
    search_input.send_keys("测试联系人")

    assert search_input.get_attribute("value") == "测试联系人"


@pytest.mark.ui
def test_messages_contacts_panel_shows_items_or_empty_state(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    contact_items = driver.find_elements(By.CSS_SELECTOR, ".contact-item")
    empty_contacts = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无可发起联系人']")

    assert contact_items or empty_contacts, "联系人面板既没有联系人项，也没有显示空状态提示。"


@pytest.mark.ui
def test_messages_conversations_panel_shows_items_or_empty_state(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    conversations = driver.find_elements(By.CSS_SELECTOR, ".conv-item")
    empty_conversations = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无会话']")

    assert conversations or empty_conversations, "会话列表既没有会话项，也没有显示空状态提示。"


@pytest.mark.ui
def test_messages_can_select_existing_conversation(driver, ui_config):
    _login_and_open_messages(driver, ui_config)

    conversations = driver.find_elements(By.CSS_SELECTOR, ".conv-item")
    if not conversations:
        pytest.skip("当前账号暂无历史会话，跳过会话切换测试。")

    conversations[0].click()

    wait_for_visible(driver, By.CSS_SELECTOR, ".chat-title")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='输入消息...']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='图片']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='发送']")
