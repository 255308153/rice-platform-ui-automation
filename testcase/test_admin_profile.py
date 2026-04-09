import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from common import (
    login_admin_front,
    require_credentials,
    wait_for_text,
    wait_for_visible,
)


def _login_and_open_admin_profile(driver, ui_config):
    require_credentials(
        ui_config.admin_username,
        ui_config.admin_password,
        "未设置后台个人信息测试账号环境变量 `RICE_UI_ADMIN_USERNAME/RICE_UI_ADMIN_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.admin_username, ui_config.admin_password)
    driver.get(f"{ui_config.admin_base_url}/profile")


def _login_and_open_merchant_profile(driver, ui_config):
    require_credentials(
        ui_config.merchant_username,
        ui_config.merchant_password,
        "未设置商户资料测试账号环境变量 `RICE_UI_MERCHANT_USERNAME/RICE_UI_MERCHANT_PASSWORD`。",
    )
    login_admin_front(driver, ui_config.admin_base_url, ui_config.merchant_username, ui_config.merchant_password)
    driver.get(f"{ui_config.admin_base_url}/profile")


@pytest.mark.ui
def test_admin_profile_page_default_sections_visible(driver, ui_config):
    _login_and_open_admin_profile(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "个人信息")
    wait_for_visible(driver, By.XPATH, "//label[normalize-space()='用户名']")
    wait_for_visible(driver, By.XPATH, "//label[normalize-space()='手机号']")
    wait_for_visible(driver, By.XPATH, "//label[normalize-space()='角色']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='保存']")


@pytest.mark.ui
def test_admin_profile_phone_input_accepts_text(driver, ui_config):
    _login_and_open_admin_profile(driver, ui_config)

    phone_input = wait_for_visible(driver, By.XPATH, "//label[normalize-space()='手机号']/following-sibling::input")
    phone_input.clear()
    phone_input.send_keys("13800138000")

    assert phone_input.get_attribute("value") == "13800138000"


@pytest.mark.ui
def test_merchant_profile_page_default_sections_visible(driver, ui_config):
    _login_and_open_merchant_profile(driver, ui_config)

    wait_for_text(driver, By.TAG_NAME, "h2", "店铺信息")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入店铺名称']")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入店铺联系方式']")
    wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='请输入店铺简介']")
    wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入营业执照编号']")
    wait_for_visible(driver, By.XPATH, "//button[normalize-space()='保存店铺信息']")


@pytest.mark.ui
def test_merchant_profile_inputs_accept_text(driver, ui_config):
    _login_and_open_merchant_profile(driver, ui_config)

    name_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入店铺名称']")
    contact_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入店铺联系方式']")
    license_input = wait_for_visible(driver, By.XPATH, "//input[@placeholder='请输入营业执照编号']")
    WebDriverWait(driver, 5).until(lambda d: name_input.get_attribute("value").strip() != "")

    driver.execute_script(
        """
        const [nameInput, contactInput, licenseInput] = arguments;
        const updateValue = (element, value) => {
          element.value = value;
          element.dispatchEvent(new Event('input', { bubbles: true }));
          element.dispatchEvent(new Event('change', { bubbles: true }));
        };
        updateValue(nameInput, 'ShopAutoTest');
        updateValue(contactInput, '4008009000');
        updateValue(licenseInput, 'LIC2026001');
        """,
        name_input,
        contact_input,
        license_input,
    )

    WebDriverWait(driver, 3).until(lambda d: name_input.get_attribute("value") == "ShopAutoTest")
    WebDriverWait(driver, 3).until(lambda d: contact_input.get_attribute("value") == "4008009000")
    WebDriverWait(driver, 3).until(lambda d: license_input.get_attribute("value") == "LIC2026001")
    assert name_input.get_attribute("value") == "ShopAutoTest"
    assert contact_input.get_attribute("value") == "4008009000"
    assert license_input.get_attribute("value") == "LIC2026001"
