export interface WorkSession {
  id: string;
  startTime: Date;
  endTime?: Date;
  projectName: string;
  tasks: Task[];
  summary?: string;
}

export interface Task {
  id: string;
  description: string;
  startTime: Date;
  endTime?: Date;
  status: 'in_progress' | 'completed' | 'failed';
  codeChanges: CodeChange[];
  humanInputs: HumanInput[];
}

export interface CodeChange {
  id: string;
  filePath: string;
  changeType: 'create' | 'modify' | 'delete';
  linesAdded: number;
  linesDeleted: number;
  timestamp: Date;
}

export interface HumanInput {
  id: string;
  type: 'instruction' | 'decision' | 'feedback' | 'correction';
  content: string;
  timestamp: Date;
  impact: 'critical' | 'high' | 'medium' | 'low';
}

export interface ReportData {
  session: WorkSession;
  totalDuration: number;
  totalCodeLines: number;
  totalFilesChanged: number;
  humanInputCount: number;
  criticalDecisions: HumanInput[];
  generatedAt: Date;
}

export interface ReportOptions {
  format: 'markdown' | 'json';
  includeCodeStats: boolean;
  includeHumanInputs: boolean;
  includeTimeline: boolean;
  language: 'zh' | 'en';
}
