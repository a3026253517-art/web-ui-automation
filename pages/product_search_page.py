"""Automation Exercise 商品搜索页面对象。"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class ProductSearchPage(BasePage):
    """封装商品列表页中的搜索操作和结果读取。"""

    # 商品关键字输入框。
    SEARCH_INPUT = (By.ID, "search_product")
    # 提交商品搜索的按钮。
    SEARCH_BUTTON = (By.ID, "submit_search")
    # 搜索成功后显示的 “Searched Products” 标题。
    SEARCHED_PRODUCTS_TITLE = (
        By.XPATH,
        "//h2[contains(translate(normalize-space(), "
        "'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), "
        "'SEARCHED PRODUCTS')]",
    )
    # 搜索结果卡片中的商品名称。
    SEARCH_RESULT_PRODUCT_NAMES = (By.CSS_SELECTOR, ".features_items .productinfo p")

    def search(self, keyword):
        """输入关键词并提交搜索。"""
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)

    def searched_products_title(self):
        """等待并读取搜索结果区域标题。"""
        return self.text_of(self.SEARCHED_PRODUCTS_TITLE)

    def searched_product_names(self):
        """等待搜索结果渲染完毕，并返回页面上的全部商品名称。"""
        elements = self.wait.until(
            EC.visibility_of_all_elements_located(self.SEARCH_RESULT_PRODUCT_NAMES)
        )
        return [element.text.strip() for element in elements if element.text.strip()]
