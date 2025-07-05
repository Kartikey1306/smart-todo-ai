"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TaskForm } from "@/components/task-form"
import { TaskList } from "@/components/task-list"
import { ContextManager } from "@/components/context-manager"
import { AIInsights } from "@/components/ai-insights"
import { DashboardStats } from "@/components/dashboard-stats"
import { Brain, CheckSquare, MessageSquare, BarChart3 } from "lucide-react"
import type { Task, ContextEntry } from "@/lib/db"

export default function HomePage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [contextEntries, setContextEntries] = useState<ContextEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const userId = 1

  const loadTasks = async () => {
    try {
      const response = await fetch(`/api/tasks?userId=${userId}`)
      if (response.ok) {
        const data = await response.json()
        setTasks(data.tasks)
      }
    } catch (error) {
      console.error("Error loading tasks:", error)
    }
  }

  const loadContextEntries = async () => {
    try {
      const response = await fetch(`/api/context?userId=${userId}`)
      if (response.ok) {
        const data = await response.json()
        setContextEntries(data.contextEntries)
      }
    } catch (error) {
      console.error("Error loading context:", error)
    }
  }

  const handleTaskUpdate = async (id: number, updates: Partial<Task>) => {
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      })

      if (response.ok) {
        await loadTasks()
      }
    } catch (error) {
      console.error("Error updating task:", error)
    }
  }

  const handleTaskDelete = async (id: number) => {
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        await loadTasks()
      }
    } catch (error) {
      console.error("Error deleting task:", error)
    }
  }

  const handleDataRefresh = async () => {
    await Promise.all([loadTasks(), loadContextEntries()])
  }

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      await Promise.all([loadTasks(), loadContextEntries()])
      setIsLoading(false)
    }

    loadData()
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your smart todo list...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Smart Todo List</h1>
          <p className="text-gray-600">
            AI-powered task management with intelligent prioritization and context-aware recommendations
          </p>
        </div>

        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex items-center gap-2">
              <CheckSquare className="h-4 w-4" />
              Tasks
            </TabsTrigger>
            <TabsTrigger value="context" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Context
            </TabsTrigger>
            <TabsTrigger value="ai-insights" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI Insights
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <DashboardStats tasks={tasks} />
          </TabsContent>

          <TabsContent value="tasks" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <TaskForm onTaskCreated={loadTasks} userId={userId} />
              </div>
              <div className="lg:col-span-2">
                <TaskList tasks={tasks} onTaskUpdate={handleTaskUpdate} onTaskDelete={handleTaskDelete} />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="context" className="space-y-6">
            <ContextManager userId={userId} contextEntries={contextEntries} onContextUpdate={loadContextEntries} />
          </TabsContent>

          <TabsContent value="ai-insights" className="space-y-6">
            <AIInsights userId={userId} onTaskCreated={handleDataRefresh} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
