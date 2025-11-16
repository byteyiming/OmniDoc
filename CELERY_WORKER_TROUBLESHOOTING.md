# Celery Worker 故障排查指南

## 问题：文档没有生成，但在 Railway 上看不到日志

### 🔍 检查清单

#### 1. **确认 Celery Worker 服务正在运行**

在 Railway 上：
1. 打开你的项目
2. 检查是否有 **两个服务**：
   - `omnidoc-backend` (API 服务器)
   - `omnidoc-celery-worker` (Celery Worker)
3. 如果没有 `omnidoc-celery-worker` 服务，需要创建它（见下方）

#### 2. **检查 Celery Worker 日志**

在 Railway 上：
1. 点击 `omnidoc-celery-worker` 服务
2. 打开 **"Deploy Logs"** 标签
3. 你应该看到：
   ```
   celery@xxx v5.x.x
   
   [2025-11-16 00:00:00,000: INFO/MainProcess] Connected to redis://...
   [2025-11-16 00:00:00,000: INFO/MainProcess] celery@xxx ready.
   ```

如果看到错误或连接失败，说明：
- ❌ Celery Worker 没有启动
- ❌ Redis 连接配置错误
- ❌ 环境变量缺失

#### 3. **检查任务是否被提交到队列**

在 Railway 上，查看 `omnidoc-backend` 服务的日志：
1. 点击 `omnidoc-backend` 服务
2. 打开 **"Deploy Logs"** 标签
3. 查找：
   ```
   Submitted generation task <task-id> for project <project-id>
   ```

如果看到这个日志，说明任务已提交到队列。

#### 4. **检查 Celery Worker 是否处理任务**

在 `omnidoc-celery-worker` 的日志中，你应该看到：
```
[CELERY TASK] Starting document generation for project <project-id>
[CELERY TASK] Selected documents: [...]
[DOCUMENT GENERATION] Starting <document-id> (1/7) for project <project-id>
```

如果**没有**看到这些日志，说明：
- ❌ Celery Worker 没有连接到正确的 Redis
- ❌ 任务在队列中但没有被 worker 处理
- ❌ Celery Worker 配置错误

---

## 🔧 解决方案

### 问题 1：没有 Celery Worker 服务

**创建 Celery Worker 服务：**

1. 在 Railway 项目中，点击 **"+ New"** → **"GitHub Repo"**
2. 选择相同的仓库（和 backend 一样的仓库）
3. 配置服务：
   - **Name**: `omnidoc-celery-worker`
   - **Root Directory**: `/` (仓库根目录)
   - **Dockerfile Path**: `Dockerfile` (自动检测)

4. **设置 Custom Start Command**：
   - 进入 **Settings** → **Deploy**
   - 滚动到 **"Custom Start Command"**
   - 点击 **"+ Start Command"**
   - 输入：
     ```
     celery -A src.tasks.celery_app worker --loglevel=info --concurrency=1
     ```

5. **配置环境变量**：
   - 进入 **Variables** 标签
   - 添加**所有** backend 服务需要的环境变量（特别是）：
     - `DATABASE_URL`
     - `REDIS_URL` (必须正确配置！)
     - `GEMINI_API_KEY`
     - `LLM_PROVIDER`
     - `LOG_LEVEL=INFO`
     - `LOG_FORMAT=json`

6. **部署**：
   - 点击 **"Deploy"**
   - 等待部署完成

### 问题 2：Celery Worker 连接 Redis 失败

**检查 Redis 配置：**

1. 确认 `REDIS_URL` 环境变量已设置（在 `omnidoc-celery-worker` 服务的 Variables 中）
2. 确认 `REDIS_URL` 使用 `rediss://` 协议（如果使用 Upstash）
3. 在 Celery Worker 日志中查找连接错误：
   ```
   Redis connection failed: ...
   ```
4. 确认 Redis URL 格式正确：
   ```
   rediss://default:<password>@<host>:6379?ssl_cert_reqs=none
   ```

### 问题 3：任务在队列中但没有被处理

**检查 Celery Worker 状态：**

