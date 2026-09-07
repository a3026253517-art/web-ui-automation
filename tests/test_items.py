import allure
import pytest
from datetime import datetime
from time import sleep

from pages.item_page import ItemPage
from pages.login_page import LoginPage


def build_unique_item(items_data: dict, label: str = "item") -> dict:
    """复制 YAML 数据并生成本次运行专属的目的地名称。"""
    new_item = items_data["new_item"].copy()
    new_item["name"] = f'{new_item.pop("name_prefix")}_{label}_{datetime.now():%Y%m%d%H%M%S}'
    return new_item


def login_and_open_items(login_page, item_page, accounts):
    """登录练习站后进入旅行项目列表页，供多个用例复用。"""
    login_page.open_login_dialog()
    login_page.login(**accounts["valid_user"])
    assert login_page.wait_until_login_dialog_closed(), "正确登录后，登录弹窗没有关闭"
    item_page.open_items_page()


@allure.title("首次进入旅行项目页时总费用应等于表格费用之和")
def test_total_cost_matches_table_on_initial_items_page_load(driver, config, accounts):
    """验证已有旅行项目加载完成后，总费用不会错误显示为 0。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])

    with allure.step("登录并首次进入旅行项目列表"):
        login_and_open_items(login_page, item_page, accounts)

    with allure.step("验证首次加载的总费用等于表格费用之和"):
        expected_total = item_page.listed_cost_sum()
        actual_total = item_page.total_cost_value()
        assert actual_total == expected_total, (
            f"首次进入页面时，表格费用总和应为 {expected_total}，页面总费用实际为 {actual_total}"
        )


@allure.title("管理员可以新增一条旅行项目")
def test_create_travel_item(driver, config, accounts, items_data):
    """验证保存后，新增的目的地会出现在旅行项目列表中。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])
    new_item = build_unique_item(items_data)

    with allure.step("使用正确账号登录练习站"):
        login_and_open_items(login_page, item_page, accounts)

    with allure.step("打开新增旅行项目弹窗"):
        item_page.open_create_item_dialog()

    with allure.step("填写旅行项目并保存"):
        item_page.create_item(**new_item)
        assert item_page.wait_until_item_dialog_closed(), "保存后，新增旅行项目弹窗没有关闭"

    with allure.step("等待保存完成并刷新列表"):
        # 练习站偶发不实时刷新列表；刷新后验证已持久化的数据。
        sleep(5)
        driver.refresh()

    with allure.step("验证新增的目的地出现在刷新后的列表中"):
        assert item_page.wait_until_item_visible(new_item["name"]), "新增旅行项目没有出现在列表中"


@allure.title("管理员修改旅行项目状态后刷新页面仍应保留")
def test_update_travel_item_status_persists(driver, config, accounts, items_data):
    """验证状态修改会保存到服务端，而不是只暂时显示在当前页面。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])
    new_item = build_unique_item(items_data)

    with allure.step("登录并新增一条待修改的旅行项目"):
        login_and_open_items(login_page, item_page, accounts)
        item_page.open_create_item_dialog()
        item_page.create_item(**new_item)
        assert item_page.wait_until_item_dialog_closed(), "保存后，新增旅行项目弹窗没有关闭"
        sleep(5)
        driver.refresh()
        assert item_page.wait_until_item_visible(new_item["name"]), "待修改的旅行项目没有出现在列表中"

    with allure.step("将旅行状态修改为已完成"):
        item_page.update_item_status(new_item["name"], "Completed")

    with allure.step("等待练习站异步保存状态"):
        # 该练习站未提供可定位的“保存成功”提示；立即刷新会中断异步保存。
        # 这是针对站点限制的同步等待，不用于替代页面元素的显式等待。
        sleep(5)

    with allure.step("刷新页面并验证状态仍为已完成"):
        driver.refresh()
        item_page.wait_until_item_visible(new_item["name"])
        assert item_page.selected_status_value(new_item["name"]) == "Completed", "刷新后旅行状态没有保留为已完成"


@allure.title("删除旅行项目时不应影响其他旅行项目")
def test_delete_travel_item_only_removes_target(driver, config, accounts, items_data):
    """验证删除目标记录后，同次创建的对照记录依旧存在。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])
    control_item = build_unique_item(items_data, "control")
    target_item = build_unique_item(items_data, "target")

    with allure.step("登录并创建删除目标和对照记录"):
        login_and_open_items(login_page, item_page, accounts)

        item_page.open_create_item_dialog()
        item_page.create_item(**control_item)
        assert item_page.wait_until_item_dialog_closed(), "保存对照记录后，弹窗没有关闭"
        # 练习站保存后偶发不立即刷新列表，等待保存完成后主动刷新再确认。
        sleep(5)
        driver.refresh()
        assert item_page.wait_until_item_visible(control_item["name"]), "对照记录没有出现在列表中"

        item_page.open_create_item_dialog()
        item_page.create_item(**target_item)
        assert item_page.wait_until_item_dialog_closed(), "保存删除目标后，弹窗没有关闭"
        sleep(5)
        driver.refresh()
        assert item_page.wait_until_item_visible(target_item["name"]), "删除目标没有出现在列表中"

    with allure.step("删除指定的目标记录"):
        item_page.delete_item(target_item["name"])
        assert item_page.wait_until_item_disappears(target_item["name"]), "点击删除后，目标记录仍在列表中"

    with allure.step("验证对照记录没有被误删"):
        assert item_page.wait_until_item_visible(control_item["name"]), "删除目标记录时，对照记录也被删除了"


