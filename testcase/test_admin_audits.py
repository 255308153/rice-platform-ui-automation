import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

from common import (
    click_by_text,
    get_alert_text_and_accept,
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_admin_audits(driver, ui_config):
    require_credentials(
        ui_config.admin_username,
        ui_config.admin_password,
        "未设置管理员审核测试账号环境变量 `RICE_UI_ADMIN_USERNAME/RICE_UI_ADMIN_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.admin_username, ui_config.admin_password)
    driver.get(f"{ui_config.admin_base_url}/admin/audits")


@pytest.mark.ui
def test_admin_audits_page_default_sections_visible(driver, ui_config):
    _login_and_open_admin_audits(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "资质审核")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='刷新']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='商户申请']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='专家申请']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='待审核']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='已通过']")
    wait_for_visible(driver, By.XPATH, "//select/option[normalize-space()='已拒绝']")


@pytest.mark.ui
def test_admin_audits_filters_can_switch(driver, ui_config):
    _login_and_open_admin_audits(driver, ui_config)

    selects = driver.find_elements(By.TAG_NAME, "select")
    assert len(selects) >= 2, "审核页筛选下拉框数量不符合预期。"

    role_select = Select(selects[0])
    status_select = Select(selects[1])

    role_select.select_by_value("EXPERT")
    assert role_select.first_selected_option.text.strip() == "专家申请"

    status_select.select_by_value("1")
    assert status_select.first_selected_option.text.strip() == "已通过"


@pytest.mark.ui
def test_admin_audits_show_items_or_empty_state(driver, ui_config):
    _login_and_open_admin_audits(driver, ui_config)

    WebDriverWait(driver, 5).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, ".audit-item")
        or d.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无审核申请']")
    )
    audit_items = driver.find_elements(By.CSS_SELECTOR, ".audit-item")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and normalize-space()='暂无审核申请']")

    assert audit_items or empty_state, "审核页既没有审核项，也没有显示空状态提示。"


@pytest.mark.ui
def test_admin_audits_reject_dialog_validates_empty_remark(driver, ui_config):
    _login_and_open_admin_audits(driver, ui_config)

    reject_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='拒绝']")
    if not reject_buttons:
        pytest.skip("当前没有待审核申请，跳过拒绝备注校验测试。")

    reject_buttons[0].click()
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='拒绝申请']")
    click_by_text(driver, "button", "确认提交")

    assert get_alert_text_and_accept(driver) == "拒绝申请时请填写审核备注"


@pytest.mark.ui
def test_admin_audits_can_open_and_cancel_approve_dialog(driver, ui_config):
    _login_and_open_admin_audits(driver, ui_config)

    approve_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='通过']")
    if not approve_buttons:
        pytest.skip("当前没有待审核申请，跳过通过弹窗展示测试。")

    approve_buttons[0].click()
    wait_for_visible(driver, By.XPATH, "//h3[normalize-space()='通过申请']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='确认提交']")
    click_by_text(driver, "button", "取消")

    dialogs = driver.find_elements(By.XPATH, "//h3[normalize-space()='通过申请']")
    assert not dialogs, "点击取消后，通过申请弹窗未关闭。"
