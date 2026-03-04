import { WorkSession, ReportData, ReportOptions, HumanInput } from './types.js';

export class ReportGenerator {
  generateReport(session: WorkSession, options: ReportOptions): string {
    const data = this.prepareData(session);
    
    if (options.format === 'json') {
      return JSON.stringify(data, null, 2);
    }
    
    return this.generateMarkdown(data, options);
  }

  private prepareData(session: WorkSession): ReportData {
    const totalDuration = session.endTime 
      ? session.endTime.getTime() - session.startTime.getTime()
      : Date.now() - session.startTime.getTime();
    
    let totalCodeLines = 0;
    let totalFilesChanged = new Set<string>();
    let humanInputCount = 0;
    const criticalDecisions: HumanInput[] = [];
    
    for (const task of session.tasks) {
      for (const change of task.codeChanges) {
        totalCodeLines += change.linesAdded + change.linesDeleted;
        totalFilesChanged.add(change.filePath);
      }
      humanInputCount += task.humanInputs.length;
      
      for (const input of task.humanInputs) {
        if (input.impact === 'critical' || input.impact === 'high') {
          criticalDecisions.push(input);
        }
      }
    }
    
    return {
      session,
      totalDuration,
      totalCodeLines,
      totalFilesChanged: totalFilesChanged.size,
      humanInputCount,
      criticalDecisions,
      generatedAt: new Date(),
    };
  }

  private generateMarkdown(data: ReportData, options: ReportOptions): string {
    const { session, totalDuration, totalCodeLines, totalFilesChanged, humanInputCount, criticalDecisions } = data;
    const isZh = options.language === 'zh';
    
    const formatDuration = (ms: number): string => {
      const hours = Math.floor(ms / 3600000);
      const minutes = Math.floor((ms % 3600000) / 60000);
      if (hours > 0) {
        return isZh ? `${hours}小时${minutes}分钟` : `${hours}h ${minutes}m`;
      }
      return isZh ? `${minutes}分钟` : `${minutes}m`;
    };
    
    const formatTime = (date: Date): string => {
      return date.toLocaleString(isZh ? 'zh-CN' : 'en-US');
    };

    let report = '';
    
    // Header
    report += `# ${isZh ? 'AI Agent 工作汇报' : 'AI Agent Work Report'}\n\n`;
    report += `> **${isZh ? '项目' : 'Project'}:** ${session.projectName}  \n`;
    report += `> **${isZh ? '汇报时间' : 'Report Time'}:** ${formatTime(data.generatedAt)}  \n`;
    report += `> **${isZh ? '工作时段' : 'Work Period'}:** ${formatTime(session.startTime)} - ${session.endTime ? formatTime(session.endTime) : (isZh ? '进行中' : 'Ongoing')}\n\n`;
    
    // Executive Summary
    report += `## ${isZh ? '📊 执行摘要' : '📊 Executive Summary'}\n\n`;
    report += `${isZh ? '本次工作中，AI Agent 与人类紧密协作，高效完成了既定目标。' : 'In this work session, AI Agent collaborated closely with humans to efficiently achieve the set objectives.'}\n\n`;
    
    // Key Metrics
    report += `## ${isZh ? '📈 关键指标' : '📈 Key Metrics'}\n\n`;
    report += `| ${isZh ? '指标' : 'Metric'} | ${isZh ? '数值' : 'Value'} |\n`;
    report += `|------|------|\n`;
    report += `| ${isZh ? '工作时长' : 'Duration'} | ${formatDuration(totalDuration)} |\n`;
    report += `| ${isZh ? '完成任务' : 'Tasks Completed'} | ${session.tasks.filter(t => t.status === 'completed').length}/${session.tasks.length} |\n`;
    report += `| ${isZh ? '代码变更' : 'Code Changes'} | ${totalCodeLines} ${isZh ? '行' : 'lines'} |\n`;
    report += `| ${isZh ? '文件变动' : 'Files Changed'} | ${totalFilesChanged} ${isZh ? '个' : 'files'} |\n`;
    report += `| ${isZh ? '人工介入' : 'Human Inputs'} | ${humanInputCount} ${isZh ? '次' : 'times'} |\n`;
    report += `| ${isZh ? '关键决策' : 'Critical Decisions'} | ${criticalDecisions.length} |\n\n`;
    
    // Work Content
    report += `## ${isZh ? '📝 工作内容' : '📝 Work Content'}\n\n`;
    
    if (session.summary) {
      report += `### ${isZh ? '工作概述' : 'Work Overview'}\n\n`;
      report += `${session.summary}\n\n`;
    }
    
    for (let i = 0; i < session.tasks.length; i++) {
      const task = session.tasks[i];
      const taskDuration = task.endTime 
        ? task.endTime.getTime() - task.startTime.getTime()
        : Date.now() - task.startTime.getTime();
      
      report += `### ${isZh ? '任务' : 'Task'} ${i + 1}: ${task.description}\n\n`;
      report += `- **${isZh ? '状态' : 'Status'}:** ${this.getStatusEmoji(task.status)} ${this.formatStatus(task.status, isZh)}  \n`;
      report += `- **${isZh ? '耗时' : 'Duration'}:** ${formatDuration(taskDuration)}  \n`;
      report += `- **${isZh ? '代码变更' : 'Code Changes'}:** ${task.codeChanges.reduce((sum, c) => sum + c.linesAdded + c.linesDeleted, 0)} ${isZh ? '行' : 'lines'}  \n`;
      report += `- **${isZh ? '人工指导' : 'Human Guidance'}:** ${task.humanInputs.length} ${isZh ? '次' : 'times'}\n\n`;
      
      if (options.includeHumanInputs && task.humanInputs.length > 0) {
        report += `#### ${isZh ? '人工指导详情' : 'Human Guidance Details'}\n\n`;
        for (const input of task.humanInputs) {
          report += `- **${this.getInputTypeLabel(input.type, isZh)}** (${this.getImpactLabel(input.impact, isZh)}): ${input.content}\n`;
        }
        report += '\n';
      }
    }
    
    // Human-AI Collaboration
    report += `## ${isZh ? '🤝 人机协作亮点' : '🤝 Human-AI Collaboration Highlights'}\n\n`;
    
    if (criticalDecisions.length > 0) {
      report += `### ${isZh ? '关键决策点' : 'Key Decision Points'}\n\n`;
      report += `${isZh ? '以下人类指导对项目成功起到了决定性作用：' : 'The following human guidance played a decisive role in project success:'}\n\n`;
      for (const decision of criticalDecisions) {
        report += `- **${this.getInputTypeLabel(decision.type, isZh)}**: ${decision.content}\n`;
      }
      report += '\n';
    }
    
    report += `### ${isZh ? '协作总结' : 'Collaboration Summary'}\n\n`;
    report += `${isZh ? 
      `在整个工作过程中，**AI Agent 展现了高效的代码生成和问题解决能力**，同时**人类的战略指导和关键决策确保了方向的正确性**。\n\n` +
      `具体体现：\n` +
      `- AI Agent 自主完成了 ${session.tasks.filter(t => t.status === 'completed').length} 个任务，生成 ${totalCodeLines} 行高质量代码\n` +
      `- 人类提供 ${humanInputCount} 次精准指导，其中 ${criticalDecisions.length} 次关键决策直接影响项目走向\n` +
      `- 人机协作模式显著提升了开发效率，实现了 1+1>2 的效果\n` :
      
      `Throughout the work process, **AI Agent demonstrated efficient code generation and problem-solving capabilities**, while **human strategic guidance and key decisions ensured the correct direction**.\n\n` +
      `Key highlights:\n` +
      `- AI Agent independently completed ${session.tasks.filter(t => t.status === 'completed').length} tasks, generating ${totalCodeLines} lines of high-quality code\n` +
      `- Humans provided ${humanInputCount} precise guidance inputs, with ${criticalDecisions.length} critical decisions directly impacting project direction\n` +
      `- The human-AI collaboration model significantly improved development efficiency, achieving a 1+1>2 effect\n`
    }\n`;
    
    // Conclusion
    report += `## ${isZh ? '✅ 总结' : '✅ Conclusion'}\n\n`;
    report += `${isZh ? 
      `本次工作充分展示了 AI Agent 在现代软件开发中的价值。通过人机协作模式，我们不仅提高了开发效率，更确保了代码质量和业务目标的达成。**AI Agent 是强大的工具，而人类的创造力和判断力仍是不可替代的核心竞争力。**` :
      `This work fully demonstrated the value of AI Agent in modern software development. Through the human-AI collaboration model, we not only improved development efficiency but also ensured code quality and business objectives. **AI Agent is a powerful tool, while human creativity and judgment remain irreplaceable core competencies.**`
    }\n\n`;
    
    report += `---\n\n`;
    report += `*${isZh ? '本报告由 AI Agent Report MCP 工具自动生成' : 'This report was automatically generated by AI Agent Report MCP Tool'}*\n`;
    
    return report;
  }

