import { type NextRequest, NextResponse } from "next/server"
import { Database } from "@/lib/db"

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const body = await request.json()
    const taskId = Number.parseInt(params.id)

    const updates: any = {}
    if (body.title !== undefined) updates.title = body.title
    if (body.description !== undefined) updates.description = body.description
    if (body.priority !== undefined) updates.priority = body.priority
    if (body.status !== undefined) {
      updates.status = body.status
      if (body.status === "completed") {
        updates.completed_at = new Date().toISOString()
      }
    }
    if (body.deadline !== undefined) updates.deadline = body.deadline

    const task = await Database.updateTask(taskId, updates)
    return NextResponse.json({ task })
  } catch (error) {
    console.error("Error updating task:", error)
    return NextResponse.json({ error: "Failed to update task" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const taskId = Number.parseInt(params.id)
    await Database.deleteTask(taskId)
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error deleting task:", error)
    return NextResponse.json({ error: "Failed to delete task" }, { status: 500 })
  }
}
