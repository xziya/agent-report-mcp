#!/bin/bash

# 测试脚本 - 模拟完整的工作流程

echo "=== Agent Report MCP 测试 ==="
echo ""

# 注意：这个脚本演示了如何使用 MCP 工具
# 实际使用时，这些调用会通过 Claude 或 OpenCode CLI 自动完成

cat << 'EOF'

测试场景：开发一个用户认证模块

步骤 1: 开始工作会话
-------------------
工具: start_session
参数: {"projectName": "用户认证模块开发"}

步骤 2: 开始第一个任务
---------------------
工具: start_task
参数: {"description": "设计用户数据库模型"}

步骤 3: 记录代码变更
-------------------
工具: record_code_change
参数: {
  "filePath": "src/models/user.ts",
  "changeType": "create",
  "linesAdded": 45,
  "linesDeleted": 0
}

步骤 4: 记录人工指导
-------------------
工具: record_human_input
参数: {
  "type": "decision",
  "content": "使用 UUID 作为主键，添加 email 唯一索引",
  "impact": "critical"
}

步骤 5: 结束第一个任务
---------------------
工具: end_task
参数: {"status": "completed"}

步骤 6: 开始第二个任务
---------------------
工具: start_task
参数: {"description": "实现登录 API 接口"}

步骤 7: 记录代码变更
-------------------
工具: record_code_change
参数: {
  "filePath": "src/routes/auth.ts",
  "changeType": "create",
  "linesAdded": 120,
  "linesDeleted": 0
}

工具: record_code_change
参数: {
  "filePath": "src/middleware/jwt.ts",
  "changeType": "create",
  "linesAdded": 35,
  "linesDeleted": 0
}

步骤 8: 记录人工反馈
-------------------
工具: record_human_input
参数: {
  "type": "feedback",
  "content": "添加密码强度验证，要求至少8位包含大小写字母",
  "impact": "high"
}

步骤 9: 记录代码修正
-------------------
工具: record_code_change
参数: {
  "filePath": "src/routes/auth.ts",
  "changeType": "modify",
  "linesAdded": 15,
  "linesDeleted": 5
}

步骤 10: 结束第二个任务
----------------------
工具: end_task
参数: {"status": "completed"}

步骤 11: 生成工作报告
--------------------
工具: generate_report
参数: {
  "format": "markdown",
  "includeCodeStats": true,
  "includeHumanInputs": true,
  "includeTimeline": true,
  "language": "zh"
}

步骤 12: 结束工作会话
--------------------
工具: end_session
参数: {
  "summary": "完成了用户认证模块的核心功能，包括数据库模型设计和登录 API 实现"
}

EOF

echo ""
echo "=== 测试说明 ==="
echo "以上步骤展示了完整的工作流程。实际使用时，Claude 或 OpenCode 会自动调用这些工具。"
echo ""
echo "要手动测试 MCP 服务器，可以运行:"
echo "  node dist/index.js"
echo ""
echo "然后在支持 MCP 的客户端中配置此服务器。"