  private getStatusEmoji(status: string): string {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'failed': return '❌';
      default: return '⏳';
    }
  }

  private formatStatus(status: string, isZh: boolean): string {
    if (isZh) {
      switch (status) {
        case 'completed': return '已完成';
        case 'in_progress': return '进行中';
        case 'failed': return '失败';
        default: return '未知';
      }
    }
    switch (status) {
      case 'completed': return 'Completed';
      case 'in_progress': return 'In Progress';
      case 'failed': return 'Failed';
      default: return 'Unknown';
    }
  }

  private getInputTypeLabel(type: string, isZh: boolean): string {
    if (isZh) {
      switch (type) {
        case 'instruction': return '指令';
        case 'decision': return '决策';
        case 'feedback': return '反馈';
        case 'correction': return '纠正';
        default: return type;
      }
    }
    switch (type) {
      case 'instruction': return 'Instruction';
      case 'decision': return 'Decision';
      case 'feedback': return 'Feedback';
      case 'correction': return 'Correction';
      default: return type;
    }
  }

  private getImpactLabel(impact: string, isZh: boolean): string {
    if (isZh) {
      switch (impact) {
        case 'critical': return '关键';
        case 'high': return '高';
        case 'medium': return '中';
        case 'low': return '低';
        default: return impact;
      }
    }
    switch (impact) {
      case 'critical': return 'Critical';
      case 'high': return 'High';
      case 'medium': return 'Medium';
      case 'low': return 'Low';
      default: return impact;
    }
  }
}
