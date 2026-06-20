# VisionAttend 前端架构说明

> PySide6 + qfluentwidgets 人脸识别考勤系统前端

---

## 一、技术栈

| 层 | 技术 | 版本 |
|------|------|------|
| Qt 绑定 | PySide6 | 6.11.1 |
| UI 组件库 | qfluentwidgets（PySide6-Fluent-Widgets） | 1.11.2 |
| 图标 | qtawesome（Font Awesome） | 1.4.2 |
| 摄像头 | opencv-python-headless | 4.13.0 |
| 图表 | pyqtgraph | 0.14.0 |
| HTTP | requests | 2.34.2 |
| 数据模型 | pydantic | 2.13.x |
| 图像处理 | pillow + numpy | 最新 |
| 日志 | loguru | 0.7.x |
| Python | CPython | 3.13.13 |
| 包管理 | uv | 0.11.19 |

---

## 二、目录结构

```
frontend/
├── main.py                       # 应用入口：QApp → 登录 → 主窗口
├── pyproject.toml                # 依赖管理
├── uv.lock                       # 锁定版本
├── .python-version               # Python 3.13.13
├── resources/                    # 静态资源
│   ├── icons/                    # 图标文件
│   ├── fonts/                    # 字体文件
│   └── styles/                   # 样式系统
│       ├── base.qss              # QSS 模板（含 {placeholder}）
│       └── themes/
│           ├── theme_dark.json   # 暗色 Token 原始值
│           └── theme_light.json  # 亮色 Token 原始值
├── app/                          # 应用代码
│   ├── core/                     # 基础设施层
│   │   ├── theme.py              # ThemeManager + 设计 Token
│   │   ├── router.py             # 页面路由
│   │   ├── store.py              # 全局状态管理
│   │   └── event_bus.py          # 全局信号总线
│   ├── components/               # 可复用 UI 组件库
│   │   ├── stat_card.py          # 统计卡片
│   │   ├── action_card.py        # 操作卡片
│   │   ├── form_card.py          # 表单卡片容器
│   │   ├── data_table.py         # 通用表格
│   │   ├── course_combo.py       # 课程下拉框
│   │   └── delete_confirm.py     # 删除确认弹窗
│   ├── pages/                    # 业务页面
│   │   ├── base_page.py          # 页面基类
│   │   ├── login/                # 登录页
│   │   ├── dashboard/            # 考勤总览
│   │   ├── checkin/              # 人脸打卡（含 CameraWidget）
│   │   ├── attendance/           # 考勤记录（表格+统计）
│   │   ├── students/             # 学生管理（CRUD+人脸注册）
│   │   └── courses/              # 课程管理（CRUD）
│   ├── services/                 # API 服务层
│   │   ├── api_client.py         # HTTP 基础封装
│   │   ├── auth_service.py       # 登录/登出
│   │   ├── student_service.py    # 学生 CRUD + 人脸
│   │   ├── course_service.py     # 课程 + 班级
│   │   └── attendance_service.py # 考勤明细 + 统计
│   └── models/                   # Pydantic 数据模型
│       ├── user.py               # 管理员
│       ├── student.py            # 学生
│       ├── course.py             # 课程 + 班级
│       └── attendance.py         # 考勤记录 + 统计
└── tests/                        # 单元测试
```

---

## 三、架构分层

```
┌──────────────────────────────────────────────────┐
│  Pages — 业务页面                                  │
│  (Login, Dashboard, Checkin, Attendance, ...)      │
├──────────────────────┬───────────────────────────┤
│  Components          │  Services + Models         │
│  (可复用 UI 组件)     │  (API 调用 + 数据模型)       │
├──────────────────────┴───────────────────────────┤
│  Core (基础设施)                                   │
│  ThemeManager / Router / AppStore / SignalBus     │
├──────────────────────────────────────────────────┤
│  PySide6 + qfluentwidgets + qtawesome + pyqtgraph │
└──────────────────────────────────────────────────┘
```

### 数据流方向

```
用户操作 → Page → Service(HTTP) → 后端 API
                    ↓
              Store(信号) → Page UI 自动刷新
```

### 信号流向

```
Service (数据变更) →  emit → SignalBus → Page.connect()
组件 (用户操作)    →  emit → SignalBus → MainWindow/Router
ThemeManager      →  emit → 所有 Widget → style().polish()
```

---

## 四、核心模块说明

### 4.1 ThemeManager (`core/theme.py`)

设计 Token 系统：所有颜色、间距、字号、圆角值集中管理，供 QPalette 和 QSS 模板使用。

```
Design → JSON Tokens → ThemeManager → QPalette + QSS
                              ↓
                         signal: theme_changed
```

### 4.2 Router (`core/router.py`)

基于 QStackedWidget 的页面路由。页面通过 `register(name, widget)` 注册，通过 `navigate(name)` 跳转。

```
Router.register("dashboard", DashboardPage)
Router.navigate("checkin")  → 触发 checkin_page.on_enter()
```

### 4.3 AppStore (`core/store.py`)

全局状态管理。按范围划分：

| 全局 | 页面本地 |
|------|---------|
| Token/当前用户 | 学生列表 |
| 考勤统计数据 | 班级列表 |
| 课程列表 | 考勤明细 |

### 4.4 ApiClient (`services/api_client.py`)

HTTP 基础封装，处理：
- Session 管理 + Token 自动注入
- 统一错误处理（ConnectionError、HTTP 4xx/5xx → ApiResult）
- 文件上传支持（`_post_file`）

各领域 Service 通过继承 ApiClient 获得一致的请求接口。

---

## 五、设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 导航方案 | qfluentwidgets NavigationInterface | 内置展开/收起/高亮/底部卡片，QSS 覆盖后匹配 Figma |
| 组件抽取策略 | 积极抽取（≥2次即封装） | 代码复用度高，毕设可写"组件化设计" |
| API 服务层 | 按领域拆分多 Service | 关注点分离，每个 Service 聚焦一个领域 |
| 状态管理 | QObject-based Store + SignalBus | 结构清晰，Qt 原生响应式模式 |
| 主题系统 | Python Token 类 + QSS 模板替换 | 比 `QPalette` 更灵活，比主题库更可控 |
| 数据模型 | Pydantic BaseModel | 类型安全，运行时验证 |
| 页面切换 | QStackedWidget + Router | 轻量、可控、生命周期清晰 |

---

## 六、启动方式

```bash
# 1. 进入项目目录
cd F:/face-recognition/frontend

# 2. 确保依赖已安装
uv sync

# 3. 启动前端
uv run python main.py

# 确保后端已启动（在另一个终端）
cd F:/face-recognition/backend
uv run python run.py
```

---

## 七、剩余工作（TODO）

当前骨架已完成以下文件的创建：

- [x] `core/` — theme / router / store / event_bus
- [x] `services/` — api_client / auth / student / course / attendance
- [x] `models/` — user / student / course / attendance
- [x] `components/` — stat_card / action_card / form_card / data_table / course_combo / delete_confirm
- [x] `pages/` — base_page + 6 个页面骨架 + camera_widget
- [x] `main.py` — 入口骨架
- [x] `resources/` — base.qss 模板 + theme_dark.json

**待填充（下一个阶段）**：
1. `main.py` — 完整的 NavigationInterface + QStackedWidget 布局（需要对接 qfluentwidgets API）
2. 每个 page 的实质性 UI 代码（当前为占位 + TODO 注释）
3. pages/ 下各页的 `__init__.py`
4. 与后端的联调测试
