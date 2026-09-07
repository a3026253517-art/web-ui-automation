from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class LoginPage(BasePage):
    # 元素的定位器：By.ID 表示通过 HTML 中的 id 属性查找元素。
    OPEN_LOGIN_BUTTON = (By.ID, "login-btn")  # 首页的“登录”按钮
    USERNAME_INPUT = (By.ID, "login-username")  # 登录弹窗中的账号/邮箱输入框
    PASSWORD_INPUT = (By.ID, "login-password")  # 登录弹窗中的密码输入框
    SUBMIT_LOGIN_BUTTON = (By.ID, "login-submit-btn")  # 提交登录信息的按钮
    LOGIN_FORM = (By.ID, "login-modal-content")  # 整个登录弹窗区域，用于判断弹窗是否可见

    def open_login_dialog(self):
        """点击首页右上角的 Login，打开登录弹窗。"""
        self.click(self.OPEN_LOGIN_BUTTON)

    def login(self, email: str, password: str):
        """输入账号和密码，并提交登录。"""
        self.fill(self.USERNAME_INPUT, email)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_LOGIN_BUTTON)

    def wait_until_login_dialog_closed(self):
        """正确登录后，等待登录弹窗从页面中消失。"""
        return self.wait.until(EC.invisibility_of_element_located(self.LOGIN_FORM))

    def is_login_dialog_visible(self):
        elements = self.driver.find_elements(*self.LOGIN_FORM)
        return bool(elements) and elements[0].is_displayed()
