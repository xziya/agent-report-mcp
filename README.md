# Agent Report MCP

一个 MCP (Model Context Protocol) 工具，用于自动总结 AI Agent 的工作内容、生成汇报文档。

## 功能特性

- 📊 **工作追踪**: 自动记录工作会话、任务和代码变更
- ⏱️ **时间统计**: 精确计算工作时长和任务耗时
- 📝 **代码统计**: 统计代码行数、文件变更数量
- 🤝 **人机协作记录**: 记录人工指导、决策和反馈
- 📄 **汇报生成**: 生成适合向领导汇报的 Markdown 文档
- 🌐 **多语言支持**: 支持中文和英文报告
- 🔄 **自动追踪**: 监听文件系统和 Git，自动记录代码变更
- 🎯 **CLI 工具**: 提供命令行工具，方便快速使用
- 🌍 **远程部署**: 支持 SSE 远程服务器模式

## 安装

```bash
npm install -g agent-report-mcp
```

或者本地开发：

```bash
git clone <repository>
cd agent-report-mcp
npm install
npm run build
```

## 配置

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "agent-report": {
      "command": "node",
      "args": ["/path/to/agent-report-mcp/dist/index.js"]
    }
  }
}
```

配置文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

### Claude CLI 配置 (Linux)

在 Linux 环境中使用 Claude CLI，需要创建或编辑配置文件：

```bash
# 创建配置目录（如果不存在）
mkdir -p ~/.config/claude

# 创建或编辑配置文件
nano ~/.config/claude/config.json
```

在配置文件中添加：

```json
{
  "mcpServers": {
    "agent-report": {
      "command": "node",
      "args": ["/path/to/agent-report-mcp/dist/index.js"]
    }
  }
}
```

**注意**: 请将 `/path/to/agent-report-mcp/dist/index.js` 替换为实际的绝对路径。可以使用 `pwd` 命令获取当前目录路径：

```bash
# 在 agent-report-mcp 目录下执行
pwd
```

**验证配置**:

```bash
# 检查配置文件是否正确
cat ~/.config/claude/config.json

# 测试 MCP 服务器是否正常运行
node /path/to/agent-report-mcp/dist/index.js
```

### OpenCode CLI 配置

在 OpenCode 配置文件中添加 MCP 服务器配置。

### 远程服务器模式 (SSE)

除了本地运行，你还可以部署为远程 MCP 服务器，通过 URL 直接使用，无需本地克隆。

#### 启动远程服务器

```bash
# 方式1：使用 npm 脚本
npm run server

# 方式2：先构建再启动
npm run build
npm run start:server

# 方式3：使用环境变量指定端口
PORT=8080 npm run start:server
```

服务器启动后，会提供以下端点：
- `GET /` - 服务器信息
- `GET /health` - 健康检查
- `GET /sse` - SSE 连接端点
- `POST /message` - 消息处理端点

#### 客户端配置 (远程模式)

**Claude Desktop 配置远程服务器:**

```json
{
  "mcpServers": {
    "agent-report-remote": {
      "url": "http://your-server-address:3000/sse"
    }
  }
}
```

**Claude CLI 配置远程服务器:**

```json
{
  "mcpServers": {
    "agent-report-remote": {
      "url": "http://your-server-address:3000/sse"
    }
  }
}
```

**OpenCode 配置远程服务器:**

在 OpenCode 配置文件中添加：

```json
{
  "mcpServers": {
    "agent-report-remote": {
      "url": "http://your-server-address:3000/sse"
    }
  }
}
```

#### 部署到云平台

你可以将 MCP 服务器部署到任何支持 Node.js 的平台：

**Railway 部署示例:**

1. 创建 `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start:server",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

2. 推送到 GitHub 并连接到 Railway

**Docker 部署:**

创建 `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start:server"]
```

构建并运行:

```bash
docker build -t agent-report-mcp .
docker run -p 3000:3000 agent-report-mcp
```

#### 使用远程服务器的优势

