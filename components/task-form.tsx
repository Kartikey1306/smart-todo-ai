"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Sparkles, Plus, Loader2 } from "lucide-react"

interface TaskFormProps {
  onTaskCreated: () => void
  userId: number
}

export function TaskForm({ onTaskCreated, userId }: TaskFormProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState("3")
  const [useAI, setUseAI] = useState(true)
  const [naturalLanguage, setNaturalLanguage] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          title,
          description,
          priority: naturalLanguage ? undefined : Number.parseInt(priority),
          useAI,
          naturalLanguage,
        }),
      })

      if (response.ok) {
        setTitle("")
        setDescription("")
        setPriority("3")
        onTaskCreated()
      }
    } catch (error) {
      console.error("Error creating task:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5" />
          Add New Task
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex items-center space-x-2">
              <Switch id="use-ai" checked={useAI} onCheckedChange={setUseAI} />
              <Label htmlFor="use-ai" className="flex items-center gap-1">
                <Sparkles className="h-4 w-4" />
                AI Suggestions
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Switch id="natural-language" checked={naturalLanguage} onCheckedChange={setNaturalLanguage} />
              <Label htmlFor="natural-language">Natural Language</Label>
            </div>
          </div>

          <div>
            <Input
              placeholder={
                naturalLanguage
                  ? "Describe your task naturally (e.g., 'I need to prepare for the client meeting next Friday')"
                  : "Task title"
              }
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          {!naturalLanguage && (
            <>
              <div>
                <Textarea
                  placeholder="Task description (optional)"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </div>

              {!useAI && (
                <div>
                  <Select value={priority} onValueChange={setPriority}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">
                        <Badge variant="destructive">High Priority</Badge>
                      </SelectItem>
                      <SelectItem value="2">
                        <Badge variant="secondary">Medium Priority</Badge>
                      </SelectItem>
                      <SelectItem value="3">
                        <Badge variant="outline">Low Priority</Badge>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </>
          )}

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {useAI || naturalLanguage ? "AI Processing..." : "Creating..."}
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Add Task
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
