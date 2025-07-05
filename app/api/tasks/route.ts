import { type NextRequest, NextResponse } from "next/server"
import { Database } from "@/lib/db"
import { AIService } from "@/lib/ai-service"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")

    if (!userId) {
      return NextResponse.json({ error: "User ID required" }, { status: 400 })
    }

    const tasks = await Database.getTasks(Number.parseInt(userId))
    return NextResponse.json({ tasks })
  } catch (error) {
    console.error("Error fetching tasks:", error)
    return NextResponse.json({ error: "Failed to fetch tasks" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, title, description, useAI = false, naturalLanguage = false } = body

    if (!userId || !title) {
      return NextResponse.json({ error: "User ID and title required" }, { status: 400 })
    }

    let taskData = {
      user_id: Number.parseInt(userId),
      title,
      description: description || "",
      priority: 3,
      status: "pending" as const,
      deadline: undefined as string | undefined,
      ai_suggested_priority: undefined as number | undefined,
      ai_suggested_deadline: undefined as string | undefined,
      context_tags: [] as string[],
    }

    if (useAI || naturalLanguage) {
      const contextEntries = await Database.getContextEntries(Number.parseInt(userId))

      if (naturalLanguage) {
        // Parse natural language input
        const parsed = await AIService.parseNaturalLanguageTask(title, contextEntries)
        taskData = {
          ...taskData,
          title: parsed.title,
          description: parsed.description,
          priority: parsed.priority,
          deadline: parsed.deadline,
          context_tags: parsed.contextTags,
        }
      } else {
        // Get AI suggestions for priority and deadline
        const suggestion = await AIService.suggestTaskPriority(title, description, contextEntries)
        taskData.ai_suggested_priority = suggestion.priority
        taskData.ai_suggested_deadline = suggestion.deadline
        taskData.priority = suggestion.priority
        taskData.context_tags = suggestion.contextTags
        if (suggestion.deadline) {
          taskData.deadline = suggestion.deadline
        }
      }
    }

    const task = await Database.createTask(taskData)
    return NextResponse.json({ task })
  } catch (error) {
    console.error("Error creating task:", error)
    return NextResponse.json({ error: "Failed to create task" }, { status: 500 })
  }
}
