# 智能教育平台（Education Platform）

面向“管理端 + Pad 端（老师/学生）+ AI 服务”的一体化教育系统。

## 项目概览

本项目由三个核心子系统组成，职责严格分离：

- `frontend`：前端界面（主控端 + Pad 端入口与页面）
- `backend`：Spring Boot 业务后端（用户/权限/作业/考试/成绩/任务）
- `ai_service`：FastAPI AI 服务（RAG 检索问答、成绩预测、AI 批改）

### 角色与端能力

- 管理者（主控端）
  - 查看全局成绩
  - 创建老师任务与学生作业
  - 进入 Pad 业务入口
- 老师（Pad 端）
  - 发布作业/考试、批改、查看班级成绩
  - 使用 AI 能力（RAG、成绩预测、AI 批改）
- 学生（Pad 端）
  - 查看并提交作业、查看考试成绩
  - 使用 AI 能力（RAG、成绩预测）

## 目录结构

```text
.
├── frontend/                      # Vue3 前端
│   ├── src/views/education/       # 教师/学生 Pad 页面
│   ├── src/api/education/         # 教育模块 API
│   └── src/router/education/      # 教育模块路由
├── backend/                       # Spring Boot（若依 + 业务模块）
│   ├── ruoyi-admin/               # 启动模块
│   └── zhiyu/                     # 教育业务模块
├── ai_service/                    # FastAPI AI 服务
│   ├── main.py
│   ├── rag_service.py
│   ├── prediction_service.py
│   ├── database.py
│   └── config.py
└── deploy/sql/                    # SQL 脚本
```

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Pinia、Axios
- 后端：Spring Boot 2.5.x、MyBatis、Redis、MySQL
- AI 服务：FastAPI、Pandas、Qdrant、DashScope、TensorFlow、scikit-learn
- Python 环境管理：`uv`

## 安装与启动

### 1. 环境要求

- JDK 8+
- Maven 3.6+
- Node.js 18+
- Python 3.11+（建议）
- MySQL 5.7+/8.0+
- Redis

### 2. 数据库初始化

1. 创建数据库：`ry-vue`
2. 导入脚本：

```bash
mysql -uroot -p ry-vue < backend/sql/ry_20250522.sql
mysql -uroot -p ry-vue < deploy/sql/schema.sql
mysql -uroot -p ry-vue < deploy/sql/seed.sql
```

### 3. 启动后端（8080）

```bash
cd backend
mvn clean install -DskipTests
cd ruoyi-admin
mvn spring-boot:run
```

### 4. 启动 AI 服务（8000）

```bash
cd ai_service
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端（默认 80 或 Vite 默认端口）

```bash
cd frontend
npm install
npm run dev
```

## 使用示例

### 1. Pad 端登录/注册

- 路由：`/education/auth`
- 登录后进入：`/education/pad`

### 2. 成绩管理接口（后端）

```http
GET    /student/performance/list
GET    /student/performance/{id}
POST   /student/performance
PUT    /student/performance
DELETE /student/performance/{id}
```

### 3. RAG 接口（AI 服务）

```http
POST /upload-excel
GET  /query?question=如何提高数学成绩
GET  /rag-api/datasets
GET  /rag-api/datasets/{dataset_id}
DELETE /rag-api/datasets/{dataset_id}
```

### 4. 成绩预测接口（AI 服务）

```http
POST /train-prediction-model
POST /predict-score
GET  /model-info
```

## 配置说明

### 前端

- 环境变量：`frontend/.env.development`
- 代理：`frontend/vite.config.js`

### 后端

- 主配置：`backend/ruoyi-admin/src/main/resources/application.yml`
- 数据源：`backend/ruoyi-admin/src/main/resources/application-druid.yml`

### AI 服务

优先使用环境变量；未设置时会读取 `ai_service/.env`。

推荐配置：

```bash
# DashScope
DASHSCOPE_API_KEY=your_api_key

# 数据库（二选一）
EDU_DATABASE_URL=mysql+pymysql://user:password@host:3306/ry-vue
# 或分项配置
EDU_DB_HOST=localhost
EDU_DB_PORT=3306
EDU_DB_NAME=ry-vue
EDU_DB_USER=root
EDU_DB_PASSWORD=your_password
```

## 代码规范约定

- 已启用根目录 `.editorconfig` 统一缩进与换行规范。
- 前端接口统一放在 `frontend/src/api`，页面禁止散写请求地址。
- 教师/学生页面统一维护在 `frontend/src/views/education`。
- 路由统一维护在 `frontend/src/router` 与 `frontend/src/router/education`。
- AI 推理逻辑仅在 `ai_service`，业务流程与权限逻辑仅在 `backend`。

## 贡献指南

1. Fork 并创建分支（建议命名：`feature/<name>`、`fix/<name>`）
2. 按模块提交：前端/后端/AI 服务改动分开
3. 提交前自检：
   - 前端：`npm run dev` 可启动
   - 后端：`mvn -q -DskipTests package` 通过
   - AI 服务：`uv run uvicorn main:app --reload` 可启动
4. 提交 PR，说明改动范围、影响角色（管理者/老师/学生）、验证步骤

## 故障排查

### 1. AI 服务无法访问大模型

- 检查 `DASHSCOPE_API_KEY` 是否配置
- 检查 `ai_service/.env` 是否生效
- 访问 `GET /llm-status` 查看在线模型状态

### 2. AI 服务数据库连接失败

- 优先检查 `EDU_DATABASE_URL` 是否正确
- 或检查 `EDU_DB_HOST/PORT/NAME/USER/PASSWORD`
- 确认 MySQL 已启动且库名存在

### 3. 前端调用接口 401/403

- 确认当前登录角色与目标页面权限匹配
- 清理本地 token 后重新登录

### 4. 上传文件失败

- RAG 仅支持：`.xlsx/.xls/.txt`
- 预测训练仅支持：`.csv`
- AI 批改图片仅支持常见图片格式（png/jpg/jpeg/webp/bmp/gif）

## License

本项目遵循仓库中既有开源协议与版权声明。
