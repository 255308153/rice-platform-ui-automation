import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from common import (
    click_by_text,
    get_alert_text_and_accept,
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_profile(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置个人中心测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/profile")


@pytest.mark.ui
def test_profile_page_default_sections_visible(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    wait_for_visible(driver, By.XPATH, "//div[normalize-space()='个人用户中心']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='个人中心']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='修改个人信息']")
    wait_for_visible(driver, By.XPATH, "//span[normalize-space()='申请身份认证']")
    wait_for_text(driver, By.TAG_NAME, "h3", "个人中心")
    wait_for_visible(driver, By.XPATH, "//h4[contains(normalize-space(),'我的订单')]")
    wait_for_visible(driver, By.XPATH, "//h4[contains(normalize-space(),'我的发帖')]")
    wait_for_visible(driver, By.XPATH, "//h4[contains(normalize-space(),'我的评论')]")
    wait_for_visible(driver, By.XPATH, "//h4[contains(normalize-space(),'我的收藏')]")


@pytest.mark.ui
def test_profile_can_switch_to_edit_profile_section(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    click_by_text(driver, "span", "修改个人信息")

    wait_for_text(driver, By.TAG_NAME, "h3", "修改个人信息")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入手机号']")
    wait_for_visible(driver, By.XPATH, "//button[contains(@class,'btn-upload-avatar')]")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='保存资料']")
    wait_for_visible(driver, By.XPATH, "//h4[normalize-space()='收货地址']")


@pytest.mark.ui
def test_profile_phone_input_accepts_text(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    click_by_text(driver, "span", "修改个人信息")
    phone_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入手机号']")
    phone_input.clear()
    phone_input.send_keys("13800138000")

    assert phone_input.get_attribute("value") == "13800138000"


@pytest.mark.ui
def test_profile_can_switch_to_certification_section(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    click_by_text(driver, "span", "申请身份认证")

    wait_for_text(driver, By.TAG_NAME, "h3", "申请身份认证")
    wait_for_visible(driver, By.XPATH, "//h4[normalize-space()='我的申请记录']")
    cert_form = driver.find_elements(By.CSS_SELECTOR, ".cert-form")
    cert_tip = driver.find_elements(By.CSS_SELECTOR, ".cert-tip")
    assert cert_form or cert_tip, "认证页既没有申请表单，也没有当前角色提示。"


@pytest.mark.ui
def test_profile_certification_empty_credentials_validation(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    click_by_text(driver, "span", "申请身份认证")
    cert_form = driver.find_elements(By.CSS_SELECTOR, ".cert-form")
    if not cert_form:
        pytest.skip("当前账号不是普通用户，跳过认证申请表单校验。")

    click_by_text(driver, "button", "提交认证申请")
    assert get_alert_text_and_accept(driver) == "请填写资质说明"


@pytest.mark.ui
def test_profile_order_status_filter_can_switch(driver, ui_config):
    _login_and_open_profile(driver, ui_config)

    order_status_select = Select(wait_for_visible(driver, By.XPATH, "(//h4[contains(normalize-space(),'我的订单')]/ancestor::section[contains(@class,'center-card')]//select)[1]"))
    assert order_status_select.first_selected_option.text.strip() == "全部状态"

    order_status_select.select_by_value("3")
    assert order_status_select.first_selected_option.text.strip() == "已完成"
