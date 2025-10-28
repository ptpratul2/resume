"use client"
import { useState, useEffect } from "react"
import type React from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  Briefcase,
  Upload,
  MessageSquare,
  FileText,
  UserCheck,
  Plus,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertCircle,
  Calendar,
  Sparkles,
  TrendingUp,
  Users,
  Target,
  Zap,
} from "lucide-react"
import Link from "next/link"

interface WorkflowStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  status: "completed" | "current" | "pending"
  route?: string
  color: string
}

export default function RecruitmentDashboard() {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const [workflowProgress, setWorkflowProgress] = useState(0)

  const workflowSteps: WorkflowStep[] = [
    {
      id: "job-opening",
      title: "Job Opening",
      description: "Create or select job opening",
      icon: <Briefcase className="h-5 w-5" />,
      status: selectedJobId ? "completed" : "current",
      route: "/create-job",
      color: "from-blue-500 to-indigo-600",
    },
    {
      id: "resume-upload",
      title: "Resume Collection",
      description: "Upload and process resumes",
      icon: <Upload className="h-5 w-5" />,
      status: selectedJobId ? "current" : "pending",
      route: "/upload-resumes",
      color: "from-emerald-500 to-teal-600",
    },
    {
      id: "interview",
      title: "Interview Scheduling",
      description: "Schedule and conduct interviews",
      icon: <Calendar className="h-5 w-5" />,
      status: "pending",
      route: "/interview",
      color: "from-orange-500 to-amber-600",
    },
    {
      id: "feedback",
      title: "Candidate Feedback",
      description: "Review and provide feedback",
      icon: <MessageSquare className="h-5 w-5" />,
      status: "pending",
      route: "/feedback",
      color: "from-purple-500 to-pink-600",
    },
    {
      id: "offer-letter",
      title: "Offer Letter",
      description: "Generate and send offers",
      icon: <FileText className="h-5 w-5" />,
      status: "pending",
      route: "/offer-letter",
      color: "from-emerald-500 to-teal-600",
    },
    {
      id: "appointment",
      title: "Appointment Letter",
      description: "Final appointment process",
      icon: <UserCheck className="h-5 w-5" />,
      status: "pending",
      route: "/appointment",
      color: "from-blue-500 to-indigo-600",
    },
  ]

  useEffect(() => {
    const completedSteps = workflowSteps.filter((step) => step.status === "completed").length
    const progress = (completedSteps / workflowSteps.length) * 100
    setWorkflowProgress(progress)
  }, [selectedJobId])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "current":
        return <Clock className="h-4 w-4 text-blue-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500"
      case "current":
        return "bg-blue-500"
      default:
        return "bg-gray-300"
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto p-8 space-y-8">
        {/* Hero Header */}
        <div className="text-center space-y-6">
          <div className="flex items-center justify-center space-x-3">
            <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Job Management System
            </h1>
          </div>
        </div>

        {/* Progress Overview */}
        <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-2xl flex items-center space-x-2">
                  <TrendingUp className="h-6 w-6 text-blue-600" />
                  <span>Workflow Progress</span>
                </CardTitle>
                <CardDescription className="text-base">
                  Track your recruitment pipeline progress in real-time
                </CardDescription>
              </div>
              <Badge variant="outline" className="text-base font-semibold px-4 py-2">
                {Math.round(workflowProgress)}% Complete
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="relative">
              <Progress value={workflowProgress} className="h-4 bg-gray-100" />
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full opacity-20"></div>
            </div>

            {/* Workflow Steps */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {workflowSteps.map((step, index) => (
                <div key={step.id} className="relative">
                  <Card
                    className={`transition-all duration-500 hover:shadow-lg hover:-translate-y-1 ${step.status === "current"
                        ? "ring-2 ring-blue-500 shadow-lg scale-105"
                        : step.status === "completed"
                          ? "ring-2 ring-green-500 shadow-md"
                          : "hover:shadow-md"
                      }`}
                  >
                    <CardContent className="p-4 text-center space-y-4">
                      <div
                        className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto transition-all duration-300 ${step.status === "completed"
                            ? "bg-green-500 text-white shadow-lg"
                            : step.status === "current"
                              ? `bg-gradient-to-r ${step.color} text-white shadow-lg`
                              : "bg-gray-100 text-gray-500"
                          }`}
                      >
                        {step.status === "completed" ? <CheckCircle className="h-7 w-7" /> : step.icon}
                      </div>
                      <div className="space-y-1">
                        <h3 className="font-semibold text-sm">{step.title}</h3>
                        <p className="text-xs text-muted-foreground leading-tight">{step.description}</p>
                      </div>
                      <div className="flex items-center justify-center">{getStatusIcon(step.status)}</div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Create New Job Opening */}
          <Card className="border-0 shadow-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white hover:shadow-2xl transition-all duration-500 hover:scale-105">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                  <Plus className="h-8 w-8" />
                </div>
                <div className="space-y-1">
                  <CardTitle className="text-2xl">Create New Job Opening</CardTitle>
                  <CardDescription className="text-blue-100 text-base">
                    Start a fresh recruitment process with AI assistance
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <Link href="/create-job">
                <Button className="w-full h-12 text-lg bg-white text-blue-600 hover:bg-blue-50 font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                  Create Job Opening
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Proceed with Existing */}
          <Card className="border-0 shadow-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white hover:shadow-2xl transition-all duration-500 hover:scale-105">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                  <Briefcase className="h-8 w-8" />
                </div>
                <div className="space-y-1">
                  <CardTitle className="text-2xl">Continue Existing Process</CardTitle>
                  <CardDescription className="text-emerald-100 text-base">
                    Resume with ongoing recruitment workflows
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <Button
                className="w-full h-12 text-lg bg-white text-emerald-600 hover:bg-emerald-50 font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                onClick={() => setSelectedJobId("existing-job")}
              >
                Select Existing Job
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        {selectedJobId && (
          <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center space-x-2">
                <Zap className="h-6 w-6 text-yellow-500" />
                <span>Quick Actions</span>
              </CardTitle>
              <CardDescription className="text-base">Jump to any stage of your recruitment process</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {workflowSteps.slice(1).map((step) => (
                  <Link key={step.id} href={step.route || "#"}>
                    <Button
                      variant="outline"
                      className={`w-full h-auto p-6 flex flex-col items-center space-y-3 hover:shadow-lg transition-all duration-300 bg-gradient-to-br ${step.color} hover:text-white group`}
                      disabled={step.status === "pending" && !["resume-upload", "interview"].includes(step.id)}
                    >
                      <div className="p-2 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors">
                        {step.icon}
                      </div>
                      <div className="text-center">
                        <span className="font-medium">{step.title}</span>
                        <p className="text-xs opacity-80 mt-1">{step.description}</p>
                      </div>
                    </Button>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Enhanced Statistics */}
        {/* <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 hover:shadow-xl transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <div className="p-2 bg-blue-500 rounded-lg">
                  <Briefcase className="h-5 w-5 text-white" />
                </div>
                <div className="text-3xl font-bold text-blue-600">12</div>
              </div>
              <div className="text-sm font-medium text-blue-800">Active Jobs</div>
              <div className="text-xs text-blue-600 mt-1">+3 this week</div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-emerald-50 to-emerald-100 hover:shadow-xl transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <div className="p-2 bg-emerald-500 rounded-lg">
                  <Upload className="h-5 w-5 text-white" />
                </div>
                <div className="text-3xl font-bold text-emerald-600">248</div>
              </div>
              <div className="text-sm font-medium text-emerald-800">Resumes Received</div>
              <div className="text-xs text-emerald-600 mt-1">+45 today</div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-amber-50 to-amber-100 hover:shadow-xl transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <div className="p-2 bg-amber-500 rounded-lg">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <div className="text-3xl font-bold text-amber-600">36</div>
              </div>
              <div className="text-sm font-medium text-amber-800">In Review</div>
              <div className="text-xs text-amber-600 mt-1">Processing</div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 hover:shadow-xl transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <div className="p-2 bg-purple-500 rounded-lg">
                  <FileText className="h-5 w-5 text-white" />
                </div>
                <div className="text-3xl font-bold text-purple-600">8</div>
              </div>
              <div className="text-sm font-medium text-purple-800">Offers Sent</div>
              <div className="text-xs text-purple-600 mt-1">Awaiting response</div>
            </CardContent>
          </Card>
        </div> */}

        {/* Feature Highlights */}
        {/* <Card className="border-0 shadow-xl bg-gradient-to-r from-slate-900 to-slate-800 text-white">
          <CardContent className="p-8">
            <div className="text-center space-y-4 mb-8">
              <h2 className="text-3xl font-bold">Why Choose Our Platform?</h2>
              <p className="text-slate-300 text-lg">Experience the future of recruitment with cutting-edge features</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center space-y-3">
                <div className="p-4 bg-white/10 rounded-full w-fit mx-auto">
                  <Sparkles className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-semibold">AI-Powered Matching</h3>
                <p className="text-slate-300">
                  Advanced algorithms match candidates to job requirements with 95% accuracy
                </p>
              </div>

              <div className="text-center space-y-3">
                <div className="p-4 bg-white/10 rounded-full w-fit mx-auto">
                  <TrendingUp className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-semibold">Real-time Analytics</h3>
                <p className="text-slate-300">
                  Track your hiring metrics and optimize your recruitment process continuously
                </p>
              </div>

              <div className="text-center space-y-3">
                <div className="p-4 bg-white/10 rounded-full w-fit mx-auto">
                  <Zap className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-semibold">Lightning Fast</h3>
                <p className="text-slate-300">
                  Reduce time-to-hire by 60% with automated workflows and smart screening
                </p>
              </div>
            </div>
          </CardContent>
        </Card>*/}
      </div>
    </div>
  )
}