@pytest.mark.xfail(
    reason="BecomeQA Lab 新增后偶发列表未同步新记录、总费用与表格数据不一致；单次通过不代表问题已消失。",
)
@allure.title("新增旅行项目后总费用应等于表格费用之和")
def test_total_cost_matches_table_after_creating_item(driver, config, accounts, items_data):
    """验证新增后绿色总费用与表格各行费用相加的结果一致。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])
    new_item = build_unique_item(items_data, "total")

    with allure.step("登录并进入旅行项目列表"):
        login_and_open_items(login_page, item_page, accounts)

    with allure.step("新增一条固定费用的旅行项目"):
        item_page.open_create_item_dialog()
        item_page.create_item(**new_item)
        assert item_page.wait_until_item_dialog_closed(), "保存后，新增旅行项目弹窗没有关闭"

    with allure.step("验证总费用等于表格全部费用之和"):
        expected_total = item_page.listed_cost_sum()
        actual_total = item_page.total_cost_value()
        assert actual_total == expected_total, (
            f"表格费用总和应为 {expected_total}，页面总费用实际为 {actual_total}"
        )


@allure.title("刷新页面后总费用应持续等于表格费用之和")
def test_total_cost_remains_consistent_after_refresh(driver, config, accounts, items_data):
    """验证刷新后总费用不会只短暂正确，随后又回到错误数值。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])
    new_item = build_unique_item(items_data, "total_refresh")

    with allure.step("登录并进入旅行项目列表"):
        login_and_open_items(login_page, item_page, accounts)

    with allure.step("新增一条固定费用的旅行项目"):
        item_page.open_create_item_dialog()
        item_page.create_item(**new_item)
        assert item_page.wait_until_item_dialog_closed(), "保存后，新增旅行项目弹窗没有关闭"

    with allure.step("等待练习站异步保存数据"):
        # 页面没有提供总费用保存完成的可定位提示，先等待异步保存结束。
        sleep(5)

    with allure.step("刷新页面后连续检查八次总费用"):
        driver.refresh()
        item_page.wait_until_item_visible(new_item["name"])
        for check_number in range(1, 9):
            expected_total = item_page.listed_cost_sum()
            actual_total = item_page.total_cost_value()
            assert actual_total == expected_total, (
                f"刷新后的第 {check_number} 次检查：表格费用总和应为 {expected_total}，"
                f"页面总费用实际为 {actual_total}"
            )
            # 该循环的目的就是验证一段时间内的稳定性，因此每次检查间隔 1 秒。
            if check_number < 8:
                sleep(1)


@allure.title("旅行项目必填项为空时应显示校验提示")
def test_required_fields_show_validation_errors(driver, config, accounts):
    """验证空表单不能保存，且目的地和费用都会显示对应提示。"""
    login_page = LoginPage(driver, config["timeout"])
    item_page = ItemPage(driver, config["timeout"])

    with allure.step("登录并打开新增旅行项目弹窗"):
        login_and_open_items(login_page, item_page, accounts)
        item_page.open_create_item_dialog()

    with allure.step("不填写必填项，直接点击保存"):
        item_page.click(item_page.SAVE_ITEM_BUTTON)

    with allure.step("验证浏览器原生校验提示并关闭弹窗"):
        alert_text = item_page.validation_alert_text()
        assert alert_text == "Please fill in all required fields", f"原生校验提示不正确：{alert_text}"
        item_page.accept_validation_alert()

    with allure.step("验证弹窗未关闭且显示目的地与费用行内提示"):
        name_error = item_page.name_error_text()
        cost_error = item_page.cost_error_text()
        assert item_page.is_item_dialog_visible(), "必填项为空时，新增弹窗不应关闭"
        assert name_error, "目的地为空时，没有显示校验提示"
        assert cost_error, "费用为空时，没有显示校验提示"
