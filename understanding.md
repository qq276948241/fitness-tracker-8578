# 健身打卡项目 - 整体架构说明

## 一、项目概览

一个前后端分离的健身打卡 Web 应用，帮助用户记录训练打卡、追踪体重变化、查看数据统计、选择训练计划。

```
健身打卡
├── 后端 (FastAPI + SQLite) - 端口 8000
└── 前端 (Vue 3 + Vite)       - 端口 5173
```

---

## 二、技术栈

### 后端技术栈
| 技术 | 用途 | 版本 |
|------|------|------|
| Python | 开发语言 | 3.x |
| FastAPI | Web 框架 | 0.100+ |
| SQLAlchemy | ORM | 2.0+ |
| SQLite | 数据库 | 内置 |
| Pydantic | 数据校验 | 2.0+ |
| python-jose | JWT 认证 | - |
| passlib + bcrypt | 密码哈希 | - |
| uvicorn | ASGI 服务器 | - |

### 前端技术栈
| 技术 | 用途 | 版本 |
|------|------|------|
| Vue 3 | 前端框架 | 3.3+ (Composition API) |
| Vite | 构建工具 | 5.0+ |
| Pinia | 状态管理 | 2.0+ |
| Vue Router | 路由 | 4.0+ |
| Element Plus | UI 组件库 | 2.4+ (中文语言包) |
| ECharts | 数据可视化 | 5.4+ |
| Axios | HTTP 请求库 | - |
| dayjs | 日期处理 | - |

---

## 三、后端架构

### 3.1 目录结构
```
backend/
├── requirements.txt    # 依赖清单
├── database.py         # 数据库连接配置
├── models.py           # SQLAlchemy 数据模型
├── schemas.py          # Pydantic 数据校验 schema
├── auth.py             # JWT 认证与密码哈希
└── main.py             # 应用入口 + 所有 API 路由
```

### 3.2 模块详解

#### database.py - 数据库连接
- 定义 SQLite 数据库 URL: `sqlite:///./fitness.db`
- 创建 `engine`、`SessionLocal` 会话工厂
- `get_db()` 依赖注入函数，为每个请求提供独立的数据库会话
- 使用 `Base` 作为所有模型的基类

#### models.py - 数据模型
定义 4 个核心数据表模型：

| 模型 | 表名 | 核心字段 | 说明 |
|------|------|---------|------|
| User | users | id, username, email, full_name, height, target_weight, hashed_password, created_at | 用户信息 |
| WorkoutRecord | workout_records | id, user_id, date, workout_type, duration, calories, notes, exercises, created_at | 训练打卡记录 |
| WeightRecord | weight_records | id, user_id, date, weight, body_fat, notes, created_at | 体重记录 |
| WorkoutPlan | workout_plans | id, user_id, name, description, plan_data, is_template, created_at | 训练计划 |

#### schemas.py - 数据校验
定义请求和响应的 Pydantic schema：
- `UserCreate` / `UserLogin` / `UserBase` / `UserResponse` - 用户相关
- `WorkoutRecordCreate` / `WorkoutRecordUpdate` / `WorkoutRecordResponse` - 训练记录
- `WeightRecordCreate` / `WeightRecordUpdate` / `WeightRecordResponse` - 体重记录
- `WorkoutPlanCreate` / `WorkoutPlanResponse` - 训练计划
- `Token` - 登录响应（含 access_token 和 user）
- `StatsResponse` - 统计数据响应（含 weight_to_target、calendar_data 等）

#### auth.py - 认证模块
- `get_password_hash()`: 使用 bcrypt 哈希密码
- `verify_password()`: 验证密码
- `create_access_token()`: 创建 JWT token（默认 30 分钟过期）
- `get_current_user()`: 从请求 Header 解析 token，获取当前用户（API 依赖）
- `SECRET_KEY` + `ALGORITHM`(HS256) + `ACCESS_TOKEN_EXPIRE_MINUTES`(30)

#### main.py - API 路由
应用启动时：
1. `Base.metadata.create_all(bind=engine)` - 自动建表
2. `init_template_plans(db)` - 初始化 5 个内置训练计划模板（不存在时）
3. 启用 CORS 中间件（允许所有来源）

API 列表（统一前缀 `/api`）：

