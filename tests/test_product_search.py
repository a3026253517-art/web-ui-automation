"""商品搜索 UI 自动化测试。"""

import allure

from pages.product_search_page import ProductSearchPage


@allure.title("输入商品关键字后应展示匹配的商品")
def test_search_product(driver, config, search_data):
    """验证商品搜索的结果区域和结果内容都与输入关键字相符。"""
    page = ProductSearchPage(driver, config["timeout"])
    product_search = search_data["product_search"]
    keyword = product_search["keyword"]
    expected_product = product_search["expected_product"]

    with allure.step("打开商品列表页面"):
        page.open(config["automation_exercise_products_url"])

    with allure.step(f"搜索商品：{keyword}"):
        page.search(keyword)

    with allure.step("验证页面显示搜索结果且包含目标商品"):
        assert "SEARCHED PRODUCTS" in page.searched_products_title().upper(), (
            "提交搜索后，没有显示搜索结果标题"
        )
        assert expected_product in page.searched_product_names(), (
            f"搜索结果中没有找到预期商品：{expected_product}"
        )
