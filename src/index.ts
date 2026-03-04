#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { WorkTracker } from './tracker.js';
import { ReportGenerator } from './report-generator.js';
import { ReportOptions } from './types.js';

const tracker = new WorkTracker();
const reportGenerator = new ReportGenerator();

const TOOLS: Tool[] = [
  {
    name: 'start_session',
    description: 'Start a new work session for tracking AI Agent activities',
    inputSchema: {
      type: 'object',
      properties: {
        projectName: {
          type: 'string',
          description: 'Name of the project or task',
        },
      },
      required: ['projectName'],
    },
  },
  {
    name: 'end_session',
    description: 'End the current work session and generate summary',
    inputSchema: {
      type: 'object',
      properties: {
        summary: {
          type: 'string',
          description: 'Optional summary of the work session',
        },
      },
    },
  },
  {
    name: 'start_task',
    description: 'Start tracking a new task within the current session',
    inputSchema: {
      type: 'object',
      properties: {
        description: {
          type: 'string',
          description: 'Description of the task',
        },
      },
      required: ['description'],
    },
  },
  {
    name: 'end_task',
    description: 'Mark the current task as completed or failed',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          enum: ['completed', 'failed'],
          description: 'Status of the task completion',
        },
      },
    },
  },
  {
    name: 'record_code_change',
    description: 'Record a code change (file creation, modification, or deletion)',
    inputSchema: {
      type: 'object',
      properties: {
        filePath: {
          type: 'string',
          description: 'Path to the file that was changed',
        },
        changeType: {
          type: 'string',
          enum: ['create', 'modify', 'delete'],
          description: 'Type of change made to the file',
        },
        linesAdded: {
          type: 'number',
          description: 'Number of lines added',
        },
        linesDeleted: {
          type: 'number',
          description: 'Number of lines deleted',
        },
      },
      required: ['filePath', 'changeType'],
    },
  },
  {
    name: 'record_human_input',
    description: 'Record human guidance, decision, feedback, or correction',
    inputSchema: {
      type: 'object',
      properties: {
        type: {
          type: 'string',
          enum: ['instruction', 'decision', 'feedback', 'correction'],
          description: 'Type of human input',
        },
        content: {
          type: 'string',
          description: 'Content of the human input',
        },
        impact: {
          type: 'string',
          enum: ['critical', 'high', 'medium', 'low'],
          description: 'Impact level of this input on the project',
        },
      },
      required: ['type', 'content'],
    },
  },
  {
    name: 'generate_report',
    description: 'Generate a work report in markdown or JSON format',
    inputSchema: {
      type: 'object',
      properties: {
        format: {
          type: 'string',
          enum: ['markdown', 'json'],
          description: 'Output format for the report',
        },
        includeCodeStats: {
          type: 'boolean',
          description: 'Whether to include detailed code statistics',
        },
        includeHumanInputs: {
          type: 'boolean',
          description: 'Whether to include detailed human input records',
        },
        includeTimeline: {
          type: 'boolean',
          description: 'Whether to include timeline information',
        },
        language: {
          type: 'string',
          enum: ['zh', 'en'],
          description: 'Language for the report (zh for Chinese, en for English)',
        },
      },
    },
  },
  {
    name: 'get_session_status',
    description: 'Get the current status of the work session',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
];

