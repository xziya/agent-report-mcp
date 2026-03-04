import { WorkTracker } from './tracker.js';
import * as chokidar from 'chokidar';
import { simpleGit, SimpleGit } from 'simple-git';
import * as fs from 'fs/promises';
import * as path from 'path';

export interface AutoTrackerConfig {
  watchPaths: string[];
  gitEnabled: boolean;
  autoStartSession: boolean;
  projectName?: string;
  ignorePatterns: string[];
  humanInputDetection: boolean;
}

export class AutoTracker {
  private tracker: WorkTracker;
  private watcher: chokidar.FSWatcher | null = null;
  private git: SimpleGit | null = null;
  private config: AutoTrackerConfig;
  private lastCommitHash: string = '';
  private isRunning: boolean = false;
  private humanInputFile: string = '.agent-human-inputs.json';

  constructor(config: Partial<AutoTrackerConfig> = {}) {
    this.tracker = new WorkTracker();
    this.config = {
      watchPaths: config.watchPaths || [process.cwd()],
      gitEnabled: config.gitEnabled !== false,
      autoStartSession: config.autoStartSession !== false,
      projectName: config.projectName || 'Auto-tracked Project',
      ignorePatterns: config.ignorePatterns || [
        'node_modules/**',
        'dist/**',
        'build/**',
        '.git/**',
        '*.log',
        '.DS_Store',
      ],
      humanInputDetection: config.humanInputDetection !== false,
    };
  }

  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('AutoTracker is already running');
    }

    this.isRunning = true;

    if (this.config.autoStartSession) {
      this.tracker.startSession(this.config.projectName!);
      console.log(`Auto-tracking started for project: ${this.config.projectName}`);
    }

    if (this.config.gitEnabled) {
      await this.initializeGit();
    }

    await this.startFileWatcher();
    await this.startHumanInputWatcher();

    console.log('AutoTracker is now running');
  }

  async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;

    if (this.watcher) {
      await this.watcher.close();
      this.watcher = null;
    }

    const session = this.tracker.endSession('Auto-tracking session ended');
    if (session) {
      console.log(`Auto-tracking session ended. Duration: ${this.formatDuration(session.endTime!.getTime() - session.startTime.getTime())}`);
    }
  }

  private async initializeGit(): Promise<void> {
    try {
      this.git = simpleGit();
      const isRepo = await this.git.checkIsRepo();
      
      if (isRepo) {
        const log = await this.git.log({ maxCount: 1 });
        if (log.latest) {
          this.lastCommitHash = log.latest.hash;
        }
        console.log('Git integration enabled');
      } else {
        console.log('Not a git repository, git integration disabled');
        this.git = null;
      }
    } catch (error) {
      console.error('Failed to initialize git:', error);
      this.git = null;
    }
  }

  private async startFileWatcher(): Promise<void> {
    this.watcher = chokidar.watch(this.config.watchPaths, {
      ignored: this.config.ignorePatterns,
      persistent: true,
      ignoreInitial: false,
      awaitWriteFinish: {
        stabilityThreshold: 2000,
        pollInterval: 100,
      },
    });

    this.watcher
      .on('add', (filePath) => this.handleFileChange('create', filePath))
      .on('change', (filePath) => this.handleFileChange('modify', filePath))
      .on('unlink', (filePath) => this.handleFileChange('delete', filePath));
  }

  private async handleFileChange(changeType: 'create' | 'modify' | 'delete', filePath: string): Promise<void> {
    try {
      if (!this.isRunning) {
        return;
      }

      const stats = await fs.stat(filePath).catch(() => null);
      if (!stats) {
        return;
      }

      const linesAdded = changeType === 'delete' ? 0 : await this.countLines(filePath);
      const linesDeleted = changeType === 'create' ? 0 : await this.countLines(filePath);

      this.tracker.recordCodeChange(filePath, changeType, linesAdded, linesDeleted);

      console.log(`Recorded ${changeType}: ${filePath} (${linesAdded} lines)`);
    } catch (error) {
      console.error(`Failed to handle file change: ${filePath}`, error);
    }
  }

  private async countLines(filePath: string): Promise<number> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return content.split('\n').length;
    } catch {
      return 0;
    }
  }

  private async startHumanInputWatcher(): Promise<void> {
    if (!this.config.humanInputDetection) {
      return;
    }

    const watcher = chokidar.watch(this.humanInputFile, {
      persistent: true,
      ignoreInitial: true,
    });

    watcher.on('change', async () => {
      await this.processHumanInputFile();
    });

    await this.processHumanInputFile();
  }

  private async processHumanInputFile(): Promise<void> {
    try {
      const content = await fs.readFile(this.humanInputFile, 'utf-8');
      const inputs = JSON.parse(content);

      for (const input of inputs) {
        this.tracker.recordHumanInput(
          input.type,
          input.content,
          input.impact || 'medium'
        );
      }

      await fs.writeFile(this.humanInputFile, '[]', 'utf-8');
      console.log(`Processed ${inputs.length} human inputs`);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        console.error('Failed to process human input file:', error);
      }
    }
  }

  async checkGitChanges(): Promise<void> {
    if (!this.git || !this.isRunning) {
      return;
    }

    try {
      const log = await this.git.log({ maxCount: 1 });
      if (!log.latest || log.latest.hash === this.lastCommitHash) {
        return;
      }

      const diff = await this.git.diffSummary([`${this.lastCommitHash}..HEAD`]);
      this.lastCommitHash = log.latest.hash;

      for (const file of diff.files) {
        const insertions = 'insertions' in file ? file.insertions : 0;
        const deletions = 'deletions' in file ? file.deletions : 0;
        const changeType = deletions > 0 && insertions === 0 ? 'delete' : 
                          insertions > 0 && deletions === 0 ? 'create' : 'modify';
        
        this.tracker.recordCodeChange(
          'file' in file ? file.file : String(file),
          changeType,
          insertions,
          deletions
        );
      }

      console.log(`Synced ${diff.files.length} files from git`);
    } catch (error) {
      console.error('Failed to check git changes:', error);
    }
  }

  async generateReport(options: { format?: 'markdown' | 'json'; language?: 'zh' | 'en' } = {}): Promise<string> {
    const session = this.tracker.getCurrentSession();
    if (!session) {
      throw new Error('No active session');
    }

    const { ReportGenerator } = await import('./report-generator.js');
    const generator = new ReportGenerator();

    return generator.generateReport(session, {
      format: options.format || 'markdown',
      includeCodeStats: true,
      includeHumanInputs: true,
      includeTimeline: true,
      language: options.language || 'zh',
    });
  }

  getTracker(): WorkTracker {
    return this.tracker;
  }

  static async createHumanInputFile(filePath: string = '.agent-human-inputs.json'): Promise<void> {
    try {
      await fs.writeFile(filePath, '[]', 'utf-8');
      console.log(`Created human input file: ${filePath}`);
    } catch (error) {
      console.error('Failed to create human input file:', error);
    }
  }

  private formatDuration(ms: number): string {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    }
    return `${minutes}m ${seconds}s`;
  }
}

export interface HumanInput {
  type: 'instruction' | 'decision' | 'feedback' | 'correction';
  content: string;
  impact?: 'critical' | 'high' | 'medium' | 'low';
}

export async function addHumanInput(input: HumanInput, filePath: string = '.agent-human-inputs.json'): Promise<void> {
  try {
    let inputs: HumanInput[] = [];
    
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      inputs = JSON.parse(content);
    } catch {
      inputs = [];
    }

    inputs.push(input);
    await fs.writeFile(filePath, JSON.stringify(inputs, null, 2), 'utf-8');
    console.log('Human input added');
  } catch (error) {
    console.error('Failed to add human input:', error);
  }
}
