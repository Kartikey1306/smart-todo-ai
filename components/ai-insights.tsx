"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Sparkles, TrendingUp, Lightbulb, Loader2, Plus, Briefcase, Flag, CalendarClock, Info } from "lucide-react"

interface AIInsightsProps {
  userId: number
  onTaskCreated: () => void
}

interface Recommendation {
  title: string
  description: string
  priority: number
  reasoning: string
  contextTags: string[]
}

interface Analysis {
  workloadAssessment: string
  priorityDistribution: string
  schedulingInsights: string
  managementSuggestions: string[]
}

export function AIInsights({ userId, onTaskCreated }: AIInsightsProps) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(true)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(true)
  const [isCreatingTask, setIsCreatingTask] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadAnalysis = async () => {
    setIsLoadingAnalysis(true)
    setError(null)
    try {
      const response = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId }),
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysis(data.analysis)
      } else {
        throw new Error("Failed to load analysis.")
      }
    } catch (error) {
      console.error("Error loading analysis:", error)
      setError("Could not load AI analysis. Please try again later.")
    } finally {
      setIsLoadingAnalysis(false)
    }
  }

  const loadRecommendations = async () => {
    setIsLoadingRecommendations(true)
    try {
      const response = await fetch("/api/ai/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId }),
      })

      if (response.ok) {
        const data = await response.json()
        setRecommendations(data.recommendations)
      } else {
        throw new Error("Failed to load recommendations.")
      }
    } catch (error) {
      console.error("Error loading recommendations:", error)
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  const createTaskFromRecommendation = async (recommendation: Recommendation, index: number) => {
    setIsCreatingTask(index)
    try {
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          title: recommendation.title,
          description: recommendation.description,
          priority: recommendation.priority,
          useAI: false, // The recommendation is already AI-driven
          context_tags: recommendation.contextTags,
        }),
      })

      if (response.ok) {
        onTaskCreated()
        setRecommendations((prev) => prev.filter((_, i) => i !== index))
      }
    } catch (error) {
      console.error("Error creating task:", error)
    } finally {
      setIsCreatingTask(null)
    }
  }

  const getPriorityBadge = (priority: number) => {
    const variants = {
      1: { variant: "destructive" as const, label: "High" },
      2: { variant: "secondary" as const, label: "Medium" },
      3: { variant: "outline" as const, label: "Low" },
    }
    return variants[priority as keyof typeof variants]
  }

  useEffect(() => {
    loadAnalysis()
    loadRecommendations()
  }, [userId])

  const renderAnalysisContent = () => {
    if (isLoadingAnalysis) {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          Analyzing your tasks...
        </div>
      )
    }

    if (error) {
      return (
        <div className="text-center py-8 text-red-600">
          <p>{error}</p>
        </div>
      )
    }

    if (!analysis) {
      return (
        <div className="text-center py-8">
          <Info className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">No analysis available yet.</p>
          <p className="text-xs text-muted-foreground mt-1">Add more tasks or context for the AI to analyze.</p>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Workload</CardTitle>
              <Briefcase className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{analysis.workloadAssessment}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Priorities</CardTitle>
              <Flag className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{analysis.priorityDistribution}</p>
            </CardContent>
          </Card>
        </div>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduling Insights</CardTitle>
            <CalendarClock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{analysis.schedulingInsights}</p>
          </CardContent>
        </Card>
        <div>
          <h4 className="text-sm font-medium mb-2">Management Suggestions</h4>
          <ul className="space-y-2 list-disc list-inside text-sm text-muted-foreground">
            {analysis.managementSuggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      </div>
    )
  }

  const renderRecommendationsContent = () => {
    if (isLoadingRecommendations) {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          Getting recommendations...
        </div>
      )
    }

    if (recommendations.length > 0) {
      return (
        <div className="space-y-4">
          {recommendations.map((rec, index) => {
            const priorityBadge = getPriorityBadge(rec.priority)
            return (
              <div key={index} className="border rounded-lg p-4 bg-background">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h4 className="font-medium">{rec.title}</h4>
                      <Badge variant={priorityBadge.variant}>{priorityBadge.label}</Badge>
                    </div>

                    <p className="text-sm text-muted-foreground mb-2">{rec.description}</p>

                    <p className="text-xs text-muted-foreground mb-3">
                      <strong>AI Reasoning:</strong> {rec.reasoning}
                    </p>

                    {rec.contextTags && rec.contextTags.length > 0 && (
                      <div className="flex gap-1 flex-wrap">
                        {rec.contextTags.map((tag, tagIndex) => (
                          <Badge key={tagIndex} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <Button
                    onClick={() => createTaskFromRecommendation(rec, index)}
                    size="sm"
                    disabled={isCreatingTask === index}
                  >
                    {isCreatingTask === index ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-1" />
                        Add Task
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      )
    }

    return (
      <div className="text-center py-8">
        <Info className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
        <p className="text-muted-foreground">No new recommendations right now.</p>
        <p className="text-xs text-muted-foreground mt-1">Add more context to discover new tasks.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            AI Task Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderAnalysisContent()}
          <Button
            onClick={loadAnalysis}
            variant="outline"
            size="sm"
            className="mt-4 bg-transparent"
            disabled={isLoadingAnalysis}
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Refresh Analysis
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            AI Task Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderRecommendationsContent()}
          <Button
            onClick={loadRecommendations}
            variant="outline"
            size="sm"
            className="mt-4 bg-transparent"
            disabled={isLoadingRecommendations}
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Refresh Recommendations
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
