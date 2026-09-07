import allure
import pytest

from pages.login_page import LoginPage


@allure.title("管理员使用正确账号可以登录")
def test_valid_login(driver, config, accounts):
    page = LoginPage(driver, config["timeout"])


    with allure.step("打开登录弹窗并输入正确账号"):
        page.open_login_dialog()
        page.login(**accounts["valid_user"])

    with allure.step("验证登录弹窗关闭"):
        assert page.wait_until_login_dialog_closed(), "正确登录后，登录弹窗没有关闭"


@pytest.mark.xfail(
    strict=True,
    reason="BecomeQA Lab 当前错误密码仍会被当作登录成功，等待站点修复。",
)
@allure.title("管理员使用错误账号不可以登录")
def test_invalid_login(driver, config, accounts):
    page = LoginPage(driver, config["timeout"])

    with allure.step("打开登录弹窗并输入错误账号"):
        page.open_login_dialog()
        page.login(**accounts["invalid_user"])

    with allure.step("验证登录弹窗未关闭"):
        assert page.is_login_dialog_visible(),"错误登录后，登录弹窗关闭"
