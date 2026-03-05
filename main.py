#!/usr/bin/env python3
"""Agent Report MCP Server using FastMCP"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastmcp import McpServer, McpTool
from pydantic import BaseModel

class WorkSession(BaseModel):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    project_name: str
    tasks: List['Task'] = []
    summary: Optional[str] = None

class Task(BaseModel):
    id: str
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # in_progress, completed, failed
    code_changes: List['CodeChange'] = []
    human_inputs: List['HumanInput'] = []

class CodeChange(BaseModel):
    id: str
    file_path: str
    change_type: str  # create, modify, delete
    lines_added: int = 0
    lines_deleted: int = 0
    timestamp: datetime

class HumanInput(BaseModel):
    id: str
    type: str  # instruction, decision, feedback, correction
    content: str
    timestamp: datetime
    impact: str  # critical, high, medium, low

class ReportOptions(BaseModel):
    format: str = 'markdown'  # markdown, json
    include_code_stats: bool = True
    include_human_inputs: bool = True
    include_timeline: bool = True
    language: str = 'zh'  # zh, en

class WorkTracker:
    def __init__(self):
        self.current_session: Optional[WorkSession] = None
        self.current_task: Optional[Task] = None
    
    def start_session(self, project_name: str) -> WorkSession:
        session_id = f"{int(time.time())}-{hash(project_name) % 10000}"
        self.current_session = WorkSession(
            id=session_id,
            start_time=datetime.now(),
            project_name=project_name
        )
        return self.current_session
    
    def end_session(self, summary: Optional[str] = None) -> Optional[WorkSession]:
        if not self.current_session:
            return None
        
        if self.current_task:
            self.end_task()
        
        self.current_session.end_time = datetime.now()
        self.current_session.summary = summary
        return self.current_session
    
    def start_task(self, description: str) -> Task:
        if not self.current_session:
            raise ValueError("No active session. Call start_session first.")
        
        if self.current_task:
            self.end_task()
        
        task_id = f"{int(time.time())}-{hash(description) % 10000}"
        self.current_task = Task(
            id=task_id,
            description=description,
            start_time=datetime.now(),
            status='in_progress'
        )
        
        self.current_session.tasks.append(self.current_task)
        return self.current_task
    
    def end_task(self, status: str = 'completed') -> Optional[Task]:
        if not self.current_task:
            return None
        
        self.current_task.end_time = datetime.now()
        self.current_task.status = status
        
        task = self.current_task
        self.current_task = None
        return task
    
    def record_code_change(self, file_path: str, change_type: str, lines_added: int = 0, lines_deleted: int = 0) -> CodeChange:
        if not self.current_task:
            raise ValueError("No active task. Call start_task first.")
        
        change_id = f"{int(time.time())}-{hash(file_path) % 10000}"
        change = CodeChange(
            id=change_id,
            file_path=file_path,
            change_type=change_type,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            timestamp=datetime.now()
        )
        
        self.current_task.code_changes.append(change)
        return change
    
    def record_human_input(self, type: str, content: str, impact: str = 'medium') -> HumanInput:
        if not self.current_task:
            raise ValueError("No active task. Call start_task first.")
        
        input_id = f"{int(time.time())}-{hash(content) % 10000}"
        human_input = HumanInput(
            id=input_id,
            type=type,
            content=content,
            timestamp=datetime.now(),
            impact=impact
        )
        
        self.current_task.human_inputs.append(human_input)
        return human_input
    
    def get_current_session(self) -> Optional[WorkSession]:
        return self.current_session
    
    def get_current_task(self) -> Optional[Task]:
        return self.current_task

class ReportGenerator:
    def generate_report(self, session: WorkSession, options: ReportOptions) -> str:
        if options.format == 'json':
            return self._generate_json(session, options)
        return self._generate_markdown(session, options)
    
    def _generate_json(self, session: WorkSession, options: ReportOptions) -> str:
        data = self._prepare_data(session)
        return json.dumps(data, default=str, indent=2, ensure_ascii=False)
    
    def _generate_markdown(self, session: WorkSession, options: ReportOptions) -> str:
        data = self._prepare_data(session)
        is_zh = options.language == 'zh'
        
        markdown = []
        markdown.append(f"# {'AI Agent 工作汇报' if is_zh else 'AI Agent Work Report'}")
        markdown.append("")
        markdown.append(f"> **{'项目' if is_zh else 'Project'}:** {session.project_name}  ")
        markdown.append(f"> **{'汇报时间' if is_zh else 'Report Time'}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        markdown.append(f"> **{'工作时段' if is_zh else 'Work Period'}:** {session.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else ('进行中' if is_zh else 'Ongoing')}")
        markdown.append("")
        
        # Executive Summary
        markdown.append(f"## {'📊 执行摘要' if is_zh else '📊 Executive Summary'}")
        markdown.append("")
        markdown.append(('本次工作中，AI Agent 与人类紧密协作，高效完成了既定目标。' if is_zh else 
                       'In this work session, AI Agent collaborated closely with humans to efficiently achieve the set objectives.'))
        markdown.append("")
        
        # Key Metrics
        markdown.append(f"## {'📈 关键指标' if is_zh else '📈 Key Metrics'}")
        markdown.append("")
        markdown.append(f"| {'指标' if is_zh else 'Metric'} | {'数值' if is_zh else 'Value'} |")
        markdown.append("|------|------|")
        markdown.append(f"| {'工作时长' if is_zh else 'Duration'} | {self._format_duration(data['total_duration'])} |")
        markdown.append(f"| {'完成任务' if is_zh else 'Tasks Completed'} | {data['completed_tasks']}/{len(session.tasks)} |")
        markdown.append(f"| {'代码变更' if is_zh else 'Code Changes'} | {data['total_code_lines']} {'行' if is_zh else 'lines'} |")
        markdown.append(f"| {'文件变动' if is_zh else 'Files Changed'} | {data['total_files_changed']} {'个' if is_zh else 'files'} |")
        markdown.append(f"| {'人工介入' if is_zh else 'Human Inputs'} | {data['human_input_count']} {'次' if is_zh else 'times'} |")
        markdown.append(f"| {'关键决策' if is_zh else 'Critical Decisions'} | {data['critical_decisions_count']} |")
        markdown.append("")
        
        # Work Content
        markdown.append(f"## {'📝 工作内容' if is_zh else '📝 Work Content'}")
        markdown.append("")
        
        if session.summary:
            markdown.append(f"### {'工作概述' if is_zh else 'Work Overview'}")
            markdown.append("")
            markdown.append(session.summary)
            markdown.append("")
        
        for i, task in enumerate(session.tasks, 1):
            task_duration = (task.end_time - task.start_time).total_seconds() if task.end_time else (datetime.now() - task.start_time).total_seconds()
            code_lines = sum(c.lines_added + c.lines_deleted for c in task.code_changes)
            
            markdown.append(f"### {'任务' if is_zh else 'Task'} {i}: {task.description}")
            markdown.append("")
            markdown.append(f"- **{'状态' if is_zh else 'Status'}:** {self._get_status_emoji(task.status)} {self._format_status(task.status, is_zh)}  ")
            markdown.append(f"- **{'耗时' if is_zh else 'Duration'}:** {self._format_duration(task_duration)}  ")
            markdown.append(f"- **{'代码变更' if is_zh else 'Code Changes'}:** {code_lines} {'行' if is_zh else 'lines'}  ")
            markdown.append(f"- **{'人工指导' if is_zh else 'Human Guidance'}:** {len(task.human_inputs)} {'次' if is_zh else 'times'}")
            markdown.append("")
            
            if options.include_human_inputs and task.human_inputs:
                markdown.append(f"#### {'人工指导详情' if is_zh else 'Human Guidance Details'}")
                markdown.append("")
                for input in task.human_inputs:
                    markdown.append(f"- **{self._get_input_type_label(input.type, is_zh)}** ({self._get_impact_label(input.impact, is_zh)}): {input.content}")
                markdown.append("")
        
        # Human-AI Collaboration
        markdown.append(f"## {'🤝 人机协作亮点' if is_zh else '🤝 Human-AI Collaboration Highlights'}")
        markdown.append("")
        
        if data['critical_decisions']:
            markdown.append(f"### {'关键决策点' if is_zh else 'Key Decision Points'}")
            markdown.append("")
            markdown.append(('以下人类指导对项目成功起到了决定性作用：' if is_zh else 
                           'The following human guidance played a decisive role in project success:'))
            markdown.append("")
            for decision in data['critical_decisions']:
                markdown.append(f"- **{self._get_input_type_label(decision.type, is_zh)}**: {decision.content}")
            markdown.append("")
        
        markdown.append(f"### {'协作总结' if is_zh else 'Collaboration Summary'}")
        markdown.append("")
        markdown.append(('在整个工作过程中，**AI Agent 展现了高效的代码生成和问题解决能力**，同时**人类的战略指导和关键决策确保了方向的正确性**。\n\n' if is_zh else 
                       'Throughout the work process, **AI Agent demonstrated efficient code generation and problem-solving capabilities**, while **human strategic guidance and key decisions ensured the correct direction**.'))
        markdown.append(('具体体现：\n' if is_zh else 'Key highlights:\n'))
        markdown.append(f"- AI Agent 自主完成了 {data['completed_tasks']} 个任务，生成 {data['total_code_lines']} 行高质量代码")
        markdown.append(f"- 人类提供 {data['human_input_count']} 次精准指导，其中 {data['critical_decisions_count']} 次关键决策直接影响项目走向")
        markdown.append(f"- 人机协作模式显著提升了开发效率，实现了 1+1>2 的效果")
        markdown.append("")
        
        # Conclusion
        markdown.append(f"## {'✅ 总结' if is_zh else '✅ Conclusion'}")
        markdown.append("")
        markdown.append(('本次工作充分展示了 AI Agent 在现代软件开发中的价值。通过人机协作模式，我们不仅提高了开发效率，更确保了代码质量和业务目标的达成。**AI Agent 是强大的工具，而人类的创造力和判断力仍是不可替代的核心竞争力。**' if is_zh else 
                       'This work fully demonstrated the value of AI Agent in modern software development. Through the human-AI collaboration model, we not only improved development efficiency but also ensured code quality and business objectives. **AI Agent is a powerful tool, while human creativity and judgment remain irreplaceable core competencies.**'))
        markdown.append("")
        markdown.append("---")
        markdown.append("")
        markdown.append(f"*{'本报告由 AI Agent Report MCP 工具自动生成' if is_zh else 'This report was automatically generated by AI Agent Report MCP Tool'}*")
        
        return '\n'.join(markdown)
    
    def _prepare_data(self, session: WorkSession) -> Dict[str, Any]:
        total_duration = (session.end_time - session.start_time).total_seconds() if session.end_time else (datetime.now() - session.start_time).total_seconds()
        
        total_code_lines = 0
        total_files = set()
        human_input_count = 0
        critical_decisions = []
        completed_tasks = 0
        
        for task in session.tasks:
            if task.status == 'completed':
                completed_tasks += 1
            for change in task.code_changes:
                total_code_lines += change.lines_added + change.lines_deleted
                total_files.add(change.file_path)
            human_input_count += len(task.human_inputs)
            for input in task.human_inputs:
                if input.impact in ['critical', 'high']:
                    critical_decisions.append(input)
        
        return {
            'total_duration': total_duration,
            'total_code_lines': total_code_lines,
            'total_files_changed': len(total_files),
            'human_input_count': human_input_count,
            'critical_decisions': critical_decisions,
            'critical_decisions_count': len(critical_decisions),
            'completed_tasks': completed_tasks
        }
    
    def _format_duration(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"
    
    def _get_status_emoji(self, status: str) -> str:
        status_map = {
            'completed': '✅',
            'in_progress': '🔄',
            'failed': '❌'
        }
        return status_map.get(status, '⏳')
    
    def _format_status(self, status: str, is_zh: bool) -> str:
        if is_zh:
            status_map = {
                'completed': '已完成',
                'in_progress': '进行中',
                'failed': '失败'
            }
        else:
            status_map = {
                'completed': 'Completed',
                'in_progress': 'In Progress',
                'failed': 'Failed'
            }
        return status_map.get(status, 'Unknown')
    
    def _get_input_type_label(self, type: str, is_zh: bool) -> str:
        if is_zh:
            type_map = {
                'instruction': '指令',
                'decision': '决策',
                'feedback': '反馈',
                'correction': '纠正'
            }
        else:
            type_map = {
                'instruction': 'Instruction',
                'decision': 'Decision',
                'feedback': 'Feedback',
                'correction': 'Correction'
            }
        return type_map.get(type, type)
    
    def _get_impact_label(self, impact: str, is_zh: bool) -> str:
        if is_zh:
            impact_map = {
                'critical': '关键',
                'high': '高',
                'medium': '中',
                'low': '低'
            }
        else:
            impact_map = {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low'
            }
        return impact_map.get(impact, impact)

# Initialize tracker and generator
tracker = WorkTracker()
generator = ReportGenerator()

# Create MCP server
server = McpServer(
    name="agent-report-mcp",
    version="1.0.0"
)

# Define tools

@server.tool
def start_session(project_name: str) -> dict:
    """Start a new work session for tracking AI Agent activities"""
    session = tracker.start_session(project_name)
    return {
        "message": f"Work session started for project: {project_name}",
        "session_id": session.id,
        "start_time": session.start_time.isoformat()
    }

@server.tool
def end_session(summary: Optional[str] = None) -> dict:
    """End the current work session and generate summary"""
    session = tracker.end_session(summary)
    if not session:
        return {
            "error": "No active session to end."
        }
    return {
        "message": f"Work session ended for project: {session.project_name}",
        "session_id": session.id,
        "duration": (session.end_time - session.start_time).total_seconds() if session.end_time else 0,
        "tasks_completed": sum(1 for t in session.tasks if t.status == 'completed'),
        "total_tasks": len(session.tasks)
    }

@server.tool
def start_task(description: str) -> dict:
    """Start tracking a new task within the current session"""
    try:
        task = tracker.start_task(description)
        return {
            "message": f"Task started: {description}",
            "task_id": task.id,
            "start_time": task.start_time.isoformat()
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

@server.tool
def end_task(status: str = 'completed') -> dict:
    """Mark the current task as completed or failed"""
    try:
        task = tracker.end_task(status)
        if not task:
            return {
                "error": "No active task to end."
            }
        return {
            "message": f"Task ended: {task.description}",
            "status": status,
            "duration": (task.end_time - task.start_time).total_seconds() if task.end_time else 0
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

@server.tool
def record_code_change(
    file_path: str,
    change_type: str,
    lines_added: int = 0,
    lines_deleted: int = 0
) -> dict:
    """Record a code change (file creation, modification, or deletion)"""
    try:
        change = tracker.record_code_change(file_path, change_type, lines_added, lines_deleted)
        return {
            "message": f"Code change recorded: {change_type} {file_path}",
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "timestamp": change.timestamp.isoformat()
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

@server.tool
def record_human_input(
    type: str,
    content: str,
    impact: str = 'medium'
) -> dict:
    """Record human guidance, decision, feedback, or correction"""
    try:
        human_input = tracker.record_human_input(type, content, impact)
        return {
            "message": f"Human input recorded: {type} ({impact})",
            "content": content,
            "timestamp": human_input.timestamp.isoformat()
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

@server.tool
def generate_report(
    format: str = 'markdown',
    include_code_stats: bool = True,
    include_human_inputs: bool = True,
    include_timeline: bool = True,
    language: str = 'zh'
) -> dict:
    """Generate a work report in markdown or JSON format"""
    session = tracker.get_current_session()
    if not session:
        return {
            "error": "No active session. Start a session first using start_session."
        }
    
    options = ReportOptions(
        format=format,
        include_code_stats=include_code_stats,
        include_human_inputs=include_human_inputs,
        include_timeline=include_timeline,
        language=language
    )
    
    report = generator.generate_report(session, options)
    return {
        "report": report
    }

@server.tool
def get_session_status() -> dict:
    """Get the current status of the work session"""
    session = tracker.get_current_session()
    task = tracker.get_current_task()
    
    if not session:
        return {
            "message": "No active session."
        }
    
    duration = (datetime.now() - session.start_time).total_seconds()
    total_code_lines = sum(
        sum(c.lines_added + c.lines_deleted for c in task.code_changes)
        for task in session.tasks
    )
    total_files = len(set(
        c.file_path for task in session.tasks for c in task.code_changes
    ))
    human_inputs = sum(len(task.human_inputs) for task in session.tasks)
    
    return {
        "project": session.project_name,
        "session_id": session.id,
        "started": session.start_time.isoformat(),
        "duration": duration,
        "tasks": len(session.tasks),
        "tasks_completed": sum(1 for t in session.tasks if t.status == 'completed'),
        "current_task": task.description if task else "None",
        "code_changes": total_code_lines,
        "files_changed": total_files,
        "human_inputs": human_inputs
    }

if __name__ == "__main__":
    server.run()
