# Agent Report MCP

一个 MCP (Model Context Protocol) 工具，用于自动总结 AI Agent 的工作内容、生成汇报文档。

## 功能特性

- 📊 **工作追踪**: 自动记录工作会话、任务和代码变更
- ⏱️ **时间统计**: 精确计算工作时长和任务耗时
- 📝 **代码统计**: 统计代码行数、文件变更数量
- 🤝 **人机协作记录**: 记录人工指导、决策和反馈
- 📄 **汇报生成**: 生成适合向领导汇报的 Markdown 文档
- 🌐 **多语言支持**: 支持中文和英文报告
- 🔄 **自动追踪**: 在会话期间自动记录文件变更、Git 提交和人工指导
- 🎯 **CLI 工具**: 提供命令行工具，方便快速使用
- 🚀 **CLI Wrapper**: 自动管理整个会话生命周期

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repository-url>
cd agent-report-mcp

# 使用 uv 安装（推荐）
uv install

# 或使用 pip
pip install -r requirements.txt
```

### 2. 启动 CLI Wrapper（最简单）

```bash
# 使用 uv
uv run wrapper "我的项目"

# 或使用 Python
python wrapper.py "我的项目"
```

Wrapper 会自动：
- ✅ 启动工作会话并开启自动追踪
- ✅ 启动 Claude/OpenCode CLI
- ✅ 追踪所有代码变更和 Git 提交
- ✅ 退出时自动生成报告

### 3. 查看报告

退出 CLI 后，报告会自动保存到 `work-report-YYYYMMDD-HHMMSS.md`

## 项目结构

```
agent-report-mcp/
├── main.py              # MCP 服务器和核心功能
├── cli.py               # 命令行工具
├── wrapper.py           # CLI Wrapper（自动会话管理）
├── auto_tracker.py      # 自动追踪模块
├── requirements.txt     # Python 依赖
├── pyproject.toml       # 项目配置（uv）
├── README.md            # 项目文档
├── LICENSE              # MIT 许可证
└── .gitignore           # Git 忽略文件
```

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

### 🎯 CLI Wrapper 模式（最推荐）

使用 wrapper 脚本自动管理整个会话生命周期，无需手动调用任何工具。

#### 启动方式

```bash
# 使用 uv
uv run wrapper "项目名称"

# 或使用 Python
python wrapper.py "项目名称"
```

#### 工作流程

```
1. 启动 wrapper
   ↓
2. 自动执行 start_session(auto_track=True)
   ↓
3. 自动启动 Claude/OpenCode CLI
   ↓
4. 正常工作（自动追踪所有活动）
   ↓
5. 退出 CLI
   ↓
6. 自动执行 generate_report() → 保存报告文件
   ↓
7. 自动执行 end_session()
```

#### 特点

- ✅ **零配置**: 自动检测 Claude CLI 或 OpenCode CLI
- ✅ **全自动**: 启动和退出时自动管理会话
- ✅ **自动追踪**: 文件变更、Git 提交、人工指导
- ✅ **自动报告**: 退出时自动生成并保存报告
- ✅ **信号处理**: 支持 Ctrl+C 优雅退出

#### 环境变量配置

如果 CLI 不在标准路径，可以设置环境变量：

```bash
# 设置 Claude CLI 路径
export CLAUDE_CLI_PATH=/path/to/claude

# 或设置 OpenCode CLI 路径
export OPENCODE_CLI_PATH=/path/to/opencode

# 然后运行
uv run wrapper "项目名称"
```

### 🎯 交互式会话模式

使用交互式 CLI 手动管理会话，适合需要更多控制的场景。

```bash
# 使用 uv
uv run session "项目名称"

# 或使用 Python
python cli.py session "项目名称"
```

交互式命令：
- `input <type> <content> [impact]` - 记录人工指导
- `status` - 查看当前状态
- `report` - 生成报告
- `exit` / `quit` / `q` - 退出会话

### 🎯 自动追踪模式（MCP 工具）

在 `start_session` 和 `end_session` 之间，系统会自动记录所有代码变更和人工指导。

#### 基本流程

```
1. start_session("项目名称", auto_track=True)
   → 自动启动文件监听、Git 集成、人工输入监听

2. 正常工作...
   → 系统自动记录所有代码变更
   → 系统自动记录 Git 提交

3. 需要记录人工指导时：
   方式A：调用 record_human_input("decision", "内容", "critical")
   方式B：编辑 .agent-human-inputs.json 文件

4. generate_report()
   → 生成完整的工作报告

5. end_session("工作总结")
   → 停止自动追踪
