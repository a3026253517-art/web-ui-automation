from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select


class BasePage:
    """所有 Page Object 共用的浏览器操作。"""

    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        self.driver.get(url)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def fill(self, locator, value: str):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(value)

    def text_of(self, locator) -> str:
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def select_by_value(self, locator, value: str):
        """等待原生下拉框可见，并按 option 的 value 属性选择选项。"""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        Select(element).select_by_value(value)
