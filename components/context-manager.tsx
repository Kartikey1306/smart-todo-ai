"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Mail, FileText, Users, Plus, Loader2 } from "lucide-react"
import type { ContextEntry } from "@/lib/db"

interface ContextManagerProps {
  userId: number
  contextEntries: ContextEntry[]
  onContextUpdate: () => void
}

export function ContextManager({ userId, contextEntries, onContextUpdate }: ContextManagerProps) {
  const [content, setContent] = useState("")
  const [entryType, setEntryType] = useState<"message" | "email" | "note" | "meeting">("note")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch("/api/context", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          content,
          entryType,
        }),
      })

      if (response.ok) {
        setContent("")
        onContextUpdate()
      }
    } catch (error) {
      console.error("Error adding context:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case "message":
        return <MessageSquare className="h-4 w-4" />
      case "email":
        return <Mail className="h-4 w-4" />
      case "note":
        return <FileText className="h-4 w-4" />
      case "meeting":
        return <Users className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "message":
        return "bg-blue-100 text-blue-800"
      case "email":
        return "bg-green-100 text-green-800"
      case "note":
        return "bg-yellow-100 text-yellow-800"
      case "meeting":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add Daily Context
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Select value={entryType} onValueChange={(value: any) => setEntryType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="note">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Note
                    </div>
                  </SelectItem>
                  <SelectItem value="message">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      Message
                    </div>
                  </SelectItem>
                  <SelectItem value="email">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email
                    </div>
                  </SelectItem>
                  <SelectItem value="meeting">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      Meeting
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Textarea
                placeholder="Enter your daily context (messages, emails, meeting notes, etc.)"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={4}
                required
              />
            </div>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Context
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Context</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {contextEntries.slice(0, 10).map((entry) => (
              <div key={entry.id} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <Badge className={getTypeColor(entry.entry_type)}>
                    {getIcon(entry.entry_type)}
                    <span className="ml-1 capitalize">{entry.entry_type}</span>
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {new Date(entry.entry_date).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm">{entry.content}</p>
              </div>
            ))}

            {contextEntries.length === 0 && (
              <p className="text-center text-muted-foreground py-4">
                No context entries yet. Add your daily context above to help AI provide better task suggestions.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