**认证接口** (`/auth`)
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/register` | 用户注册 | 否 |
| POST | `/login` | 用户登录 | 否 |
| GET | `/me` | 获取当前用户信息 | 是 |
| PUT | `/profile` | 更新个人信息（含目标体重） | 是 |

**训练记录接口** (`/workouts`)
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/` | 获取训练记录列表（支持日期、类型筛选） | 是 |
| POST | `/` | 创建训练记录 | 是 |
| GET | `/{id}` | 获取单条记录详情 | 是 |
| PUT | `/{id}` | 更新训练记录 | 是 |
| DELETE | `/{id}` | 删除训练记录 | 是 |

**体重记录接口** (`/weight`)
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/` | 获取体重记录列表（支持日期筛选） | 是 |
| POST | `/` | 创建体重记录 | 是 |
| PUT | `/{id}` | 更新体重记录 | 是 |
| DELETE | `/{id}` | 删除体重记录 | 是 |

**训练计划接口** (`/plans`)
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/` | 获取训练计划（含内置模板） | 是 |
| POST | `/` | 创建自定义训练计划 | 是 |

**统计和日历接口**
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/stats` | 获取完整统计数据 | 是 |
| GET | `/calendar` | 获取指定年月的日历打卡数据 | 是 |
| GET | `/health` | 健康检查 | 否 |

**核心工具函数**
- `build_calendar_data(workouts, weights, year, month)`: 组装指定月份的日历数据，按天聚合训练和体重记录

### 3.3 后端数据流
```
HTTP 请求 → 路由处理器 → get_current_user (JWT 校验) → get_db (获取会话)
                                                         ↓
                                          业务逻辑 (查询/创建/更新/删除)
                                                         ↓
                                          db.commit() / db.refresh()
                                                         ↓
                                          Pydantic schema 校验 + 序列化
                                                         ↓
                                                JSON 响应