const server = new Server(
  {
    name: 'agent-report-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: TOOLS,
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'start_session': {
        const { projectName } = args as { projectName: string };
        const session = tracker.startSession(projectName);
        return {
          content: [
            {
              type: 'text',
              text: `Work session started for project: ${projectName}\nSession ID: ${session.id}\nStart time: ${session.startTime.toISOString()}`,
            },
          ],
        };
      }

      case 'end_session': {
        const { summary } = args as { summary?: string };
        const session = tracker.endSession(summary);
        if (!session) {
          return {
            content: [
              {
                type: 'text',
                text: 'No active session to end.',
              },
            ],
            isError: true,
          };
        }
        return {
          content: [
            {
              type: 'text',
              text: `Work session ended for project: ${session.projectName}\nSession ID: ${session.id}\nDuration: ${session.endTime ? (session.endTime.getTime() - session.startTime.getTime()) / 1000 : 0} seconds\nTasks completed: ${session.tasks.filter(t => t.status === 'completed').length}/${session.tasks.length}`,
            },
          ],
        };
      }

      case 'start_task': {
        const { description } = args as { description: string };
        const task = tracker.startTask(description);
        return {
          content: [
            {
              type: 'text',
              text: `Task started: ${description}\nTask ID: ${task.id}\nStart time: ${task.startTime.toISOString()}`,
            },
          ],
        };
      }

      case 'end_task': {
        const { status = 'completed' } = args as { status?: 'completed' | 'failed' };
        const task = tracker.endTask(status);
        if (!task) {
          return {
            content: [
              {
                type: 'text',
                text: 'No active task to end.',
              },
            ],
            isError: true,
          };
        }
        return {
          content: [
            {
              type: 'text',
              text: `Task ended: ${task.description}\nStatus: ${status}\nDuration: ${task.endTime ? (task.endTime.getTime() - task.startTime.getTime()) / 1000 : 0} seconds`,
            },
          ],
        };
      }

      case 'record_code_change': {
        const { filePath, changeType, linesAdded = 0, linesDeleted = 0 } = args as {
          filePath: string;
          changeType: 'create' | 'modify' | 'delete';
          linesAdded?: number;
          linesDeleted?: number;
        };
        const change = tracker.recordCodeChange(filePath, changeType, linesAdded, linesDeleted);
        return {
          content: [
            {
              type: 'text',
              text: `Code change recorded: ${changeType} ${filePath}\nLines added: ${linesAdded}, Lines deleted: ${linesDeleted}\nTimestamp: ${change.timestamp.toISOString()}`,
            },
          ],
        };
      }

      case 'record_human_input': {
        const { type, content: inputContent, impact = 'medium' } = args as {
          type: 'instruction' | 'decision' | 'feedback' | 'correction';
          content: string;
          impact?: 'critical' | 'high' | 'medium' | 'low';
        };
        const input = tracker.recordHumanInput(type, inputContent, impact);
        return {
          content: [
            {
              type: 'text',
              text: `Human input recorded: ${type} (${impact})\nContent: ${inputContent}\nTimestamp: ${input.timestamp.toISOString()}`,
            },
          ],
        };
      }

      case 'generate_report': {
        const session = tracker.getCurrentSession();
        if (!session) {
          return {
            content: [
              {
                type: 'text',
                text: 'No active session. Start a session first using start_session.',
              },
            ],
            isError: true,
          };
        }

        const options: ReportOptions = {
          format: (args?.format as 'markdown' | 'json') || 'markdown',
          includeCodeStats: args?.includeCodeStats !== false,
          includeHumanInputs: args?.includeHumanInputs !== false,
          includeTimeline: args?.includeTimeline !== false,
          language: (args?.language as 'zh' | 'en') || 'zh',
        };

        const report = reportGenerator.generateReport(session, options);
        return {
          content: [
            {
              type: 'text',
              text: report,
            },
          ],
        };
      }

      case 'get_session_status': {
        const session = tracker.getCurrentSession();
        const task = tracker.getCurrentTask();
        
        if (!session) {
          return {
            content: [
              {
                type: 'text',
                text: 'No active session.',
              },
            ],
          };
        }

        const duration = Date.now() - session.startTime.getTime();
        const totalCodeLines = session.tasks.reduce((sum, t) => 
          sum + t.codeChanges.reduce((csum, c) => csum + c.linesAdded + c.linesDeleted, 0), 0);
        const totalFiles = new Set(session.tasks.flatMap(t => t.codeChanges.map(c => c.filePath))).size;
        const humanInputs = session.tasks.reduce((sum, t) => sum + t.humanInputs.length, 0);

        return {
          content: [
            {
              type: 'text',
              text: `Session Status:
Project: ${session.projectName}
Session ID: ${session.id}
Started: ${session.startTime.toISOString()}
Duration: ${Math.floor(duration / 1000)} seconds
Tasks: ${session.tasks.length} (${session.tasks.filter(t => t.status === 'completed').length} completed)
Current Task: ${task ? task.description : 'None'}
Code Changes: ${totalCodeLines} lines across ${totalFiles} files
Human Inputs: ${humanInputs}`,
            },
          ],
        };
      }

      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Agent Report MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
