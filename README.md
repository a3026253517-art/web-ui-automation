# Web UI 自动化回归测试项目

基于 Python、Selenium、pytest、YAML 和 Allure 的个人练习项目，练习页面对象封装、业务断言、等待、异常排查和测试报告。

## 测试对象

| 站点 | 测试范围 |
| --- | --- |
| [BecomeQA Lab](https://lab.becomeqa.com) | 登录、旅行事项新增、状态修改、删除、表单校验、总费用一致性 |
| [Automation Exercise 商品页](https://automationexercise.com/products) | 商品关键词搜索 |

两个站点的业务没有关联。本项目不是企业生产系统测试，也不代表覆盖了任一站点的全部功能。

## 技术实现与目录

- BasePage 封装点击、输入、文本读取、原生下拉选择及相关显式等待。
- 页面对象保存定位器，将通用操作组合成登录、事项管理和搜索操作。
- pytest fixture 读取 YAML；每条用例启动和关闭 Chrome。
- 测试用例组织业务步骤，通过断言比较实际结果与预期结果。
- Allure 展示中文步骤和结果；测试执行阶段失败或带预期失败结果时，钩子尝试保存并附加截图。

```text
web_ui_automation/
├── config/config.yaml          # 两个站点的地址和默认等待超时
├── data/
│   ├── accounts.yaml           # 公开演示账号及错误密码数据
│   ├── items.yaml              # 旅行事项测试数据
│   └── search.yaml             # 商品关键词与预期商品
├── pages/
│   ├── base_page.py            # 通用操作
│   ├── login_page.py           # 登录页面对象
│   ├── item_page.py            # 旅行事项页面对象
│   └── product_search_page.py  # 商品搜索页面对象
├── tests/
│   ├── conftest.py             # fixture 和截图钩子
│   ├── test_login.py           # 2 条用例
│   ├── test_items.py           # 7 条用例
│   └── test_product_search.py  # 1 条用例
├── .gitignore
├── requirements.txt
└── README.md
```

## 已实现的 10 条用例

| 场景 | 当前主要检查点 |
| --- | --- |
| 正确密码登录 | 登录弹窗关闭 |
| 错误密码登录 | 登录弹窗仍可见；已标记预期失败 |
| 新增旅行事项 | 保存后刷新，新增目的地出现在列表 |
| 修改旅行状态 | 改为 Completed 后刷新，选中值仍为 Completed |
| 删除指定事项 | 目标记录消失，同次创建的对照记录仍存在 |
| 首次进入列表的总费用 | 当前表格费用之和与总费用显示一致 |
| 新增后的总费用 | 表格费用之和与总费用显示一致；已标记预期失败 |
| 刷新后的费用一致性 | 连续检查 8 次，各次之间暂停 1 秒 |
| 必填项为空 | 原生 Alert 文案、表单弹窗仍可见、两项行内提示非空 |
| 商品搜索 | 搜索结果标题出现，结果中包含 Blue Top |

## 最近一次已提供的全量运行记录

2026-09-05 提供的 pytest 终端截图包含全部 10 条用例，按各条状态汇总为：

```text
8 passed, 1 xfailed, 1 xpassed
```

这是历史运行记录，整理本说明时未重新运行浏览器测试。它不表示 10 条全部通过，也不保证以后每次运行都得到相同结果。

### 已知问题与预期失败标记

| 项目 | 观察与当前处理 |
| --- | --- |
| 错误密码仍可登录 | 练习过程中观察到错误密码被接受；用例保留“应拒绝登录”的预期，使用 `xfail(strict=True)`。本轮为 XFAIL。 |
| 新增后列表更新及总费用异常 | 曾观察到新增后列表未及时更新、费用短暂正确后变为 0 等现象；新增后费用用例使用非严格 xfail。本轮为 XPASS，需继续核对缺陷复现和断言充分性。 |

XFAIL 表示标记过预期失败的用例本轮失败；仍要检查是否因预期的问题失败。XPASS 表示该用例本轮通过，不能据此单独认定缺陷已修复。错误密码用例设置了 strict=True，如果意外通过，会以 [XPASS(strict)] 计入失败，提醒检查标记是否应移除。

### 当前实现的局限

- 登录断言主要检查弹窗状态，尚未补充用户身份或受保护功能验证。
- 部分保存操作使用 sleep(5) 后刷新，固定等待不保证保存完成。刷新后能看到数据，也不能单独证明它保存在服务端。
- 新增后费用用例尚未先确认新记录进入列表；费用与表格都未更新时仍可能通过。首次加载的检查也不等于确认全部数据加载完成。
- 8 次费用采样只覆盖有限观察时间，不能证明所有时刻正确。金额解析目前按正整数处理，未覆盖小数金额等情况。
- 搜索仅验证标题和目标商品存在，尚未验证全部结果相关性、无结果、空关键词等场景。
- 时间戳名称降低重名概率，但不保证并发唯一；没有统一清理本轮创建的数据。关闭浏览器不会删除网站中的业务记录。
- 截图钩子目前处理测试执行阶段，不覆盖所有准备、清理阶段的错误。

## 环境与安装（Windows PowerShell）

已有运行记录的环境为 Windows、Python 3.14.6、Chrome；依赖版本固定在 requirements.txt，其他组合尚未在本项目中验证。

安装 Python 和 Chrome 后，进入包含本 README 的项目根目录，在新下载且尚未创建虚拟环境的副本中执行：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

下文直接使用虚拟环境中的 Python，不要求先运行激活脚本。如果系统只能识别 py 而不是 python，前两条命令可分别使用 `py --version` 和 `py -m venv .venv`。已有可用 .venv 时不必重复创建；下载别人项目时，应在本机重新创建环境，不复制对方的 .venv。

首次启动 Chrome 时，Selenium Manager 可能需要联网获取匹配驱动；需要能访问测试站点及驱动下载服务。参见 [Selenium Manager 官方说明](https://www.selenium.dev/documentation/selenium_manager/)。

### 安装报告查看工具

allure-pytest 用于生成测试结果文件，查看本项目示例报告还需要单独安装 **Allure Report 2 命令行工具**。按 [Allure 2 Windows 安装说明](https://allurereport.org/docs/v2/install-for-windows/) 配置 Java（8 或以上）、JAVA_HOME 和 Allure 的 bin 路径后，检查：

```powershell
java -version
allure --version
```

未安装 Allure 命令行工具时，仍可执行 pytest 并生成原始结果，但不能使用下文的 allure serve 查看报告。

## 配置与运行

config/config.yaml 保存 BecomeQA 首页、Automation Exercise 商品页和默认超时。当前 driver fixture 会先打开 BecomeQA 首页；搜索用例随后跳转到商品页，因此搜索用例也依赖初始首页导航成功。

data/accounts.yaml 只包含本练习使用的公开演示账号和故意设置的错误密码，不要替换为个人真实账号后提交。items.yaml 和 search.yaml 分别保存旅行事项和搜索数据；下拉选项使用页面原始 value（如 Cultural、Completed），不依赖浏览器翻译后的中文。

仅收集用例，不启动浏览器：

```powershell
.\.venv\Scripts\python.exe -m pytest --collect-only -q
```

全量执行并将结果写到新的时间戳目录，避免与旧报告混合：

```powershell
$runResults = "allure-results/run-$(Get-Date -Format 'yyyyMMdd-HHmmss-fff')"
.\.venv\Scripts\python.exe -m pytest -v -s --alluredir="$runResults"
allure serve "$runResults"
```

以上三行应在同一个 PowerShell 窗口执行，报告命令读取本轮目录。即使出现测试失败，也应查看报告分析原因。

单独执行搜索用例：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_product_search.py -v -s
```

测试会实际在公开练习站创建、修改或删除本用例的旅行记录。记录可能留在演示账号中；测试数据隔离和清理仍待完善。

## 报告与截图

Allure 页面中选择用例，展开“测试步骤”下的“失败截图”附件即可查看图片。本地图片位于 screenshots/，原始报告数据位于 allure-results/，二者均不提交到源码仓库。

如需展示项目，可人工选取少量真实截图，检查无个人信息后放入 docs/images/ 并在文档中引用；该目录未被忽略。本版本没有额外复制截图。

## 上传范围

上传项目源码目录 config/、data/、pages/、tests/，以及 .gitignore、requirements.txt 和本 README。

.gitignore 排除虚拟环境、Python 和 pytest 缓存、IDE 配置、原始报告、批量截图、日志、本地 .env、*.local.yaml / *.local.yml 和常见私钥文件。历史误拼目录 allure-tesults/ 也已排除；这些规则不会删除本机文件。

如果使用网页上传或手动打包，必须自行按上述范围选文件，不能依赖 .gitignore 自动过滤。若某个文件已经被 Git 跟踪，新增忽略规则也不会自动将它从版本记录中移除。

发布前检查待提交差异，确认没有个人密码、Cookie、令牌或私钥。忽略规则不是敏感信息检测工具；本次整理只对待发布文本文件做了常见凭证格式检查和账号配置核对，不代表对所有文件或 Git 历史的安全审计。
