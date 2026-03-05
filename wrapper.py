#!/usr/bin/env python3
"""
Wrapper script for Claude/OpenCode CLI with auto session management.
Automatically starts session on launch and generates report on exit.
"""

import sys
import os
import signal
import atexit
import subprocess
import time
from datetime import datetime

# Add the script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Global variables
tracker = None
project_name = None
report_file = None

def cleanup():
    """Cleanup on exit"""
    global tracker, project_name, report_file
    
    if tracker and tracker.get_current_session():
        print("\n\n" + "=" * 60)
        print("📊 正在生成工作报告...")
        print("=" * 60)
        
        # Import here to avoid circular imports
        from main import ReportGenerator, ReportOptions
        
        # Generate report
        generator = ReportGenerator()
        options = ReportOptions(
            format='markdown',
            include_code_stats=True,
            include_human_inputs=True,
            include_timeline=True,
            language='zh'
        )
        
        try:
            report = generator.generate_report(tracker.get_current_session(), options)
            
            # Save report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n✅ 报告已保存到: {report_file}")
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
        
        # End session
        print("\n正在结束工作会话...")
        session = tracker.end_session("CLI session ended")
        if session:
            duration = (session.end_time - session.start_time).total_seconds() if session.end_time else 0
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            print(f"✅ 会话已结束，工作时长: {hours}小时{minutes}分钟")
            print("=" * 60)

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n\n收到退出信号...")
    cleanup()
    sys.exit(0)

def main():
    global tracker, project_name, report_file
    
    # Parse arguments
    project_name = "CLI Session"
    if len(sys.argv) > 1:
        project_name = " ".join(sys.argv[1:])
    
    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = f"work-report-{timestamp}.md"
    
    print("=" * 60)
    print("🚀 Agent Report MCP - CLI Wrapper")
    print("=" * 60)
    print(f"\n项目名称: {project_name}")
    print(f"报告文件: {report_file}")
    print("\n功能说明:")
    print("  - 启动时自动创建工作会话")
    print("  - 自动追踪文件变更和 Git 提交")
    print("  - 退出时自动生成报告")
    print("\n" + "=" * 60)
    
    # Import WorkTracker
    try:
        from main import WorkTracker
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        sys.exit(1)
    
    # Initialize tracker
    tracker = WorkTracker()
    
    # Start session with auto-tracking
    print("\n正在启动工作会话...")
    session = tracker.start_session(project_name, auto_track=True)
    
    print(f"✅ 会话已启动 (ID: {session.id})")
    print(f"✅ 自动追踪已启用")
    print(f"   - 文件监听: 已启动")
    print(f"   - Git 集成: {'已启动' if tracker.auto_tracker and tracker.auto_tracker.git_repo else '未检测到 Git 仓库'}")
    print(f"   - 人工输入监听: 已启动")
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Determine which CLI to run
    cli_cmd = None
    cli_name = None
    
    if os.environ.get('CLAUDE_CLI_PATH'):
        cli_cmd = os.environ['CLAUDE_CLI_PATH']
        cli_name = "Claude CLI (custom)"
    elif os.environ.get('OPENCODE_CLI_PATH'):
        cli_cmd = os.environ['OPENCODE_CLI_PATH']
        cli_name = "OpenCode CLI (custom)"
    elif os.path.exists('/usr/local/bin/claude'):
        cli_cmd = '/usr/local/bin/claude'
        cli_name = "Claude CLI"
    elif os.path.exists('/usr/local/bin/opencode'):
        cli_cmd = '/usr/local/bin/opencode'
        cli_name = "OpenCode CLI"
    elif os.path.exists(os.path.expanduser('~/.local/bin/claude')):
        cli_cmd = os.path.expanduser('~/.local/bin/claude')
        cli_name = "Claude CLI"
    elif os.path.exists(os.path.expanduser('~/.local/bin/opencode')):
        cli_cmd = os.path.expanduser('~/.local/bin/opencode')
        cli_name = "OpenCode CLI"
    else:
        # Try to find in PATH
        for cmd in ['claude', 'opencode']:
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                cli_cmd = result.stdout.strip()
                cli_name = cmd.capitalize() + " CLI"
                break
    
    if not cli_cmd:
        print("\n❌ Neither Claude CLI nor OpenCode CLI found")
        print("\nPlease set environment variable:")
        print("  export CLAUDE_CLI_PATH=/path/to/claude")
        print("  or")
        print("  export OPENCODE_CLI_PATH=/path/to/opencode")
        print("\nOr install Claude CLI or OpenCode CLI first.")
        sys.exit(1)
    
    print(f"\n正在启动 {cli_name}...")
    print("=" * 60 + "\n")
    
    # Run the CLI
    try:
        process = subprocess.run(cli_cmd, shell=False)
        exit_code = process.returncode
    except Exception as e:
        print(f"\n❌ Failed to run CLI: {e}")
        exit_code = 1
    
    # CLI has exited, cleanup will be handled by atexit
    print("\nCLI 已退出...")
    
    # Exit with the same code as the CLI
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
