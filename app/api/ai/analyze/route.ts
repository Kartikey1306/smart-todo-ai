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

    const analysis = await AIService.analyzeTasks(tasks, contextEntries)
    return NextResponse.json({ analysis })
  } catch (error) {
    console.error("Error analyzing tasks:", error)
    return NextResponse.json({ error: "Failed to analyze tasks" }, { status: 500 })
  }
}
