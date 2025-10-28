"use client"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Star, ThumbsUp, ThumbsDown, MessageSquare, User, Calendar, ArrowLeft, Filter } from "lucide-react"
import Link from "next/link"

interface Candidate {
  id: string
  name: string
  email: string
  position: string
  experience: string
  skills: string[]
  resumeScore: number
  status: "pending" | "reviewed" | "shortlisted" | "rejected"
  appliedDate: string
}

export default function FeedbackPage() {
  const [candidates] = useState<Candidate[]>([
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.johnson@email.com",
      position: "Senior Developer",
      experience: "5+ years",
      skills: ["React", "Node.js", "TypeScript", "AWS"],
      resumeScore: 92,
      status: "pending",
      appliedDate: "2025-01-15",
    },
    {
      id: "2",
      name: "Michael Chen",
      email: "michael.chen@email.com",
      position: "Senior Developer",
      experience: "4+ years",
      skills: ["Vue.js", "Python", "Docker", "MongoDB"],
      resumeScore: 88,
      status: "reviewed",
      appliedDate: "2025-01-14",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      email: "emily.rodriguez@email.com",
      position: "Senior Developer",
      experience: "6+ years",
      skills: ["Angular", "Java", "Kubernetes", "PostgreSQL"],
      resumeScore: 95,
      status: "shortlisted",
      appliedDate: "2025-01-13",
    },
  ])

  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [feedback, setFeedback] = useState("")
  const [rating, setRating] = useState(0)
  const [filterStatus, setFilterStatus] = useState("all")

  const filteredCandidates = candidates.filter(
    (candidate) => filterStatus === "all" || candidate.status === filterStatus,
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case "shortlisted":
        return "bg-green-500"
      case "reviewed":
        return "bg-blue-500"
      case "rejected":
        return "bg-red-500"
      default:
        return "bg-yellow-500"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "shortlisted":
        return "Shortlisted"
      case "reviewed":
        return "Reviewed"
      case "rejected":
        return "Rejected"
      default:
        return "Pending Review"
    }
  }

  const handleSubmitFeedback = () => {
    // Dummy feedback submission
    console.log("Feedback submitted:", { candidate: selectedCandidate?.id, feedback, rating })
    setFeedback("")
    setRating(0)
    setSelectedCandidate(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-pink-50">
      <div className="container mx-auto p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Button>
              </Link>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Candidate Feedback
              </h1>
            </div>
            <p className="text-muted-foreground">Review candidates and provide detailed feedback</p>
          </div>

          <div className="flex items-center space-x-4">
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-40">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="reviewed">Reviewed</SelectItem>
                <SelectItem value="shortlisted">Shortlisted</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Progress Indicator */}
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Review Progress</h3>
              <Badge variant="outline">
                {candidates.filter((c) => c.status !== "pending").length} / {candidates.length} Reviewed
              </Badge>
            </div>
            <Progress
              value={(candidates.filter((c) => c.status !== "pending").length / candidates.length) * 100}
              className="h-2"
            />
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Candidates List */}
          <div className="lg:col-span-2 space-y-4">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <span>Candidates ({filteredCandidates.length})</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {filteredCandidates.map((candidate) => (
                  <Card
                    key={candidate.id}
                    className={`cursor-pointer transition-all duration-300 hover:shadow-md ${
                      selectedCandidate?.id === candidate.id ? "ring-2 ring-purple-500" : ""
                    }`}
                    onClick={() => setSelectedCandidate(candidate)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4">
                          <Avatar className="h-12 w-12">
                            <AvatarFallback className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                              {candidate.name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div className="space-y-2">
                            <div>
                              <h3 className="font-semibold">{candidate.name}</h3>
                              <p className="text-sm text-muted-foreground">{candidate.email}</p>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                              <span>{candidate.experience}</span>
                              <span>•</span>
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-3 w-3" />
                                <span>{candidate.appliedDate}</span>
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {candidate.skills.slice(0, 3).map((skill) => (
                                <Badge key={skill} variant="secondary" className="text-xs">
                                  {skill}
                                </Badge>
                              ))}
                              {candidate.skills.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{candidate.skills.length - 3} more
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="text-right space-y-2">
                          <Badge className={getStatusColor(candidate.status)}>{getStatusText(candidate.status)}</Badge>
                          <div className="text-sm">
                            <div className="font-semibold text-green-600">{candidate.resumeScore}%</div>
                            <div className="text-xs text-muted-foreground">Match Score</div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Feedback Panel */}
          <div className="space-y-6">
            {selectedCandidate ? (
              <>
                <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <MessageSquare className="h-5 w-5" />
                      <span>Provide Feedback</span>
                    </CardTitle>
                    <CardDescription className="text-purple-100">For {selectedCandidate.name}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-purple-100 mb-2 block">Overall Rating</label>
                      <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`h-6 w-6 cursor-pointer transition-colors ${
                              star <= rating ? "fill-yellow-400 text-yellow-400" : "text-purple-200"
                            }`}
                            onClick={() => setRating(star)}
                          />
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-purple-100 mb-2 block">Detailed Feedback</label>
                      <Textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Share your thoughts about this candidate..."
                        className="bg-white/20 border-purple-300 text-white placeholder:text-purple-200"
                        rows={4}
                      />
                    </div>

                    <div className="flex space-x-2">
                      <Button
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white"
                        onClick={handleSubmitFeedback}
                      >
                        <ThumbsUp className="h-4 w-4 mr-2" />
                        Shortlist
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 bg-red-500 hover:bg-red-600 text-white border-red-400"
                        onClick={handleSubmitFeedback}
                      >
                        <ThumbsDown className="h-4 w-4 mr-2" />
                        Reject
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Candidate Details */}
                <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-lg">Candidate Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-2">Skills</h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedCandidate.skills.map((skill) => (
                          <Badge key={skill} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-2">Experience</h4>
                      <p className="text-sm">{selectedCandidate.experience}</p>
                    </div>

                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-2">Resume Score</h4>
                      <div className="flex items-center space-x-2">
                        <Progress value={selectedCandidate.resumeScore} className="flex-1" />
                        <span className="text-sm font-medium">{selectedCandidate.resumeScore}%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                <CardContent className="p-8 text-center">
                  <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">Select a Candidate</h3>
                  <p className="text-sm text-muted-foreground">
                    Choose a candidate from the list to provide feedback and review their application.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
