import { type NextRequest, NextResponse } from "next/server"
import { Database } from "@/lib/db"
import { AIService } from "@/lib/ai-service"

export async function POST(request: NextRequest) {
  try {
    const { userId } = await request.json()

    const id = Number(userId)
    if (!userId || Number.isNaN(id)) {
      return NextResponse.json({ error: "Valid userId required" }, { status: 400 })
    }

    const [tasks, contextEntries] = await Promise.all([Database.getTasks(id), Database.getContextEntries(id)])

    const recommendations = await AIService.recommendTasks(contextEntries, tasks)
    return NextResponse.json({ recommendations })
  } catch (error) {
    console.error("Error getting recommendations:", error)
    return NextResponse.json({ error: "Failed to get recommendations" }, { status: 500 })
  }
}
