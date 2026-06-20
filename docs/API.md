# 后端 API 接口文档

> Base URL: `http://127.0.0.1:5000`
> Content-Type: `application/json`（人脸接口使用 `multipart/form-data`）

---

## 通用说明

### 鉴权方式
- 大部分接口需要在 HTTP Header 中传入 JWT Token：
  ```
  Authorization: Bearer <access_token>
  ```
- Token 通过 `POST /auth/login` 获取
- Token 过期后可通过 `POST /auth/refresh` 刷新
- 部分接口需要 `admin` 角色（如：新增/修改/删除操作）

### 响应格式
- **成功**：返回对应的 JSON 数据体，HTTP 200/201/204
- **失败**：返回 JSON `{"message": "错误描述"}`，HTTP 4xx/5xx

### 通用错误码
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无返回体） |
| 400 | 请求参数错误 |
| 401 | 未登录或 Token 过期 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如学号重复、班级有学生不可删除等） |
| 422 | 参数校验失败 |
| 429 | 登录限流 |
| 500 | 服务器内部错误 |

---

## 一、认证（Auth）

### POST /auth/login — 管理员登录

**请求体**（JSON）：
```json
{
  "username": "admin",
  "password": "123456"
}
```

**成功响应**（200）：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2026-06-16T10:00:00"
  }
}
```

**失败响应**（401）：
```json
{
  "message": "用户名或密码错误"
}
```

> 限制：每分钟最多 10 次登录尝试

---

### POST /auth/refresh — 刷新 Access Token

**请求头**：`Authorization: Bearer <refresh_token>`

**成功响应**（200）：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## 二、班级管理（Class）

### GET /classes — 获取班级列表

**查询参数**（可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| grade | string | 按年级筛选 |

**成功响应**（200）：
```json
[
  {
    "id": 1,
    "name": "计算机科学与技术1班",
    "grade": "2023",
    "created_at": "2026-06-16T10:00:00",
    "updated_at": "2026-06-16T10:00:00"
  }
]
```

---

### POST /classes — 新增班级

> 需要 `admin` 角色

**请求体**（JSON）：
```json
{
  "name": "计算机科学与技术2班",
  "grade": "2023"
}
```

**成功响应**（201）：
```json
{
  "id": 2,
  "name": "计算机科学与技术2班",
  "grade": "2023",
  "created_at": "...",
  "updated_at": "..."
}
```

---

### GET /classes/:class_id — 获取班级详情

**成功响应**（200）：同单条班级对象

---

### PUT /classes/:class_id — 修改班级信息

> 需要 `admin` 角色，支持部分字段更新

**请求体**（JSON，至少传一个字段）：
```json
{
  "name": "新班级名",
  "grade": "2024"
}
```

**成功响应**（200）：同单条班级对象

---

### DELETE /classes/:class_id — 删除班级

> 需要 `admin` 角色。**如果班内有学生则返回 409 拒绝删除**

**成功响应**：204 无返回体
**失败响应**（409）：`{"message": "该班级下还有学生，无法删除"}`

---

## 三、课程管理（Course）

### GET /courses — 获取课程列表

**成功响应**（200）：
```json
[
  {
    "id": 1,
    "name": "高等数学",
    "teacher": "王老师",
    "schedule": "周三 14:00-16:00",
    "created_at": "2026-06-16T10:00:00",
    "updated_at": "2026-06-16T10:00:00"
  }
]
```

---

### POST /courses — 新增课程

> 需要 `admin` 角色

**请求体**（JSON）：
```json
{
  "name": "大学英语",
  "teacher": "李老师",
  "schedule": "周一 08:00-10:00"
}
```

**成功响应**（201）：
```json
{
  "id": 2,
  "name": "大学英语",
  "teacher": "李老师",
  "schedule": "周一 08:00-10:00",
  "created_at": "...",
  "updated_at": "..."
}
```

---

### GET /courses/:course_id — 获取课程详情

**成功响应**（200）：同单条课程对象

---

### PUT /courses/:course_id — 修改课程信息

> 需要 `admin` 角色，支持部分字段更新

**请求体**（JSON，至少一个字段）：
```json
{
  "name": "新名称",
  "teacher": "新教师",
  "schedule": "新时间"
}
```

**成功响应**（200）：同单条课程对象

---

### DELETE /courses/:course_id — 删除课程

> 需要 `admin` 角色。**如果课程已有考勤记录则返回 409 拒绝删除**

**成功响应**：204 无返回体
**失败响应**（409）：`{"message": "该课程已有考勤记录，无法删除"}`

---

## 四、学生管理（Student）

### GET /students — 获取学生列表

**查询参数**（可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| class_id | int | 按班级筛选 |
| has_face | bool | 筛选有无注册人脸（true=已注册，false=未注册） |

**成功响应**（200）：
```json
[
  {
    "id": 1,
    "student_no": "2024001",
    "name": "张三",
    "gender": "男",
    "class_id": 1,
    "has_face": true,
    "created_at": "2026-06-16T10:00:00",
    "updated_at": "2026-06-16T10:00:00"
  }
]
```

> **注意**：`has_face` 是只读字段（由后端根据 `face_embedding` 是否为空自动判断）

---

### POST /students — 新增学生

> 需要 `admin` 角色

**请求体**（JSON）：
```json
{
  "student_no": "2024002",
  "name": "李四",
  "gender": "男",
  "class_id": 1
}
```

**失败响应**（409）：`{"message": "学号 '2024002' 已存在"}`

**成功响应**（201）：
```json
{
  "id": 2,
  "student_no": "2024002",
  "name": "李四",
  "gender": "男",
  "class_id": 1,
  "has_face": false,
  "created_at": "...",
  "updated_at": "..."
}
```

---

### GET /students/:student_id — 获取学生详情

**成功响应**（200）：同单条学生对象

---

### PUT /students/:student_id — 修改学生信息

> 需要 `admin` 角色，支持部分字段更新。
> 如果修改学号，后端会检查唯一性。

**请求体**（JSON，至少一个字段）：
```json
{
  "name": "李四改名字了",
  "class_id": 2
}
```

**成功响应**（200）：同单条学生对象

---

### DELETE /students/:student_id — 删除学生

> 需要 `admin` 角色。同时删除关联的考勤记录。

**成功响应**：204 无返回体

---

## 五、人脸识别（Face）

### POST /face/register — 注册人脸

> 需要 JWT 鉴权。上传一张学生人脸照片，后端提取 embedding 并保存。

**请求格式**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| student_id | int (form) | 学生 ID |
| image | file | 人脸照片（jpg/jpeg/png） |

**成功响应**（200）：
```json
{
  "message": "人脸注册成功",
  "student_id": 1,
  "student_name": "张三",
  "image_path": "uploads/xxxx.jpg"
}
```

**失败响应**：
- 422：`{"message": "请上传图片文件"}`
- 422：`{"message": "student_id 必须是整数"}`
- 422：`{"message": "不支持的图片格式，仅支持 jpg/jpeg/png"}`
- 404：`{"message": "学生 #1 不存在"}`
- 500：`{"message": "人脸特征提取失败: ..."}`

---

### POST /face/recognize — 人脸识别打卡

> **无需 JWT 鉴权**。上传照片，系统自动匹配最相似的学生并记录考勤。

**请求格式**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| image | file | 人脸照片（jpg/jpeg/png） |
| course_id | int (form, 可选) | 课程 ID |

**成功响应 — 匹配成功**（200）：
```json
{
  "is_match": true,
  "student_id": 1,
  "student_name": "张三",
  "student_no": "2024001",
  "distance": 0.2345,
  "confidence": 0.9567,
  "attendance_id": 42,
  "checkin_time": "2026-06-17T14:30:00"
}
```

**成功响应 — 未匹配**（200）：
```json
{
  "is_match": false,
  "student_id": null,
  "student_name": null,
  "distance": 1.2345,
  "message": "未识别到匹配的人脸"
}
```

**失败响应**：
- 422：`{"message": "请上传图片文件"}`
- 400：`{"message": "系统中尚无已注册人脸，请先注册"}`
- 500：`{"message": "人脸特征提取失败: ..."}`

> **说明**：`distance` 越小越好，一般 `< 1.0` 认为是匹配。
> `confidence = 1.0 - (distance / threshold)`，范围 0~1。

---

### GET /face/students — 获取已注册人脸的学生列表

> 需要 JWT 鉴权。返回所有 `face_embedding` 非空的学生精简信息。

**成功响应**（200）：
```json
[
  {
    "id": 1,
    "student_no": "2024001",
    "name": "张三",
    "class_id": 1
  }
]
```

---

## 六、考勤记录（Attendance）

### GET /attendance — 查询考勤记录

**查询参数**（均为可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| course_id | int | 按课程筛选 |
| class_id | int | 按班级筛选（join student 表） |
| student_id | int | 按学生筛选 |
| date_from | date (YYYY-MM-DD) | 起始日期 |
| date_to | date (YYYY-MM-DD) | 结束日期 |

**成功响应**（200）：
```json
[
  {
    "id": 1,
    "student_id": 1,
    "student_name": "张三",
    "course_id": 1,
    "course_name": "高等数学",
    "checkin_time": "2026-06-17T14:30:00",
    "status": "present",
    "confidence": 0.95,
    "created_at": "2026-06-17T14:30:00"
  }
]
```

> `status` 枚举值：`present`（出勤）、`late`（迟到）、`absent`（缺勤）

---

### GET /attendance/statistics — 考勤统计

**查询参数**（与 `/attendance` 相同）：

| 参数 | 类型 | 说明 |
|------|------|------|
| course_id | int | 按课程筛选 |
| class_id | int | 按班级筛选 |
| student_id | int | 按学生筛选 |
| date_from | date | 起始日期，不传则默认最近 7 天 |
| date_to | date | 结束日期，不传则默认今天 |

**成功响应**（200）：
```json
{
  "total": 245,
  "present": 182,
  "late": 23,
  "absent": 40,
  "rate": 74.29,
  "date_from": "2026-06-10",
  "date_to": "2026-06-17"
}
```

> `rate` 为出勤率百分比（浮点数）

---

## 接口汇总速查表

| 方法 | 路径 | 鉴权 | 角色 | 说明 |
|------|------|------|------|------|
| POST | `/auth/login` | ❌ | - | 登录 |
| POST | `/auth/refresh` | Refresh Token | - | 刷新 |
| GET | `/classes` | ✅ | - | 班级列表 |
| POST | `/classes` | ✅ | admin | 新增班级 |
| GET | `/classes/:id` | ✅ | - | 班级详情 |
| PUT | `/classes/:id` | ✅ | admin | 修改班级 |
| DELETE | `/classes/:id` | ✅ | admin | 删除班级 |
| GET | `/courses` | ✅ | - | 课程列表 |
| POST | `/courses` | ✅ | admin | 新增课程 |
| GET | `/courses/:id` | ✅ | - | 课程详情 |
| PUT | `/courses/:id` | ✅ | admin | 修改课程 |
| DELETE | `/courses/:id` | ✅ | admin | 删除课程 |
| GET | `/students` | ✅ | - | 学生列表 |
| POST | `/students` | ✅ | admin | 新增学生 |
| GET | `/students/:id` | ✅ | - | 学生详情 |
| PUT | `/students/:id` | ✅ | admin | 修改学生 |
| DELETE | `/students/:id` | ✅ | admin | 删除学生 |
| POST | `/face/register` | ✅ | - | 注册人脸 |
| POST | `/face/recognize` | ❌ | - | 人脸打卡 |
| GET | `/face/students` | ✅ | - | 已注册人脸列表 |
| GET | `/attendance` | ✅ | - | 考勤记录 |
| GET | `/attendance/statistics` | ✅ | - | 考勤统计 |
