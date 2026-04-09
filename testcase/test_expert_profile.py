import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_expert_profile(driver, ui_config):
    require_credentials(
        ui_config.expert_username,
        ui_config.expert_password,
        "未设置专家个人中心测试账号环境变量 `RICE_UI_EXPERT_USERNAME/RICE_UI_EXPERT_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.expert_username, ui_config.expert_password)
    driver.get(f"{ui_config.user_base_url}/expert/profile")


@pytest.mark.ui
def test_expert_profile_page_default_sections_visible(driver, ui_config):
    _login_and_open_expert_profile(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "专家个人中心")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='认证状态']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='我的回复']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='我的收藏']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='我的私信']")
    wait_for_visible(driver, By.XPATH, "//div[contains(@class,'cert-status')]")


@pytest.mark.ui
def test_expert_profile_can_switch_to_replies_tab(driver, ui_config):
    _login_and_open_expert_profile(driver, ui_config)

    click_by_text(driver, "button", "我的回复")
    reply_items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无回复记录']")

    assert reply_items or empty_state, "专家回复页签既没有回复项，也没有显示空状态提示。"


@pytest.mark.ui
def test_expert_profile_can_switch_to_favorites_tab(driver, ui_config):
    _login_and_open_expert_profile(driver, ui_config)

    click_by_text(driver, "button", "我的收藏")
    favorite_items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无收藏']")

    assert favorite_items or empty_state, "专家收藏页签既没有收藏项，也没有显示空状态提示。"


@pytest.mark.ui
def test_expert_profile_can_switch_to_messages_tab(driver, ui_config):
    _login_and_open_expert_profile(driver, ui_config)

    click_by_text(driver, "button", "我的私信")
    message_items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无私信']")

    assert message_items or empty_state, "专家私信页签既没有消息项，也没有显示空状态提示。"
