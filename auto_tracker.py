#!/usr/bin/env python3
"""Automatic work tracker for Agent Report MCP"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from git import Repo, GitCommandError

class AutoTracker:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "watch_paths": [os.getcwd()],
            "git_enabled": True,
            "auto_start_session": True,
            "project_name": "Auto-tracked Project",
            "ignore_patterns": [
                "node_modules",
                "dist",
                "build",
                ".git",
                "*.log",
                ".DS_Store",
                ".agent-human-inputs.json"
            ],
            "human_input_file": ".agent-human-inputs.json"
        }
        
        self.observer = None
        self.git_repo = None
        self.last_commit = None
        self.is_running = False
        self.tracker = None
        self.human_inputs_processed = set()
    
    def start(self, tracker_instance):
        """Start automatic tracking"""
        self.tracker = tracker_instance
        self.is_running = True
        
        # Start file system watcher
        self._start_file_watcher()
        
        # Initialize Git integration
        if self.config["git_enabled"]:
            self._init_git()
        
        # Start human input watcher
        self._start_human_input_watcher()
        
        # Auto start session if configured
        if self.config["auto_start_session"]:
            self.tracker.start_session(self.config["project_name"])
            print(f"Auto-tracking started for project: {self.config['project_name']}")
    
    def stop(self):
        """Stop automatic tracking"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.tracker:
            session = self.tracker.end_session("Auto-tracking session ended")
            if session:
                duration = (session.end_time - session.start_time).total_seconds() if session.end_time else 0
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"Auto-tracking session ended. Duration: {hours}h {minutes}m")
    
    def _start_file_watcher(self):
        """Start file system watcher"""
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        
        for path in self.config["watch_paths"]:
            self.observer.schedule(event_handler, path, recursive=True)
        
        self.observer.start()
        print(f"File system watcher started for paths: {self.config['watch_paths']}")
    
    def _init_git(self):
        """Initialize Git integration"""
        try:
            self.git_repo = Repo(os.getcwd())
            self.last_commit = self.git_repo.head.commit.hexsha
            print("Git integration enabled")
        except GitCommandError:
            print("Not a git repository, git integration disabled")
            self.git_repo = None
    
    def _start_human_input_watcher(self):
        """Start human input watcher"""
        if os.path.exists(self.config["human_input_file"]):
            self._process_human_inputs()
    
    def _process_human_inputs(self):
        """Process human inputs from file"""
        try:
            with open(self.config["human_input_file"], 'r', encoding='utf-8') as f:
                inputs = json.load(f)
            
            for input_data in inputs:
                input_id = f"{input_data['type']}-{input_data['content'][:20]}"
                if input_id not in self.human_inputs_processed:
                    self.tracker.record_human_input(
                        input_data['type'],
                        input_data['content'],
                        input_data.get('impact', 'medium')
                    )
                    self.human_inputs_processed.add(input_id)
                    print(f"Recorded human input: {input_data['type']}")
            
            # Clear processed inputs
            with open(self.config["human_input_file"], 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            print(f"Error processing human inputs: {e}")
    
    def _should_ignore(self, path):
        """Check if path should be ignored"""
        for pattern in self.config["ignore_patterns"]:
            if pattern in path:
                return True
        return False
    
    def record_file_change(self, event_type, path):
        """Record file change"""
        if not self.is_running or not self.tracker:
            return
        
        if self._should_ignore(path):
            return
        
        try:
            change_type = "modify"
            if event_type == "created":
                change_type = "create"
            elif event_type == "deleted":
                change_type = "delete"
            
            lines_added = 0
            lines_deleted = 0
            
            if event_type != "deleted":
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines_added = len(f.readlines())
                except:
                    pass
            
            # Ensure we have an active task
            if not self.tracker.get_current_task():
                self.tracker.start_task(f"File change: {os.path.basename(path)}")
            
            self.tracker.record_code_change(
                path,
                change_type,
                lines_added,
                lines_deleted
            )
            print(f"Recorded {change_type}: {path}")
        except Exception as e:
            print(f"Error recording file change: {e}")
    
    def check_git_changes(self):
        """Check for git changes"""
        if not self.git_repo:
            return
        
        try:
            current_commit = self.git_repo.head.commit.hexsha
            if current_commit != self.last_commit:
                diff = self.git_repo.git.diff(self.last_commit, current_commit, '--numstat')
                self.last_commit = current_commit
                
                for line in diff.split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            lines_added = int(parts[0])
                            lines_deleted = int(parts[1])
                            file_path = parts[2]
                            
                            if not self._should_ignore(file_path):
                                change_type = "modify"
                                if lines_deleted > 0 and lines_added == 0:
                                    change_type = "delete"
                                elif lines_added > 0 and lines_deleted == 0:
                                    change_type = "create"
                                
                                if not self.tracker.get_current_task():
                                    self.tracker.start_task(f"Git commit: {current_commit[:7]}")
                                
                                self.tracker.record_code_change(
                                    file_path,
                                    change_type,
                                    lines_added,
                                    lines_deleted
                                )
                                print(f"Synced git change: {change_type} {file_path}")
        except Exception as e:
            print(f"Error checking git changes: {e}")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, auto_tracker):
        self.auto_tracker = auto_tracker
    
    def on_created(self, event):
        if not event.is_directory:
            self.auto_tracker.record_file_change("created", event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.auto_tracker.record_file_change("modified", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.auto_tracker.record_file_change("deleted", event.src_path)

def init_project():
    """Initialize project for auto-tracking"""
    human_input_file = ".agent-human-inputs.json"
    
    if not os.path.exists(human_input_file):
        with open(human_input_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print(f"Created human input file: {human_input_file}")
        print("\nYou can now add human inputs by editing this file or using:")
        print("  python -m agent_report input <type> <content> [impact]")
    else:
        print("Project already initialized")

def add_human_input(input_type, content, impact="medium"):
    """Add human input to tracking"""
    human_input_file = ".agent-human-inputs.json"
    
    try:
        inputs = []
        if os.path.exists(human_input_file):
            with open(human_input_file, 'r', encoding='utf-8') as f:
                inputs = json.load(f)
        
        inputs.append({
            "type": input_type,
            "content": content,
            "impact": impact,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(human_input_file, 'w', encoding='utf-8') as f:
            json.dump(inputs, f, indent=2, ensure_ascii=False)
        
        print("Human input added")
    except Exception as e:
        print(f"Error adding human input: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_project()
        elif command == "input" and len(sys.argv) >= 4:
            input_type = sys.argv[2]
            content = sys.argv[3]
            impact = sys.argv[4] if len(sys.argv) > 4 else "medium"
            add_human_input(input_type, content, impact)
        else:
            print("Usage:")
            print("  python auto_tracker.py init")
            print("  python auto_tracker.py input <type> <content> [impact]")
    else:
        print("AutoTracker module")
        print("Usage:")
        print("  python auto_tracker.py init - Initialize project")
        print("  python auto_tracker.py input <type> <content> [impact] - Add human input")
