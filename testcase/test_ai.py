import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_ai(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置 AI 模块测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/ai")


@pytest.mark.ui
def test_ai_page_default_sections_visible(driver, ui_config):
    _login_and_open_ai(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h1", "上传图片后，识别结果会自动进入 AI 助手对话")
    wait_for_visible(driver, By.XPATH, "//p[normalize-space()='AI 识别联动']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='图片上传']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='AI 识别结果']")
    wait_for_visible(driver, By.XPATH, "//h2[normalize-space()='AI 助手对话']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='大米品类识别']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='叶片病害识别']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='清空会话']")
    wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='继续追问，例如：这种病害后续 7 天该怎么观察？']")


@pytest.mark.ui
def test_ai_recognition_type_switch_updates_upload_hint(driver, ui_config):
    _login_and_open_ai(driver, ui_config)

    rice_button = wait_for_visible(driver, By.XPATH, "//button[normalize-space()='大米品类识别']")
    disease_button = wait_for_visible(driver, By.XPATH, "//button[normalize-space()='叶片病害识别']")
    wait_for_visible(driver, By.XPATH, "//p[normalize-space()='点击上传品种图片']")
    assert "active" in rice_button.get_attribute("class")

    disease_button.click()

    wait_for_visible(driver, By.XPATH, "//p[normalize-space()='点击上传病害图片']")
    assert "active" in wait_for_visible(driver, By.XPATH, "//button[normalize-space()='叶片病害识别']").get_attribute("class")


@pytest.mark.ui
def test_ai_empty_conversation_state_visible_after_clear(driver, ui_config):
    _login_and_open_ai(driver, ui_config)

    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'chat-empty') and normalize-space()='还没有会话内容，上传图片或输入问题后开始咨询。']")
    click_by_text(driver, "button", "清空会话")
    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'chat-empty') and normalize-space()='还没有会话内容，上传图片或输入问题后开始咨询。']")


@pytest.mark.ui
def test_ai_question_textarea_accepts_input(driver, ui_config):
    _login_and_open_ai(driver, ui_config)

    textarea = wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='继续追问，例如：这种病害后续 7 天该怎么观察？']")
    textarea.send_keys("这是一条自动化测试问题")

    assert textarea.get_attribute("value") == "这是一条自动化测试问题"


@pytest.mark.ui
def test_ai_empty_submit_keeps_conversation_empty(driver, ui_config):
    _login_and_open_ai(driver, ui_config)

    click_by_text(driver, "button", "发送")

    messages = driver.find_elements(By.CSS_SELECTOR, ".message")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'chat-empty') and normalize-space()='还没有会话内容，上传图片或输入问题后开始咨询。']")
    assert not messages and empty_state, "空输入点击发送后，AI 对话区不应新增消息。"