- ✅ 无需本地安装 Node.js 和依赖
- ✅ 多客户端共享同一个服务器实例
- ✅ 可以在团队内部署，共享使用
- ✅ 支持自动扩展和负载均衡

## 使用方法

### 自动追踪模式 (推荐)

自动追踪模式可以自动记录代码变更，无需手动调用工具。

#### 初始化项目

```bash
# 在项目根目录执行
agent-report-mcp init
```

这会创建一个 `.agent-human-inputs.json` 文件，用于记录人工指导。

#### 启动自动追踪

```bash
# 启动自动追踪（监听当前目录）
agent-report-mcp start "项目名称"

# 指定监听路径
agent-report-mcp start "项目名称" ./src ./lib

# 后台运行
agent-report-mcp start "项目名称" &
```

自动追踪器会：
- 📁 监听文件系统变化，自动记录代码变更
- 🔄 集成 Git，自动同步提交的代码变更
- 🤝 监听人工指导文件，自动记录人工输入
- ⏱️ 自动计算工作时长

#### 记录人工指导

方式1：使用 CLI 命令

```bash
agent-report-mcp input decision "使用 UUID 作为主键" critical
agent-report-mcp input feedback "添加密码强度验证" high
agent-report-mcp input instruction "重构用户认证模块" medium
```

方式2：编辑 `.agent-human-inputs.json` 文件

```json
[
  {
    "type": "decision",
    "content": "使用 UUID 作为主键",
    "impact": "critical"
  },
  {
    "type": "feedback",
    "content": "添加密码强度验证",
    "impact": "high"
  }
]
```

保存文件后，自动追踪器会自动读取并记录这些输入。

#### 生成报告

```bash
# 生成 Markdown 报告（中文）
agent-report-mcp report

# 生成 JSON 报告
agent-report-mcp report --json

# 生成英文报告
agent-report-mcp report --en
```

#### 停止追踪

按 `Ctrl+C` 停止自动追踪器，会自动结束会话并保存数据。

### 手动模式

如果需要更精细的控制，可以使用手动模式。

#### 1. 开始工作会话

```
使用 start_session 工具，传入项目名称
```

#### 2. 开始任务

```
使用 start_task 工具，传入任务描述
```

#### 3. 记录代码变更

```
使用 record_code_change 工具，记录文件变更：
- filePath: 文件路径
- changeType: create/modify/delete
- linesAdded: 新增行数
- linesDeleted: 删除行数
```

#### 4. 记录人工指导

```
使用 record_human_input 工具，记录人工介入：
- type: instruction/decision/feedback/correction
- content: 指导内容
- impact: critical/high/medium/low
```

#### 5. 结束任务

```
使用 end_task 工具，标记任务完成
```

#### 6. 生成报告

```
使用 generate_report 工具生成汇报文档：
- format: markdown/json
- includeCodeStats: 是否包含代码统计
- includeHumanInputs: 是否包含人工指导详情
- includeTimeline: 是否包含时间线
- language: zh/en
```

#### 7. 结束会话

```
使用 end_session 工具，传入工作总结
```

## 报告示例

生成的报告包含：
- 📊 执行摘要
- 📈 关键指标（工作时长、代码变更、人工介入次数等）
- 📝 详细工作内容
- 🤝 人机协作亮点
- ✅ 总结

报告风格简洁明了，既突出 AI Agent 的高效能力，又强调人类指导和决策的不可替代性。

## 可用工具

| 工具名 | 描述 |
|--------|------|
| `start_session` | 开始新的工作会话 |
| `end_session` | 结束工作会话 |
| `start_task` | 开始追踪新任务 |
| `end_task` | 标记任务完成或失败 |
| `record_code_change` | 记录代码变更 |
| `record_human_input` | 记录人工指导 |
| `generate_report` | 生成工作报告 |
| `get_session_status` | 获取当前会话状态 |

## 开发

```bash
# 编译
npm run build

# 开发模式
npm run dev

# 运行
npm start
```

## License

MIT
