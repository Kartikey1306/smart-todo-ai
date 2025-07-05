"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Trash2, Calendar, Tag, Sparkles } from "lucide-react"
import type { Task } from "@/lib/db"

interface TaskListProps {
  tasks: Task[]
  onTaskUpdate: (id: number, updates: Partial<Task>) => void
  onTaskDelete: (id: number) => void
}

export function TaskList({ tasks, onTaskUpdate, onTaskDelete }: TaskListProps) {
  const [filter, setFilter] = useState<"all" | "pending" | "in_progress" | "completed">("all")

  const filteredTasks = tasks.filter((task) => {
    if (filter === "all") return true
    return task.status === filter
  })

  const getPriorityBadge = (priority: number, aiSuggested?: number) => {
    const variants = {
      1: { variant: "destructive" as const, label: "High" },
      2: { variant: "secondary" as const, label: "Medium" },
      3: { variant: "outline" as const, label: "Low" },
    }

    const current = variants[priority as keyof typeof variants]
    const suggested = aiSuggested ? variants[aiSuggested as keyof typeof variants] : null

    return (
      <div className="flex items-center gap-2">
        <Badge variant={current.variant}>{current.label}</Badge>
        {suggested && aiSuggested !== priority && (
          <div className="flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-blue-500" />
            <Badge variant={suggested.variant} className="text-xs">
              AI: {suggested.label}
            </Badge>
          </div>
        )}
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const isOverdue = (deadline: string) => {
    return new Date(deadline) < new Date()
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Tasks</h2>
        <Select value={filter} onValueChange={(value: any) => setFilter(value)}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-3">
        {filteredTasks.map((task) => (
          <Card key={task.id} className={`transition-all ${task.status === "completed" ? "opacity-60" : ""}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <Checkbox
                    checked={task.status === "completed"}
                    onCheckedChange={(checked) => {
                      onTaskUpdate(task.id, {
                        status: checked ? "completed" : "pending",
                      })
                    }}
                    className="mt-1"
                  />

                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className={`font-medium ${task.status === "completed" ? "line-through" : ""}`}>
                        {task.title}
                      </h3>
                      {getPriorityBadge(task.priority, task.ai_suggested_priority)}
                    </div>

                    {task.description && <p className="text-sm text-muted-foreground">{task.description}</p>}

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      {task.deadline && (
                        <div
                          className={`flex items-center gap-1 ${isOverdue(task.deadline) && task.status !== "completed" ? "text-red-500" : ""}`}
                        >
                          <Calendar className="h-4 w-4" />
                          {formatDate(task.deadline)}
                          {isOverdue(task.deadline) && task.status !== "completed" && (
                            <Badge variant="destructive" className="ml-1 text-xs">
                              Overdue
                            </Badge>
                          )}
                        </div>
                      )}

                      {task.context_tags && task.context_tags.length > 0 && (
                        <div className="flex items-center gap-1">
                          <Tag className="h-4 w-4" />
                          <div className="flex gap-1">
                            {task.context_tags.slice(0, 3).map((tag, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                            {task.context_tags.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{task.context_tags.length - 3}
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Select value={task.status} onValueChange={(status: any) => onTaskUpdate(task.id, { status })}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onTaskDelete(task.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredTasks.length === 0 && (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-muted-foreground">
                {filter === "all"
                  ? "No tasks yet. Add your first task above!"
                  : `No ${filter.replace("_", " ")} tasks.`}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
