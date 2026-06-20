# VisionAttend (人脸识别考勤系统) — 领域上下文

## 核心实体

| 术语 | 定义 | 备注 |
|------|------|------|
| **管理员 (User)** | 系统唯一角色，可执行所有操作 | 无学生/教师端 |
| **学生 (Student)** | 被考勤主体，归属于一个班级，可注册人脸特征 | face_embedding 以 JSON 形式存于 Student 模型 |
| **班级 (Class)** | 学生的组织单元 | 与 Course 无直接关联 |
| **课程 (Course)** | 考勤发生的场景（如"高等数学"） | 打卡时可选关联 |
| **考勤 (Attendance)** | 学生的一次打卡记录 | 含 status(present/late/absent)、confidence、关联的课程 |

## 领域规则

- 人脸打卡时只需选择课程（可选），不要求选择班级
- 考勤明细与考勤统计属于同一领域，放在同一页面组件中
- 班级与课程是两条独立的实体链，互不绑定

## 导航布局

- 主窗口使用 qfluentwidgets 的 NavigationInterface 实现侧栏导航
- 通过 QSS + 设计 Token 覆盖 NavigationInterface 的外观以匹配 Figma 设计
- 页面切换使用 QStackedWidget + Router 类管理

## 组件化策略

- 采用积极抽取策略：凡出现 ≥2 次的 UI 模式均封装为独立组件
- 组件置于 `app/components/` 下，页面代码仅负责组装
- 已知候选组件：StatCard、ActionCard、FormCard、DataTable、DeleteConfirm、CourseCombo、CameraWidget

## API 服务层

- 按领域拆分为多个 Service 类，而非单一 ApiService
- `services/api_client.py` 负责 HTTP 基础封装（requests session、token 注入、错误处理）
- 各领域 Service 继承/组合 api_client 提供业务方法

## 状态管理边界

| 状态 | 范围 | 理由 |
|------|------|------|
| Token / 当前用户 | 全局 Store | 所有 API 请求依赖 token |
| 考勤统计数据 | 全局 Store | Dashboard + 考勤记录页共用 |
| 课程列表 | 全局 Store | 打卡页 + 考勤记录页共用 |
| 学生列表 | 本地（页面内） | 仅学生管理页使用 |
| 班级列表 | 本地（页面内） | 仅学生管理页使用 |
| 考勤明细 | 本地（页面内） | 仅考勤记录页使用 |
| 打卡结果 | 本地（页面内） | 一次性展示，不共享 |

## 页面清单

| 路径 | 对应 API | 功能 |
|------|---------|------|
| 登录 (Login) | POST /auth/login | 管理员身份认证 |
| 考勤总览 (Dashboard) | GET /attendance/statistics | 统计卡片 + 图表 + 快捷入口 |
| 人脸打卡 (Check-in) | POST /face/recognize | 摄像头拍照识别，可选课程 |
| 考勤记录 (Records) | GET /attendance, GET /attendance/statistics | 明细表格 + 筛选 + 统计栏 |
| 学生管理 (Students) | GET/POST/DELETE /students, POST /face/register | CRUD + 人脸注册 |
| 课程管理 (Courses) | GET/POST/DELETE /courses | CRUD |
