
from pathlib import Path
from datetime import datetime
import allure
import pytest
import yaml
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def config():
    """读取 config.yaml，整个测试会话只读取一次。"""
    with open(ROOT / "config" / "config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def accounts():
    """读取演示账号和错误账号。"""
    with open(ROOT / "data" / "accounts.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def items_data():
    """读取新增旅行项目所需的测试数据。"""
    with open(ROOT / "data" / "items.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def search_data():
    """读取商品搜索测试数据。"""
    with open(ROOT / "data" / "search.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture
def driver(config):
    """每条用例启动一个全新的 Chrome，结束后关闭。"""
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(config["base_url"])
    yield browser
    try:
        browser.quit()
    except (OSError, WebDriverException) as error:
        # 浏览器或 ChromeDriver 已提前退出时，清理阶段不应覆盖用例本身的测试结果。
        print(f"浏览器已断开，跳过重复关闭：{error}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome = yield
    report = outcome.get_result()
    # 普通失败与预期失败（xfail）都保留截图，方便在 Allure 中查看缺陷现场。
    is_expected_failure = getattr(report, "wasxfail", False)
    if report.when != "call" or not (report.failed or is_expected_failure):
        return
    browser = item.funcargs.get("driver")
    if browser is None:
        return
    screenshot_dir = ROOT / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    filename = f"{item.name}_{datetime.now():%Y%m%d%H%M%S}.PNG"
    screenshot_path = screenshot_dir / filename
    browser.save_screenshot(str(screenshot_path))
    allure.attach.file(str(screenshot_path), name="失败截图",attachment_type=allure.attachment_type.PNG)
