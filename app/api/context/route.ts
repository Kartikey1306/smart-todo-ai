import { type NextRequest, NextResponse } from "next/server"
import { Database } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")
    const days = searchParams.get("days") || "7"

    if (!userId) {
      return NextResponse.json({ error: "User ID required" }, { status: 400 })
    }

    const contextEntries = await Database.getContextEntries(Number.parseInt(userId), Number.parseInt(days))
    return NextResponse.json({ contextEntries })
  } catch (error) {
    console.error("Error fetching context:", error)
    return NextResponse.json({ error: "Failed to fetch context" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, content, entryType, entryDate } = body

    if (!userId || !content || !entryType) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    const contextEntry = await Database.createContextEntry({
      user_id: Number.parseInt(userId),
      content,
      entry_type: entryType,
      entry_date: entryDate || new Date().toISOString().split("T")[0],
    })

    return NextResponse.json({ contextEntry })
  } catch (error) {
    console.error("Error creating context entry:", error)
    return NextResponse.json({ error: "Failed to create context entry" }, { status: 500 })
  }
}
