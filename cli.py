#!/usr/bin/env python3
"""CLI for Agent Report MCP"""

import sys
import os
from main import tracker, server, generate_report
from auto_tracker import AutoTracker, init_project as init_auto_tracker, add_human_input

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "start":
        start_server()
    elif command == "init":
        init_project()
    elif command == "input":
        handle_input()
    elif command == "report":
        handle_report()
    elif command == "auto":
        handle_auto()
    else:
        print_usage()

def start_server():
    """Start MCP server"""
    print("Starting Agent Report MCP server...")
    print("Server is running. Press Ctrl+C to stop.")
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped.")

def init_project():
    """Initialize project for auto-tracking"""
    init_auto_tracker()

def handle_input():
    """Handle human input command"""
    if len(sys.argv) < 4:
        print("Usage: python cli.py input <type> <content> [impact]")
        print("Types: instruction, decision, feedback, correction")
        print("Impacts: critical, high, medium, low")
        return
    
    input_type = sys.argv[2]
    content = sys.argv[3]
    impact = sys.argv[4] if len(sys.argv) > 4 else "medium"
    
    add_human_input(input_type, content, impact)

def handle_report():
    """Generate report"""
    format = "markdown"
    language = "zh"
    
    for arg in sys.argv[2:]:
        if arg == "--json":
            format = "json"
        elif arg == "--en":
            language = "en"
    
    session = tracker.get_current_session()
    if not session:
        print("No active session. Start a session first.")
        return
    
    from main import ReportOptions, ReportGenerator
    options = ReportOptions(
        format=format,
        include_code_stats=True,
        include_human_inputs=True,
        include_timeline=True,
        language=language
    )
    
    generator = ReportGenerator()
    report = generator.generate_report(session, options)
    print(report)

def handle_auto():
    """Handle auto-tracking commands"""
    if len(sys.argv) < 3:
        print("Usage: python cli.py auto <subcommand>")
        print("Subcommands: start, stop, status")
        return
    
    subcommand = sys.argv[2]
    
    if subcommand == "start":
        start_auto_tracking()
    elif subcommand == "stop":
        stop_auto_tracking()
    elif subcommand == "status":
        print_auto_status()
    else:
        print("Invalid subcommand. Use: start, stop, status")

def start_auto_tracking():
    """Start automatic tracking"""
    project_name = "Auto-tracked Project"
    if len(sys.argv) > 3:
        project_name = " ".join(sys.argv[3:])
    
    config = {
        "project_name": project_name,
        "watch_paths": [os.getcwd()],
        "git_enabled": True,
        "auto_start_session": True
    }
    
    global auto_tracker
    auto_tracker = AutoTracker(config)
    auto_tracker.start(tracker)
    
    print(f"Auto-tracking started for project: {project_name}")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Check for git changes every 5 seconds
            auto_tracker.check_git_changes()
            import time
            time.sleep(5)
    except KeyboardInterrupt:
        auto_tracker.stop()

def stop_auto_tracking():
    """Stop automatic tracking"""
    global auto_tracker
    if 'auto_tracker' in globals() and auto_tracker:
        auto_tracker.stop()
    else:
        print("No auto-tracking session is running.")

def print_auto_status():
    """Print auto-tracking status"""
    session = tracker.get_current_session()
    if not session:
        print("No active session.")
        return
    
    task = tracker.get_current_task()
    duration = (session.end_time - session.start_time).total_seconds() if session.end_time else (
        (tracker.get_current_session().end_time - tracker.get_current_session().start_time).total_seconds() if tracker.get_current_session().end_time else 0
    )
    
    print(f"Project: {session.project_name}")
    print(f"Session ID: {session.id}")
    print(f"Started: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {int(duration // 3600)}h {int((duration % 3600) // 60)}m")
    print(f"Tasks: {len(session.tasks)} ({sum(1 for t in session.tasks if t.status == 'completed')} completed)")
    print(f"Current task: {task.description if task else 'None'}")
    
    # Calculate code changes
    total_code_lines = sum(
        sum(c.lines_added + c.lines_deleted for c in task.code_changes)
        for task in session.tasks
    )
    total_files = len(set(
        c.file_path for task in session.tasks for c in task.code_changes
    ))
    human_inputs = sum(len(task.human_inputs) for task in session.tasks)
    
    print(f"Code changes: {total_code_lines} lines across {total_files} files")
    print(f"Human inputs: {human_inputs}")

def print_usage():
    """Print usage information"""
    print("\nAgent Report MCP - CLI Tool\n")
    print("Usage:")
    print("  python cli.py start")
    print("    Start MCP server for Claude/OpenCode integration")
    print("\n  python cli.py init")
    print("    Initialize project for auto-tracking")
    print("\n  python cli.py input <type> <content> [impact]")
    print("    Add human input to tracking")
    print("    Types: instruction, decision, feedback, correction")
    print("    Impacts: critical, high, medium, low")
    print("\n  python cli.py report [--json] [--en]")
    print("    Generate work report")
    print("    --json: Output as JSON")
    print("    --en: Generate report in English")
    print("\n  python cli.py auto <subcommand>")
    print("    Manage auto-tracking")
    print("    Subcommands:")
    print("      start [project-name] - Start auto-tracking")
    print("      stop - Stop auto-tracking")
    print("      status - Show current status")
    print("\nExamples:")
    print("  python cli.py input decision "Use UUID for user IDs" critical")
    print("  python cli.py report")
    print("  python cli.py auto start "My Project"")

if __name__ == "__main__":
    main()
