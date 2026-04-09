import pytest
from selenium.webdriver.common.by import By

from common import (
    login_user_front,
    require_credentials,
    wait_for_text,
    wait_for_url_contains,
    wait_for_visible,
)


def _login_and_open_post_detail(driver, ui_config):
    require_credentials(
        ui_config.user_username,
        ui_config.user_password,
        "未设置帖子详情测试账号环境变量 `RICE_UI_USER_USERNAME/RICE_UI_USER_PASSWORD`。",
    )
    login_user_front(driver, ui_config.user_base_url, ui_config.user_username, ui_config.user_password)
    driver.get(f"{ui_config.user_base_url}/forum")

    post_titles = driver.find_elements(By.CSS_SELECTOR, ".post-title")
    if not post_titles:
        pytest.skip("当前论坛没有帖子数据，跳过帖子详情页测试。")

    post_titles[0].click()
    assert wait_for_url_contains(driver, "/post/"), f"点击后未跳转帖子详情页，当前 URL: {driver.current_url}"


@pytest.mark.ui
def test_post_detail_page_default_sections_visible(driver, ui_config):
    _login_and_open_post_detail(driver, ui_config)

    wait_for_visible(driver, By.CSS_SELECTOR, ".post-detail")
    wait_for_visible(driver, By.XPATH, "//button[contains(normalize-space(),'返回')]")
    wait_for_visible(driver, By.XPATH, "//button[contains(@class,'author-entry')]")
    wait_for_visible(driver, By.XPATH, "//button[contains(@class,'btn-like')]")
    wait_for_visible(driver, By.XPATH, "//button[contains(@class,'btn-fav')]")
    wait_for_visible(driver, By.XPATH, "//h3[contains(normalize-space(),'评论（')]")


@pytest.mark.ui
def test_post_detail_comment_input_accepts_text(driver, ui_config):
    _login_and_open_post_detail(driver, ui_config)

    comment_input = wait_for_visible(driver, By.XPATH, "//textarea[@placeholder='写评论...']")
    comment_input.send_keys("测试评论内容")

    assert comment_input.get_attribute("value") == "测试评论内容"


@pytest.mark.ui
def test_post_detail_show_comments_or_empty_state(driver, ui_config):
    _login_and_open_post_detail(driver, ui_config)

    comment_items = driver.find_elements(By.CSS_SELECTOR, ".comment")
    empty_state = driver.find_elements(By.XPATH, "//div[contains(@class,'empty') and contains(normalize-space(),'暂无评论')]")

    assert comment_items or empty_state, "帖子详情页既没有评论项，也没有显示空状态提示。"
