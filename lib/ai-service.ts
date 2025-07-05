import { generateObject } from "ai"
import { openai } from "@ai-sdk/openai"
import { z } from "zod"
import type { Task, ContextEntry } from "./db"

const TaskSuggestionSchema = z.object({
  priority: z.number().min(1).max(3).describe("Priority level: 1=High, 2=Medium, 3=Low"),
  deadline: z.string().optional().describe("Suggested deadline in ISO format"),
  reasoning: z.string().describe("Explanation for the priority and deadline suggestion"),
  contextTags: z.array(z.string()).describe("Relevant context tags for this task"),
})

const TaskRecommendationsSchema = z.object({
  recommendations: z
    .array(
      z.object({
        title: z.string().describe("Recommended task title"),
        description: z.string().describe("Task description"),
        priority: z.number().min(1).max(3),
        reasoning: z.string().describe("Why this task is recommended"),
        contextTags: z.array(z.string()),
      }),
    )
    .describe("List of recommended tasks based on context"),
})

const TaskAnalysisSchema = z.object({
  workloadAssessment: z
    .string()
    .describe("A brief assessment of the user's current workload (e.g., light, manageable, heavy)."),
  priorityDistribution: z
    .string()
    .describe("An analysis of how tasks are distributed across different priority levels."),
  schedulingInsights: z
    .string()
    .describe("Comments on potential scheduling conflicts, bottlenecks, or opportunities based on deadlines."),
  managementSuggestions: z
    .array(z.string())
    .describe("A list of 2-3 actionable suggestions for better task management."),
})

export class AIService {
  static async analyzeTasks(tasks: Task[], contextEntries: ContextEntry[]) {
    const contextSummary = contextEntries.map((entry) => `${entry.entry_type}: ${entry.content}`).join("\n")

    const taskList = tasks
      .filter((task) => task.status !== "completed")
      .map((task) => `${task.title} (Priority: ${task.priority}, Deadline: ${task.deadline || "None"})`)
      .join("\n")

    if (!taskList && !contextSummary) {
      return null
    }

    const { object } = await generateObject({
      model: openai("gpt-4o"),
      system: `You are an AI task management assistant. Analyze the user's current tasks and recent context to provide structured insights about their workload, priorities, and time management. Be concise, helpful, and encouraging.`,
      prompt: `
        Current Tasks:
        ${taskList || "No active tasks."}

        Recent Context (last 7 days):
        ${contextSummary || "No recent context."}

        Provide a structured analysis covering:
        1. A workload assessment (e.g., "Your workload appears manageable this week.")
        2. A summary of priority distribution (e.g., "You have a good balance of priorities, with a few high-priority items.")
        3. Any scheduling insights or potential conflicts.
        4. 2-3 actionable management suggestions.
      `,
      schema: TaskAnalysisSchema,
    })

    return object
  }

  static async suggestTaskPriority(title: string, description: string, contextEntries: ContextEntry[]) {
    const contextSummary = contextEntries
      .slice(0, 10) // Last 10 context entries
      .map((entry) => `${entry.entry_type}: ${entry.content}`)
      .join("\n")

    const { object } = await generateObject({
      model: openai("gpt-4o"),
      system: `You are an AI task prioritization assistant. Based on the task details and user's recent context, suggest appropriate priority level and deadline.

      Priority levels:
      1 = High (urgent, important, time-sensitive)
      2 = Medium (important but not urgent, or urgent but not critical)
      3 = Low (nice to have, can be delayed)

      Consider factors like:
      - Deadlines mentioned in context
      - Work vs personal tasks
      - Dependencies on other people
      - Impact of delay`,
      prompt: `
        Task: ${title}
        Description: ${description}

        Recent Context:
        ${contextSummary}

        Suggest priority level, deadline, and provide reasoning.
      `,
      schema: TaskSuggestionSchema,
    })

    return object
  }

  static async recommendTasks(contextEntries: ContextEntry[], existingTasks: Task[]) {
    const contextSummary = contextEntries.map((entry) => `${entry.entry_type}: ${entry.content}`).join("\n")

    if (!contextSummary) {
      return []
    }

    const existingTaskTitles = existingTasks.map((task) => task.title).join("\n")

    const { object } = await generateObject({
      model: openai("gpt-4o"),
      system: `You are an AI task recommendation assistant. Based on the user's recent context (messages, emails, notes, meetings), suggest new tasks they might need to add to their todo list.

      Focus on:
      - Action items mentioned in context
      - Follow-ups needed
      - Deadlines or commitments mentioned
      - Preparation tasks for upcoming events

      Avoid suggesting tasks that already exist. If no new tasks can be suggested, return an empty array.`,
      prompt: `
        Recent Context:
        ${contextSummary}

        Existing Tasks (don't duplicate):
        ${existingTaskTitles}

        Suggest 3-5 new tasks based on the context.
      `,
      schema: TaskRecommendationsSchema,
    })

    return object.recommendations
  }

  static async parseNaturalLanguageTask(input: string, contextEntries: ContextEntry[]) {
    const contextSummary = contextEntries
      .slice(0, 5)
      .map((entry) => `${entry.entry_type}: ${entry.content}`)
      .join("\n")

    const { object } = await generateObject({
      model: openai("gpt-4o"),
      system: `You are an AI task parser. Convert natural language input into structured task data.

      Extract:
      - Clear, actionable title
      - Detailed description
      - Priority based on urgency/importance cues
      - Deadline if mentioned or implied
      - Relevant context tags`,
      prompt: `
        User input: "${input}"

        Recent context for reference:
        ${contextSummary}

        Parse this into a structured task.
      `,
      schema: z.object({
        title: z.string().describe("Clear, actionable task title"),
        description: z.string().describe("Detailed task description"),
        priority: z.number().min(1).max(3),
        deadline: z.string().optional().describe("Deadline in ISO format if mentioned"),
        contextTags: z.array(z.string()).describe("Relevant tags"),
      }),
    })

    return object
  }
}
