import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pages.base_page import BasePage


class ItemPage(BasePage):
    """旅行项目页面的操作封装。"""

    # 公开练习站保存旅行项目时偶发响应较慢，最多等待 30 秒。
    ITEM_SAVE_TIMEOUT_SECONDS = 30

    # 顶部导航中的“追踪您的旅程”链接，点击后进入旅行项目列表页。
    ITEMS_NAVIGATION_LINK = (By.ID, "items-link")

    # 旅行项目列表页右上角的“添加旅行项目”按钮，用于打开新增弹窗。
    CREATE_ITEM_BUTTON = (By.ID, "create-item-btn")

    # 新增/编辑旅行项目时出现的整个弹窗区域，用于等待弹窗关闭。
    ITEM_MODAL = (By.ID, "modal-content")

    # 旅行目的地输入框，例如填写 Guangzhou。
    ITEM_NAME_INPUT = (By.ID, "item-name")

    # 旅行类型原生下拉框，例如文化、休闲。
    ITEM_CATEGORY_SELECT = (By.ID, "item-category")

    # 旅行费用输入框，只能填写大于 0 的数字。
    ITEM_COST_INPUT = (By.ID, "item-cost")

    # 旅行状态原生下拉框，例如计划、完成。
    ITEM_STATUS_SELECT = (By.ID, "item-status")

    # 新增旅行项目弹窗右下角的“保存”按钮。
    SAVE_ITEM_BUTTON = (By.ID, "submit-btn")

    # 未填写旅行目的地时显示的红色校验提示。
    NAME_ERROR = (By.ID, "name-error")

    # 未填写有效旅行费用时显示的红色校验提示。
    COST_ERROR = (By.ID, "cost-error")

    # 旅行项目列表右上角显示总费用的绿色区域。
    TOTAL_COST = (By.CSS_SELECTOR, "div.total-cost")

    # 表格中每条旅行项目的费用单元格。
    ITEM_COST_CELLS = (By.CSS_SELECTOR, "tbody.table-body td.cell-cost")

    def open_items_page(self):
        """从顶部导航进入旅行项目列表页。"""
        self.click(self.ITEMS_NAVIGATION_LINK)

    def open_create_item_dialog(self):
        """点击“添加旅行项目”，打开新增弹窗。"""
        self.click(self.CREATE_ITEM_BUTTON)

    def create_item(
        self,
        name: str,
        category_value: str,
        cost: str,
        status_value: str,
    ):
        """填写新增旅行项目表单并保存。

        category_value 和 status_value 要传 HTML option 的原始 value，
        不使用浏览器翻译后的中文文字。
        """
        self.fill(self.ITEM_NAME_INPUT, name)
        self.select_by_value(self.ITEM_CATEGORY_SELECT, category_value)
        self.fill(self.ITEM_COST_INPUT, cost)
        self.select_by_value(self.ITEM_STATUS_SELECT, status_value)
        self.click(self.SAVE_ITEM_BUTTON)

    def wait_until_item_dialog_closed(self):
        """保存成功后，等待新增旅行项目弹窗从页面中消失。

        保存过程出现“Saving travel item...”加载层时，仍以弹窗消失作为成功条件。
        """
        save_wait = WebDriverWait(self.driver, self.ITEM_SAVE_TIMEOUT_SECONDS)
        return save_wait.until(EC.invisibility_of_element_located(self.ITEM_MODAL))

    def name_error_text(self) -> str:
        """读取旅行目的地输入框下方的校验提示文字。"""
        return self.text_of(self.NAME_ERROR)

    def cost_error_text(self) -> str:
        """读取旅行费用输入框下方的校验提示文字。"""
        return self.text_of(self.COST_ERROR)

    def is_item_dialog_visible(self) -> bool:
        """判断新增旅行项目弹窗是否仍显示在页面上。"""
        elements = self.driver.find_elements(*self.ITEM_MODAL)
        return bool(elements) and elements[0].is_displayed()

    def validation_alert_text(self) -> str:
        """等待空表单提交后出现的浏览器原生校验弹窗，并读取其文字。"""
        return self.wait.until(EC.alert_is_present()).text

    def accept_validation_alert(self):
        """关闭浏览器原生校验弹窗，使 Selenium 可以继续操作页面。"""
        self.wait.until(EC.alert_is_present()).accept()

    def destination_cell(self, name: str):
        """按目的地名称生成对应表格单元格的定位器。

        不使用 travel-row-1 这类会随行数变化的编号，
        而是查找目的地文本完全等于 name 的单元格。
        """
        return (
            By.XPATH,
            "//tbody[contains(@class, 'table-body')]"
            f"//td[contains(@class, 'cell-destination') and normalize-space()='{name}']",
        )

    def wait_until_item_visible(self, name: str):
        """等待指定目的地出现在旅行项目列表中。"""
        return self.wait.until(EC.visibility_of_element_located(self.destination_cell(name)))

    def status_dropdown(self, name: str):
        """按目的地名称定位同一行的旅行状态下拉框。

        页面中的 status-dropdown-1 编号会随行号变化，
        因此先锁定目的地所在的 tr，再在该行内查找状态下拉框。
        """
        return (
            By.XPATH,
            "//tbody[contains(@class, 'table-body')]"
            f"//tr[.//td[contains(@class, 'cell-destination') and normalize-space()='{name}']]"
            "//select[contains(@class, 'status-dropdown')]",
        )

    def update_item_status(self, name: str, status_value: str):
        """将指定旅行项目的状态改为传入的原始 value。"""
        self.select_by_value(self.status_dropdown(name), status_value)

    def selected_status_value(self, name: str) -> str:
        """读取指定旅行项目当前被选中的状态原始 value。"""
        element = self.wait.until(EC.visibility_of_element_located(self.status_dropdown(name)))
        return Select(element).first_selected_option.get_attribute("value")

    def delete_button(self, name: str):
        """按目的地名称定位同一行的删除按钮。

        不使用 delete-btn-1 这类随行号变化的 ID，
        避免列表排序或增删后操作到错误记录。
        """
        return (
            By.XPATH,
            "//tbody[contains(@class, 'table-body')]"
            f"//tr[.//td[contains(@class, 'cell-destination') and normalize-space()='{name}']]"
            "//button[contains(@class, 'btn-delete')]",
        )

    def delete_item(self, name: str):
        """点击指定旅行项目所在行的删除按钮。"""
        self.click(self.delete_button(name))

    def wait_until_item_disappears(self, name: str):
        """等待指定目的地从旅行项目列表中消失。"""
        return self.wait.until(EC.invisibility_of_element_located(self.destination_cell(name)))

    def total_cost_value(self) -> int:
        """读取总费用区域中的金额，并转换为整数。

        页面可能显示英文的 'Total Cost: $123'，也可能被浏览器翻译为中文。
        两种文本都提取其中的数字，因此不依赖界面语言。
        """
        total_cost_text = self.text_of(self.TOTAL_COST).replace(",", "")
        matched = re.search(r"\d+", total_cost_text)
        if matched is None:
            raise ValueError(f"无法从总费用文本中提取金额：{total_cost_text}")
        return int(matched.group())

    def listed_cost_sum(self) -> int:
        """计算当前表格全部旅行项目费用的总和。

        费用单元格可能显示 '$123' 或 '123美元'，只提取数字，
        因此不受浏览器翻译影响。
        """
        cost_cells = self.wait.until(lambda driver: driver.find_elements(*self.ITEM_COST_CELLS))
        costs = []
        for cell in cost_cells:
            matched = re.search(r"\d+", cell.text.replace(",", ""))
            if matched is None:
                raise ValueError(f"无法从费用单元格中提取金额：{cell.text}")
            costs.append(int(matched.group()))
        return sum(costs)
