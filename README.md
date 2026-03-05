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

## 安装

### 使用 uv 管理（推荐）

```bash
# 初始化 uv 环境
uv init

# 安装依赖
uv install
```

### 使用 pip

```bash
# 安装依赖
pip install -r requirements.txt
```

## 配置

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "agent-report": {
      "command": "python",
      "args": ["/path/to/agent-report-mcp/cli.py", "start"]
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
      "command": "python",
      "args": ["/path/to/agent-report-mcp/cli.py", "start"]
    }
  }
}
```

**注意**: 请将 `/path/to/agent-report-mcp/cli.py` 替换为实际的绝对路径。可以使用 `pwd` 命令获取当前目录路径：

```bash
# 在 agent-report-mcp 目录下执行
pwd
```

**验证配置**:

```bash
# 检查配置文件是否正确
cat ~/.config/claude/config.json

# 测试 MCP 服务器是否正常运行
python /path/to/agent-report-mcp/cli.py start
```

### OpenCode CLI 配置

在 OpenCode 配置文件中添加：

```json
{
  "mcpServers": {
    "agent-report": {
      "command": "python",
      "args": ["/path/to/agent-report-mcp/cli.py", "start"]
    }
  }
}
```

## 使用方法

### 使用 uv 命令（推荐）

#### 初始化项目

```bash
# 初始化项目
uv run init
```

#### 启动 MCP 服务器

```bash
# 启动 MCP 服务器
uv run start
```

#### 管理自动追踪

```bash
# 启动自动追踪
uv run auto start "项目名称"

# 停止自动追踪
uv run auto stop

# 查看状态
uv run auto status
```

#### 记录人工指导

```bash
uv run input decision "使用 UUID 作为主键" critical
uv run input feedback "添加密码强度验证" high
uv run input instruction "重构用户认证模块" medium
```

#### 生成报告

```bash
# 生成 Markdown 报告（中文）
uv run report

# 生成 JSON 报告
uv run report --json

# 生成英文报告
uv run report --en
```

### 使用 Python 命令

#### 初始化项目

```bash
# 在项目根目录执行
python cli.py init
```

#### 启动自动追踪

```bash
# 启动自动追踪（监听当前目录）
python cli.py auto start "项目名称"

# 后台运行
python cli.py auto start "项目名称" &
```

自动追踪器会：
- 📁 监听文件系统变化，自动记录代码变更
- 🔄 集成 Git，自动同步提交的代码变更
- 🤝 监听人工指导文件，自动记录人工输入
- ⏱️ 自动计算工作时长

#### 记录人工指导

方式1：使用 CLI 命令

```bash
python cli.py input decision "使用 UUID 作为主键" critical
python cli.py input feedback "添加密码强度验证" high
python cli.py input instruction "重构用户认证模块" medium
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
python cli.py report

# 生成 JSON 报告
python cli.py report --json

# 生成英文报告
python cli.py report --en
```

#### 停止追踪

按 `Ctrl+C` 停止自动追踪器，会自动结束会话并保存数据。

### 手动模式

如果需要更精细的控制，可以使用手动模式。

#### 1. 启动 MCP 服务器

```bash
# 使用 uv
uv run start

# 或使用 python
python cli.py start
```

#### 2. 在 Claude/OpenCode 中使用工具

```
使用 start_session 工具，传入项目名称
使用 start_task 工具，传入任务描述
使用 record_code_change 工具，记录文件变更
使用 record_human_input 工具，记录人工介入
使用 end_task 工具，标记任务完成
使用 generate_report 工具生成汇报文档
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

### 使用 uv

```bash
# 安装依赖
uv install

# 运行 MCP 服务器
uv run start

# 初始化项目
uv run init

# 管理自动追踪
uv run auto start "项目名称"
uv run auto stop
uv run auto status

# 生成报告
uv run report
```

### 使用 Python

```bash
# 运行 MCP 服务器
python cli.py start

# 初始化项目
python cli.py init

# 管理自动追踪
python cli.py auto start "项目名称"
python cli.py auto stop
python cli.py auto status

# 生成报告
python cli.py report
```

## License

MIT