```

---

## 四、前端架构

### 4.1 目录结构
```
frontend/src/
├── api/                    # API 请求封装
│   ├── auth.js             # 认证相关接口
│   ├── stats.js            # 统计 + 日历接口
│   ├── weight.js           # 体重记录接口
│   └── workout.js          # 训练记录接口
├── components/             # 可复用组件
│   ├── BaseChart.vue       # 通用 ECharts 图表组件
│   └── CalendarView.vue    # 日历打卡视图组件
├── router/
│   └── index.js            # 路由配置 + 导航守卫
├── stores/                 # Pinia 状态管理
│   ├── user.js             # 用户状态（token、用户信息）
│   └── stats.js            # 统计数据状态（含缓存）
├── utils/                  # 工具函数
│   ├── chartOptions.js     # ECharts 配置工厂
│   ├── constants.js        # 常量（训练类型、颜色映射）
│   └── request.js          # Axios 实例 + 拦截器
├── views/                  # 页面组件
│   ├── Login.vue           # 登录页
│   ├── Register.vue        # 注册页
│   ├── Home.vue            # 首页（今日打卡）
│   ├── History.vue         # 历史记录页（列表+日历）
│   ├── Stats.vue           # 数据统计页
│   ├── Plans.vue           # 训练计划页
│   └── Settings.vue        # 个人设置页
├── App.vue                 # 根组件（布局+导航）
├── main.js                 # 应用入口
└── style.css               # 全局样式
```

### 4.2 核心模块详解

#### request.js - HTTP 客户端
- 基于 Axios 创建实例，`baseURL: 'http://localhost:8000/api'`
- **请求拦截器**：自动注入 Authorization Header (`Bearer ${token}`)
- **响应拦截器**：
  - 自动提取 `response.data`
  - 401 时自动登出并跳转登录页
  - 统一错误提示（ElMessage）

#### API 层
每个领域对应一个 API 文件，封装对应的 HTTP 请求：
- [auth.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/api/auth.js): `login()`, `register()`, `getProfile()`, `updateProfile()`
- [workout.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/api/workout.js): `getWorkouts()`, `createWorkout()`, `updateWorkout()`, `deleteWorkout()`
- [weight.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/api/weight.js): `getWeightRecords()`, `createWeightRecord()`, `updateWeightRecord()`, `deleteWeightRecord()`
- [stats.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/api/stats.js): `getStats()`, `getCalendarData(year, month)`

#### stores/user.js - 用户状态管理
**State**：
- `token`: JWT token（localStorage 持久化）
- `user`: 用户信息对象（localStorage 持久化）

**Getters**：
- `isLoggedIn`: 是否已登录

**Actions**：
- `login(username, password)`: 登录，调用 API 后存储 token 和 user
- `register(userData)`: 注册
- `logout()`: 清空本地状态 + 清空 stats store
- `checkAuth()`: 页面加载时校验 token 有效性
- `updateUser(userData)`: 更新用户信息

#### stores/stats.js - 统计数据状态管理
**State**：
- `stats`: 统计数据对象（总训练次数、总时长、体重历史等）
- `calendarMap`: 日历数据缓存，key 为 `YYYY-MM` 格式
- `loading`: 加载状态

**核心逻辑**：
```javascript
// 按月缓存日历数据，同月份不重复请求
const loadCalendarData = async (year, month, force = false) => {
  const key = `${year}-${String(month).padStart(2, '0')}`
  if (calendarMap.value[key] && !force) {
    return calendarMap.value[key]
  }
  const data = await getCalendarData(year, month)
  calendarMap.value[key] = data
  return data
}
```

**Computed**：
- `targetAchieved`: 是否已达成目标体重
- `targetPercentage`: 目标进度百分比（0-100）
- `targetColor`: 进度条颜色（根据进度变化）

**Actions**：
- `loadStats(force)`: 加载统计数据（有缓存时直接返回）
- `refreshStats()`: 强制刷新统计数据
- `loadCalendarData(year, month, force)`: 加载指定月份日历数据
- `refreshCalendar(year, month)`: 强制刷新指定月份日历
- `$reset()`: 清空所有状态（登出时调用）

#### router/index.js - 路由
**路由表**：
| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | Login.vue | 未登录用户 |
| `/register` | Register.vue | 未登录用户 |
| `/` | Home.vue | 已登录 |
| `/history` | History.vue | 已登录 |
| `/stats` | Stats.vue | 已登录 |
| `/plans` | Plans.vue | 已登录 |
| `/settings` | Settings.vue | 已登录 |

**导航守卫** (`beforeEach`)：
- 访问需要认证的页面但未登录 → 跳转 `/login`
- 已登录用户访问登录/注册页 → 跳转 `/`
- 其他情况正常放行

#### components/BaseChart.vue - 通用图表组件
**Props**：
- `option`: ECharts 配置对象
- `height`: 图表高度（默认 300px）

**功能**：
- 自动初始化 ECharts 实例
- 监听 option 变化自动更新（`setOption` + `resize`）
- 监听窗口 resize 自动调整
- 组件销毁时自动 dispose
- `defineExpose({ resize })`

#### components/CalendarView.vue - 日历打卡组件
**Props**（支持 `v-model:year` / `v-model:month`）：
- `year`, `month`: 当前显示年月
- `days`: 日历数据数组
- `summary`: 月度汇总（打卡天数、总时长、总消耗）
- `loading`: 加载状态

**Events**：
- `update:year` / `update:month`: 双向绑定更新
- `change`: 月份切换时触发，参数 `{ year, month }`
- `day-click`: 点击某一天时触发，参数 cell 对象

**功能**：
- 上/下月切换、回到今天
- 日历格子展示（打卡状态、训练类型 tag、时长、消耗、体重）
- 月度汇总展示
- 图例说明

#### utils/constants.js - 常量
- `WORKOUT_TYPES`: 训练类型列表（力量训练、有氧训练、HIIT、瑜伽等 8 种）
- `WORKOUT_TYPE_COLORS`: 训练类型到 Element Plus tag 颜色的映射
- `getWorkoutTypeColor(type)`: 获取训练类型对应的颜色

#### utils/chartOptions.js - 图表配置工厂
4 个工厂函数，接收数据返回 ECharts option 对象：
- `getWeeklyWorkoutOption(weeklyData)`: 本周训练柱状图（时长）
- `getWeightTrendOption(weightHistory)`: 体重变化趋势折线图
- `getWorkoutTypePieOption(workoutTypes)`: 训练类型分布饼图
- `getWeeklyStatsOption(weeklyData)`: 近 7 天柱+折线组合图（时长+卡路里）

### 4.3 页面组件详解

#### App.vue - 根组件
- 整体布局：左侧导航菜单 + 右侧内容区
- 导航菜单：今日打卡、历史记录、数据统计、训练计划、个人设置
- 顶部欢迎信息 + 退出登录按钮
- `onMounted` 时调用 `userStore.checkAuth()` 校验登录状态

#### Home.vue - 首页今日打卡
- **数据卡片**：累计训练次数、累计时长、消耗卡路里、当前体重
- **记录训练**：今日训练记录列表 + 添加打卡弹窗
- **记录体重**：最新体重展示 + 记录体重弹窗
- **目标进度**：当前→目标体重、进度条、还差多少 kg
- **本周训练**：柱状图展示近 7 天训练时长
- 新增/删除记录后：`loadData()` + `statsStore.refreshStats()` + `refreshCalendar()`

#### History.vue - 历史记录
两个 Tab：
- **训练记录**：支持列表/日历视图切换
  - 列表：日期范围筛选、训练类型筛选、编辑/删除
  - 日历：`CalendarView` 组件，按月展示打卡情况
- **体重记录**：列表展示，日期范围筛选、编辑/删除

编辑/删除后自动刷新：列表数据 + stats store + calendar 缓存

#### Stats.vue - 数据统计
- **数据卡片**：累计训练次数、累计时长、消耗卡路里、平均每次时长
- **训练类型分布**：饼图（`BaseChart` + `getWorkoutTypePieOption`）
- **体重变化趋势**：折线图（`BaseChart` + `getWeightTrendOption`）
- **近 7 天训练时长**：柱+折线组合图（`BaseChart` + `getWeeklyStatsOption`）
- 进入页面强制刷新：`statsStore.refreshStats()`

#### Plans.vue - 训练计划
- 展示 5 个内置训练计划模板 + 用户自定义计划
- 卡片形式展示：计划名称、描述、频率、时长、难度等级
- 支持创建自定义训练计划

#### Settings.vue - 个人设置
- **基本信息**：用户名（只读）、昵称、邮箱、身高、目标体重
- **修改密码**：原密码 + 新密码 + 确认密码
- **我的数据**：展示统计数据（从 stats store 获取）
- 保存后：`userStore.updateUser()` + `statsStore.refreshStats()`

### 4.4 前端数据流

**整体数据流**：
```
用户操作 → View 组件调用 API → API 层封装 HTTP 请求
    ↓
