import pytest
from selenium.webdriver.common.by import By

from common import (
    click_by_text,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


@pytest.mark.ui
def test_user_home_sections_visible_after_login(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置前台首页测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )

    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)

    wait_for_visible(driver, By.CLASS_NAME, "welcome-banner")
    wait_for_visible(driver, By.XPATH, "//section[contains(@class,'notice-board')]//h3[normalize-space()='系统公告']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='最近订单']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='商品购买']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='AI服务']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='助农论坛']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='我的订单']")


@pytest.mark.ui
def test_user_home_quick_link_to_shop(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置前台首页测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )

    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    click_by_text(driver, "div", "商品购买")

    assert wait_for_url_contains(driver, "/shop"), f"点击商品购买后未跳转商城页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_user_home_recent_orders_link_to_orders(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置前台首页测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )

    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    click_by_text(driver, "button", "查看全部")

    assert wait_for_url_contains(driver, "/orders"), f"点击查看全部后未跳转订单页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_expert_dashboard_sections_visible_after_login(driver, ui_config):
    require_credentials(
        ui_config.expert_username,
        ui_config.expert_password,
        "未设置专家测试账号环境变量 `RICE_UI_EXPERT_USERNAME/RICE_UI_EXPERT_PASSWORD`。",
    )

    login_user_front(driver, ui_config.user_base_url, ui_config.expert_username, ui_config.expert_password)

    assert wait_for_url_contains(driver, "/expert"), f"专家登录后未跳转工作台，当前 URL: {driver.current_url}"
    wait_for_text(driver, By.TAG_NAME, "h2", "专家工作台")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='系统公告']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='未读私信']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='待回复求助']")
    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='我的回复']")
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='待回复求助帖']")


@pytest.mark.ui
def test_expert_dashboard_forum_entry_navigates_to_forum(driver, ui_config):
    require_credentials(
        ui_config.expert_username,
        ui_config.expert_password,
        "未设置专家测试账号环境变量 `RICE_UI_EXPERT_USERNAME/RICE_UI_EXPERT_PASSWORD`。",
    )

    login_user_front(driver, ui_config.user_base_url, ui_config.expert_username, ui_config.expert_password)
    click_by_text(driver, "button", "查看论坛")

    assert wait_for_url_contains(driver, "/forum"), f"点击查看论坛后未跳转论坛页，当前 URL: {driver.current_url}"