1. 在 Railway 上，进入 `omnidoc-celery-worker` 服务的 **Shell**（如果有）
2. 运行：
   ```bash
   celery -A src.tasks.celery_app inspect active
   ```
3. 如果看到任务列表，说明任务在队列中
4. 如果列表为空，说明任务没有提交到队列

**检查 Celery Worker 是否在处理：**

在 Celery Worker 日志中，你应该看到：
```
[2025-11-16 00:00:00,000: INFO/MainProcess] Task omnidoc.generate_documents[<task-id>] received
[CELERY TASK] Starting document generation for project <project-id>
```

如果没有这些日志，说明：
- Worker 没有连接到 Redis broker
- 任务被发送到错误的队列
- Worker 配置错误

### 问题 4：日志看不到

**确保日志输出到 stdout/stderr：**

✅ 已修复（在最新代码中）：
- 所有日志现在都输出到 `sys.stdout` 和 `sys.stderr`
- Railway 会自动捕获这些日志
- 使用 `print()` 语句确保日志可见性

**查看日志：**

1. 在 Railway 上，打开 `omnidoc-celery-worker` 服务
2. 查看 **"Deploy Logs"** 标签
3. 你应该看到：
   ```
   [CELERY TASK] Starting document generation for project <project-id>
   [DOCUMENT GENERATION] Starting <document-id> (1/7) for project <project-id>
   [DOCUMENT GENERATION] ✅ Completed <document-id> (1/7) in X.XXs (XXXX chars) for project <project-id>
   ```

---

## 📊 诊断步骤

### 步骤 1：检查服务状态

```bash
# 在 Railway 上检查
1. Backend 服务：应该显示 "Deployed"
2. Celery Worker 服务：应该显示 "Deployed"
```

### 步骤 2：检查日志

```bash
# Backend 日志应该显示：
Submitted generation task <task-id> for project <project-id>

# Celery Worker 日志应该显示：
[CELERY TASK] Starting document generation for project <project-id>
[DOCUMENT GENERATION] Starting <document-id> (1/7) for project <project-id>
```

### 步骤 3：检查任务状态

如果可能，在 Railway Shell 中运行：
```bash
celery -A src.tasks.celery_app inspect active
celery -A src.tasks.celery_app inspect registered
```

---

## 🚨 常见错误

### 错误 1：`Failed to submit task to background queue`

**原因**：Redis 不可用或 Celery Worker 未运行

**解决**：
1. 检查 `REDIS_URL` 是否正确
2. 确认 Redis 服务正在运行（Upstash）
3. 确认 Celery Worker 服务已部署

### 错误 2：`Task received but not processed`

**原因**：Celery Worker 没有连接到正确的 Redis

**解决**：
1. 确认 Backend 和 Celery Worker 使用**相同的** `REDIS_URL`
2. 检查 Redis 连接字符串格式
3. 重启 Celery Worker 服务

### 错误 3：`No handlers found for logger`

**原因**：日志配置问题

**解决**：
✅ 已修复 - 最新代码强制日志输出到 stdout/stderr

---

## ✅ 验证清单

完成任务后，确认以下所有项：

- [ ] Celery Worker 服务存在并在运行
- [ ] Celery Worker 日志显示 "Connected to redis://..."
- [ ] Celery Worker 日志显示 "celery@xxx ready"
- [ ] 提交任务后，Backend 日志显示 "Submitted generation task..."
- [ ] Celery Worker 日志显示 "[CELERY TASK] Starting..."
- [ ] Celery Worker 日志显示 "[DOCUMENT GENERATION] Starting..."
- [ ] Celery Worker 日志显示 "[DOCUMENT GENERATION] ✅ Completed..."
- [ ] 前端显示文档生成进度

---

## 📞 如果问题仍然存在

1. **收集日志**：
   - Backend 服务的完整日志
   - Celery Worker 服务的完整日志
   - 错误消息和时间戳

2. **检查配置**：
   - 所有环境变量是否正确设置
   - Redis URL 是否正确
   - Celery Worker 的 Custom Start Command 是否正确

3. **测试 Redis 连接**：
   - 在 Railway Shell 中测试 Redis 连接
   - 确认 Redis 服务可访问