request.js 拦截器自动加 token → 后端 API
    ↓
后端返回 JSON → request.js 拦截器处理响应
    ↓
View 组件更新 store → store 响应式更新 → 所有相关 View 自动更新
```

**状态管理数据流**：
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   API 层    │──────→│  Pinia Store│──────→│   View 层   │
│ (auth.js)   │       │  user.js    │       │ (各页面)    │
│ (stats.js)  │       └─────────────┘       └─────────────┘
│ (workout.js)│              ↑                       │
│ (weight.js) │       ┌─────────────┐                │
│             │──────→│  Pinia Store│                ↓
└─────────────┘       │  stats.js   │       响应式自动更新
                      └─────────────┘
```

**组件依赖关系**：
```
main.js → App.vue → 路由 → 各页面组件
                      ↓
                ┌─────┴─────┐
                │           │
          stores/user   stores/stats
                │           │
                └─────┬─────┘
                      ↓
              api/* (request.js)

页面组件依赖关系：
Home.vue     ──→ BaseChart, stats store, user store
History.vue  ──→ CalendarView, BaseChart, stats store
Stats.vue    ──→ BaseChart, stats store
Settings.vue ──→ stats store, user store
Plans.vue    ──→ (无组件依赖，自有逻辑)
```

---

## 五、完整数据流示例

### 示例 1：用户添加训练打卡
```
1. 用户在 Home.vue 点击"添加打卡" → 打开弹窗
2. 填写表单 → 点击"保存"
3. Home.vue 调用 submitWorkout()
   ├─ 防重检查：if (submitting.value) return
   ├─ 设置 submitting = true
   ├─ 调用 createWorkout(workoutForm.value) → API 层
   │   └─ request.js 自动加 token → POST /api/workouts
   ├─ 后端创建记录 → 返回新记录
   ├─ ElMessage.success('打卡成功！')
   ├─ 关闭弹窗、重置表单
   ├─ 刷新数据：
   │   ├─ loadData() → 重新加载今日训练和最新体重
   │   ├─ statsStore.refreshStats() → 刷新统计数据
   │   └─ statsStore.refreshCalendar(year, month) → 刷新当月日历
   └─ 设置 submitting = false

4. 所有页面自动更新：
   ├─ Home.vue：今日训练列表、统计卡片、本周训练图表 自动更新
   ├─ History.vue：日历视图中当天格子显示打卡
   └─ Stats.vue：下次进入时获取最新数据
```

