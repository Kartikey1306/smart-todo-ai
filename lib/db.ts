import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export interface User {
  id: number
  email: string
  name: string
  created_at: string
}

export interface Task {
  id: number
  user_id: number
  title: string
  description?: string
  priority: number
  status: "pending" | "in_progress" | "completed"
  deadline?: string
  ai_suggested_priority?: number
  ai_suggested_deadline?: string
  context_tags?: string[]
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface ContextEntry {
  id: number
  user_id: number
  content: string
  entry_type: "message" | "email" | "note" | "meeting"
  entry_date: string
  created_at: string
}

export class Database {
  static async getUser(email: string): Promise<User | null> {
    const users = await sql`SELECT * FROM users WHERE email = ${email} LIMIT 1`
    return users[0] || null
  }

  static async createUser(email: string, name: string): Promise<User> {
    const users = await sql`
      INSERT INTO users (email, name) 
      VALUES (${email}, ${name}) 
      RETURNING *
    `
    return users[0]
  }

  static async getTasks(userId: number): Promise<Task[]> {
    return await sql`
      SELECT * FROM tasks 
      WHERE user_id = ${userId} 
      ORDER BY 
        CASE WHEN status = 'completed' THEN 1 ELSE 0 END,
        priority ASC,
        deadline ASC NULLS LAST,
        created_at DESC
    `
  }

  static async createTask(task: Omit<Task, "id" | "created_at" | "updated_at">): Promise<Task> {
    const tasks = await sql`
      INSERT INTO tasks (user_id, title, description, priority, status, deadline, ai_suggested_priority, ai_suggested_deadline, context_tags)
      VALUES (${task.user_id}, ${task.title}, ${task.description || null}, ${task.priority}, ${task.status}, ${task.deadline || null}, ${task.ai_suggested_priority || null}, ${task.ai_suggested_deadline || null}, ${task.context_tags || null})
      RETURNING *
    `
    return tasks[0]
  }

  static async updateTask(id: number, updates: Partial<Task>): Promise<Task> {
    const setClause = Object.entries(updates)
      .filter(([_, value]) => value !== undefined)
      .map(([key, _]) => `${key} = $${key}`)
      .join(", ")

    const tasks = await sql`
      UPDATE tasks 
      SET ${sql.unsafe(setClause)}, updated_at = CURRENT_TIMESTAMP
      WHERE id = ${id}
      RETURNING *
    `
    return tasks[0]
  }

  static async deleteTask(id: number): Promise<void> {
    await sql`DELETE FROM tasks WHERE id = ${id}`
  }

  static async getContextEntries(userId: number, days = 7): Promise<ContextEntry[]> {
    return await sql`
      SELECT * FROM context_entries 
      WHERE user_id = ${userId} 
      AND entry_date >= CURRENT_DATE - INTERVAL '${days} days'
      ORDER BY entry_date DESC, created_at DESC
    `
  }

  static async createContextEntry(entry: Omit<ContextEntry, "id" | "created_at">): Promise<ContextEntry> {
    const entries = await sql`
      INSERT INTO context_entries (user_id, content, entry_type, entry_date)
      VALUES (${entry.user_id}, ${entry.content}, ${entry.entry_type}, ${entry.entry_date || "CURRENT_DATE"})
      RETURNING *
    `
    return entries[0]
  }
}
