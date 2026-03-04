import { WorkSession, Task, CodeChange, HumanInput } from './types.js';

export class WorkTracker {
  private currentSession: WorkSession | null = null;
  private currentTask: Task | null = null;

  startSession(projectName: string): WorkSession {
    this.currentSession = {
      id: this.generateId(),
      startTime: new Date(),
      projectName,
      tasks: [],
    };
    return this.currentSession;
  }

  endSession(summary?: string): WorkSession | null {
    if (!this.currentSession) return null;
    
    if (this.currentTask) {
      this.endTask();
    }
    
    this.currentSession.endTime = new Date();
    this.currentSession.summary = summary;
    
    const session = this.currentSession;
    return session;
  }

  startTask(description: string): Task {
    if (!this.currentSession) {
      throw new Error('No active session. Call startSession first.');
    }
    
    if (this.currentTask) {
      this.endTask();
    }
    
    this.currentTask = {
      id: this.generateId(),
      description,
      startTime: new Date(),
      status: 'in_progress',
      codeChanges: [],
      humanInputs: [],
    };
    
    this.currentSession.tasks.push(this.currentTask);
    return this.currentTask;
  }

  endTask(status: 'completed' | 'failed' = 'completed'): Task | null {
    if (!this.currentTask) return null;
    
    this.currentTask.endTime = new Date();
    this.currentTask.status = status;
    
    const task = this.currentTask;
    this.currentTask = null;
    return task;
  }

  recordCodeChange(
    filePath: string,
    changeType: 'create' | 'modify' | 'delete',
    linesAdded: number = 0,
    linesDeleted: number = 0
  ): CodeChange {
    if (!this.currentTask) {
      throw new Error('No active task. Call startTask first.');
    }
    
    const change: CodeChange = {
      id: this.generateId(),
      filePath,
      changeType,
      linesAdded,
      linesDeleted,
      timestamp: new Date(),
    };
    
    this.currentTask.codeChanges.push(change);
    return change;
  }

  recordHumanInput(
    type: 'instruction' | 'decision' | 'feedback' | 'correction',
    content: string,
    impact: 'critical' | 'high' | 'medium' | 'low' = 'medium'
  ): HumanInput {
    if (!this.currentTask) {
      throw new Error('No active task. Call startTask first.');
    }
    
    const input: HumanInput = {
      id: this.generateId(),
      type,
      content,
      timestamp: new Date(),
      impact,
    };
    
    this.currentTask.humanInputs.push(input);
    return input;
  }

  getCurrentSession(): WorkSession | null {
    return this.currentSession;
  }

  getCurrentTask(): Task | null {
    return this.currentTask;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