### 示例 2：日历切换月份
```
1. 用户在 History.vue 日历视图点击"上月"按钮
2. CalendarView 组件 prevMonth() 触发
   ├─ 更新 innerYear / innerMonth
   └─ emit('change', { year, month })

3. History.vue handleCalendarChange() 响应
   ├─ 更新 calendarYear / calendarMonth
   └─ 调用 loadCalendar()
      └─ statsStore.loadCalendarData(year, month)
         ├─ 检查 calendarMap 中是否有该月缓存
         ├─ 无缓存 → 调用 getCalendarData(year, month) → API 层
         ├─ 存入 calendarMap
         └─ 返回数据

4. History.vue 自动更新：
   ├─ calendarDays / calendarSummary 是 computed，直接从 store 派生
   └─ 所以 store 更新时，日历视图自动刷新
```

### 示例 3：修改目标体重
```
1. 用户在 Settings.vue 修改目标体重 → 点击"保存修改"
2. 调用 updateProfile() → API 层 → PUT /api/auth/profile
3. 后端更新 user.target_weight 字段 → 返回更新后的用户信息
4. Settings.vue：
   ├─ userStore.updateUser(res) → 更新本地用户信息
   └─ statsStore.refreshStats() → 刷新统计数据

5. 自动更新：
   ├─ Home.vue：目标进度条、进度百分比、还差多少 kg 自动更新
   └─ Settings.vue：右侧"我的数据"中的目标体重自动更新
```

---

## 六、部署与运行

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py          # 或 uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 访问: http://localhost:8000/docs (Swagger 文档)
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
# 访问: http://localhost:5173
```

### 数据库
- SQLite 数据库文件：`backend/fitness.db`
- 首次启动自动创建表和 5 个训练计划模板
- 删除 `fitness.db` 后重启后端即可重置数据库

---

## 七、关键设计决策

### 1. 前后端分离 + CORS
- 前端直接访问 `http://localhost:8000/api`，不走 Vite 代理
- 后端开启 CORS 允许所有来源，便于本地开发

### 2. 状态管理分层
- `userStore`: 管理用户身份、token、个人信息
- `statsStore`: 管理业务数据（统计、日历），带缓存机制
- 避免了每个页面各自调接口、各自存数据导致的数据不一致

### 3. 组件化抽离
- `BaseChart`: 所有图表复用，统一处理 ECharts 生命周期
- `CalendarView`: 日历逻辑集中管理，便于维护和复用
- `chartOptions.js`: 图表配置集中管理，改样式只改一处

### 4. 缓存策略
- 统计数据：首次加载后缓存，新增/修改/删除时强制刷新
- 日历数据：按月缓存（key 为 `YYYY-MM`），同月份切换不重复请求
- 编辑/删除记录时：刷新相关月份的日历缓存 + 刷新统计数据

### 5. 防重机制
- 提交按钮 loading 状态
- 函数开头 `if (submitting.value) return` 双重保险
- 确保快速点击不会重复提交

---

## 八、文件索引速查表

| 功能 | 文件路径 |
|------|---------|
| 数据库连接 | [backend/database.py](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/backend/database.py) |
| 数据模型 | [backend/models.py](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/backend/models.py) |
| 认证逻辑 | [backend/auth.py](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/backend/auth.py) |
| API 路由 | [backend/main.py](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/backend/main.py) |
| HTTP 客户端 | [frontend/src/utils/request.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/utils/request.js) |
| 用户状态 | [frontend/src/stores/user.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/stores/user.js) |
| 统计状态 | [frontend/src/stores/stats.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/stores/stats.js) |
| 路由配置 | [frontend/src/router/index.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/router/index.js) |
| 图表组件 | [frontend/src/components/BaseChart.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/components/BaseChart.vue) |
| 日历组件 | [frontend/src/components/CalendarView.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/components/CalendarView.vue) |
| 图表配置 | [frontend/src/utils/chartOptions.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/utils/chartOptions.js) |
| 常量定义 | [frontend/src/utils/constants.js](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/utils/constants.js) |
| 首页 | [frontend/src/views/Home.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/views/Home.vue) |
| 历史记录 | [frontend/src/views/History.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/views/History.vue) |
| 数据统计 | [frontend/src/views/Stats.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/views/Stats.vue) |
| 个人设置 | [frontend/src/views/Settings.vue](file:///d:/code/ai-prompt/solo-20/repos/repo44/project44/frontend/src/views/Settings.vue) |
