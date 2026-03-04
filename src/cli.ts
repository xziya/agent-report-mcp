#!/usr/bin/env node

import { AutoTracker, addHumanInput } from './auto-tracker.js';
import * as fs from 'fs/promises';
import * as path from 'path';

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  switch (command) {
    case 'start':
      await startAutoTracker();
      break;
    case 'report':
      await generateReport();
      break;
    case 'input':
      await addHumanInputCommand();
      break;
    case 'init':
      await initProject();
      break;
    default:
      printUsage();
  }
}

async function startAutoTracker() {
  const projectName = args[1] || 'Auto-tracked Project';
  const watchPaths = args.slice(2).length > 0 ? args.slice(2) : [process.cwd()];

  console.log('Starting AutoTracker...');
  console.log(`Project: ${projectName}`);
  console.log(`Watching: ${watchPaths.join(', ')}`);

  const tracker = new AutoTracker({
    projectName,
    watchPaths,
    autoStartSession: true,
    gitEnabled: true,
    humanInputDetection: true,
  });

  await tracker.start();

  process.on('SIGINT', async () => {
    console.log('\nStopping AutoTracker...');
    await tracker.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\nStopping AutoTracker...');
    await tracker.stop();
    process.exit(0);
  });
}

async function generateReport() {
  const format = args.includes('--json') ? 'json' : 'markdown';
  const language = args.includes('--en') ? 'en' : 'zh';

  try {
    const tracker = new AutoTracker();
    const report = await tracker.generateReport({ format, language });
    console.log(report);
  } catch (error) {
    console.error('Failed to generate report:', error);
    process.exit(1);
  }
}

async function addHumanInputCommand() {
  const type = args[1] as 'instruction' | 'decision' | 'feedback' | 'correction';
  const content = args[2];
  const impact = args[3] as 'critical' | 'high' | 'medium' | 'low' || 'medium';

  if (!type || !content) {
    console.error('Usage: agent-report-mcp input <type> <content> [impact]');
    console.error('Types: instruction, decision, feedback, correction');
    console.error('Impacts: critical, high, medium, low');
    process.exit(1);
  }

  await addHumanInput({ type, content, impact });
}

async function initProject() {
  const humanInputFile = '.agent-human-inputs.json';
  
  try {
    await fs.writeFile(humanInputFile, '[]', 'utf-8');
    console.log(`Created human input file: ${humanInputFile}`);
    console.log('\nYou can now add human inputs by editing this file or using:');
    console.log('  agent-report-mcp input <type> <content> [impact]');
  } catch (error) {
    console.error('Failed to initialize:', error);
    process.exit(1);
  }
}

function printUsage() {
  console.log(`
Agent Report MCP - Auto Tracking CLI

Usage:
  agent-report-mcp start [project-name] [watch-paths...]
    Start automatic tracking of work session
    
  agent-report-mcp report [--json] [--en]
    Generate work report from tracked data
    
  agent-report-mcp input <type> <content> [impact]
    Add a human input to the tracking session
    Types: instruction, decision, feedback, correction
    Impacts: critical, high, medium, low
    
  agent-report-mcp init
    Initialize project for auto-tracking

Examples:
  agent-report-mcp start "My Project" ./src
  agent-report-mcp report
  agent-report-mcp input decision "Use UUID for user IDs" critical
  agent-report-mcp init
  `);
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