```

#### 自动追踪的内容

| 类型 | 触发条件 | 记录内容 |
|------|---------|---------|
| 📁 文件变更 | 文件创建/修改/删除 | 文件路径、变更类型、行数 |
| 🔄 Git 提交 | 检测到新提交 | 提交哈希、文件变更、增删行数 |
| 🤝 人工指导 | 文件变化或手动调用 | 指导类型、内容、影响级别 |

#### 记录人工指导

**方式A：通过 MCP 工具**

```
record_human_input("decision", "使用 UUID 作为主键", "critical")
record_human_input("feedback", "添加密码强度验证", "high")
record_human_input("instruction", "重构用户认证模块", "medium")
```

**方式B：通过文件**

编辑 `.agent-human-inputs.json`：

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

保存后，系统会在 2 秒内自动读取并记录这些输入。

#### 查看当前状态

```
get_session_status()
```

返回：
- 项目名称
- 会话 ID
- 工作时长
- 任务数量和完成情况
- 代码变更统计
- 人工指导次数
- **自动追踪状态**（enabled/disabled）

### 使用 uv 命令

#### 启动 CLI Wrapper（推荐）

```bash
# 启动 CLI Wrapper，自动管理整个会话
uv run wrapper "项目名称"
```

#### 启动交互式会话

```bash
# 启动交互式会话，手动管理
uv run session "项目名称"
```

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
# 启动自动追踪（后台运行）
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

#### 启动 CLI Wrapper（推荐）

```bash
# 启动 CLI Wrapper，自动管理整个会话
python wrapper.py "项目名称"
```

#### 启动交互式会话

```bash
# 启动交互式会话，手动管理
python cli.py session "项目名称"
```

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

## 报告示例

生成的报告包含：
- 📊 执行摘要
- 📈 关键指标（工作时长、代码变更、人工介入次数等）
- 📝 详细工作内容
- 🤝 人机协作亮点
- ✅ 总结

报告风格简洁明了，既突出 AI Agent 的高效能力，又强调人类指导和决策的不可替代性。

## 可用工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `start_session` | 开始新的工作会话 | `project_name`, `auto_track=True` |
| `end_session` | 结束工作会话 | `summary`（可选） |
| `start_task` | 开始追踪新任务 | `description` |
| `end_task` | 标记任务完成或失败 | `status`（completed/failed） |
| `record_code_change` | 记录代码变更（通常自动记录） | `file_path`, `change_type`, `lines_added`, `lines_deleted` |
| `record_human_input` | 记录人工指导 | `type`, `content`, `impact` |
| `generate_report` | 生成工作报告 | `format`, `include_code_stats`, `include_human_inputs`, `include_timeline`, `language` |
| `get_session_status` | 获取当前会话状态 | 无 |

## 人工指导类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `instruction` | 指令 | "实现用户登录功能" |
| `decision` | 决策 | "使用 UUID 作为主键" |
| `feedback` | 反馈 | "添加密码强度验证" |
| `correction` | 纠正 | "修改数据库连接配置" |

## 影响级别

| 级别 | 说明 |
|------|------|
| `critical` | 关键 - 直接影响项目成败 |
| `high` | 高 - 重要但非关键 |
| `medium` | 中 - 一般性指导 |
| `low` | 低 - 次要建议 |

## 忽略的文件/目录

自动追踪会自动忽略：
- `node_modules`
- `dist`, `build`
- `.git`
- `__pycache__`
- `.venv`, `venv`
- `.agent-human-inputs.json`
- `work-report-*.md`, `work-report-*.json`

## 开发

### 使用 uv

```bash
# 安装依赖
uv install

# 启动 CLI Wrapper（推荐）
uv run wrapper "项目名称"

# 启动交互式会话
uv run session "项目名称"

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

## 工作原理

### 自动追踪机制

1. **文件系统监听**：使用 `watchdog` 库监听文件变化
2. **Git 集成**：每 5 秒检查一次 Git 提交
3. **人工输入监听**：每 2 秒检查 `.agent-human-inputs.json` 文件
4. **线程处理**：使用独立线程处理，不影响主程序性能

### 数据流

```
start_session(auto_track=True)
    ↓
启动文件监听器 → 检测文件变更 → 自动记录
启动 Git 检查器 → 检测提交 → 自动记录
启动输入监听器 → 检测文件变化 → 自动记录
    ↓
正常工作（代码编写、Git 提交、人工指导）
    ↓
generate_report() → 生成报告
    ↓
end_session() → 停止追踪 → 保存数据
```

## 常见问题

### Q: 如何查看已生成的报告？

A: 报告会自动保存为 `work-report-YYYYMMDD-HHMMSS.md` 文件，可以使用任何 Markdown 编辑器查看。

### Q: 如何在后台运行自动追踪？

A: 使用 `python cli.py auto start "项目名称" &` 命令在后台运行。

### Q: 如何手动添加人工指导？

A: 有两种方式：
1. 使用命令：`python cli.py input decision "内容" critical`
2. 编辑 `.agent-human-inputs.json` 文件

### Q: 支持哪些 CLI 工具？

A: 支持 Claude CLI 和 OpenCode CLI，wrapper 会自动检测已安装的 CLI。

### Q: 如何自定义 CLI 路径？

A: 设置环境变量 `CLAUDE_CLI_PATH` 或 `OPENCODE_CLI_PATH`。

## License

MIT
