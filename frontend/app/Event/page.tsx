
"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { useRouter } from "next/navigation"
import axios from "axios"
import { API_AUTH, API_BASE_URL } from "../create-job/page"

interface Interviewer {
  name: string
  full_name: string
  email: string
}

interface JobApplicant {
  name: string
  applicant_name: string
  email_id: string
}

interface InterviewRound {
  name: string
  round_name: string
}

export default function EventPage() {
  const router = useRouter()
  const [eventForm, setEventForm] = useState({
    interviewRound: "",
    jobApplicant: "",
    resumeLink: "",
    status: "Pending",
    scheduledOn: "",
    fromTime: "",
    toTime: "",
    interviewers: [] as string[],
    meetingLink: "", // Added for video meeting links (Zoom, Google Meet, etc.)
  })

  const [availableInterviewers, setAvailableInterviewers] = useState<Interviewer[]>([])
  const [jobApplicants, setJobApplicants] = useState<JobApplicant[]>([])
  const [interviewRounds, setInterviewRounds] = useState<InterviewRound[]>([])
  const [isSaving, setIsSaving] = useState(false)

  // Status options from Interview doctype
  const statusOptions = ["Pending", "Under Review", "Cleared", "Rejected"]

  useEffect(() => {
    fetchInterviewers()
    fetchJobApplicants()
    fetchInterviewRounds()
  }, [])

  const fetchInterviewRounds = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/resource/Interview Round?fields=["name","round_name"]&limit_page_length=100`,
        API_AUTH
      )
      
      if (response.data && response.data.data) {
        setInterviewRounds(response.data.data)
        console.log("Fetched interview rounds:", response.data.data)
      }
    } catch (error) {
      console.error("Error fetching interview rounds:", error)
      // Fallback to default rounds if API fails
      setInterviewRounds([
        { name: "First Round", round_name: "First Round" },
        { name: "Second Round", round_name: "Second Round" },
        { name: "Final Round", round_name: "Final Round" },
      ])
    }
  }

  const fetchInterviewers = async () => {
    try {
      // Use new API endpoint that filters users by 'Interviewer' role
      const response = await axios.get(
        `${API_BASE_URL}/api/method/resume.api.interview.get_interviewers`,
        API_AUTH
      )
      
      if (response.data && response.data.message && response.data.message.data) {
        setAvailableInterviewers(response.data.message.data)
        console.log("Fetched interviewers with role:", response.data.message.data)
      }
    } catch (error) {
      console.error("Error fetching interviewers:", error)
      // Fallback to old method if new API fails
      try {
        const fallbackResponse = await axios.get(
          `${API_BASE_URL}/api/resource/User?fields=["name","full_name","email"]&filters=[["enabled","=",1]]&limit_page_length=100`,
          API_AUTH
        )
        if (fallbackResponse.data && fallbackResponse.data.data) {
          const filteredUsers = fallbackResponse.data.data.filter(
            (user: any) => user.name !== "Administrator" && user.name !== "Guest"
          )
          setAvailableInterviewers(filteredUsers)
        }
      } catch (fallbackError) {
        console.error("Fallback also failed:", fallbackError)
      }
    }
  }

  const fetchJobApplicants = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/resource/Job Applicant?fields=["name","applicant_name","email_id"]&limit_page_length=100`,
        API_AUTH
      )
      
      if (response.data && response.data.data) {
        setJobApplicants(response.data.data)
        console.log("Fetched job applicants:", response.data.data)
      }
    } catch (error) {
      console.error("Error fetching job applicants:", error)
    }
  }

  const handleInterviewerToggle = (interviewer: string) => {
    setEventForm((prev) => ({
      ...prev,
      interviewers: prev.interviewers.includes(interviewer)
        ? prev.interviewers.filter((i) => i !== interviewer)
        : [...prev.interviewers, interviewer],
    }))
  }

  const handleSaveEvent = async () => {
    if (!eventForm.interviewRound || !eventForm.jobApplicant || !eventForm.scheduledOn || !eventForm.fromTime || !eventForm.toTime) {
      alert("Please fill all required fields")
      return
    }

    setIsSaving(true)
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/resource/Interview`,
        {
          interview_round: eventForm.interviewRound,
          job_applicant: eventForm.jobApplicant,
          resume_link: eventForm.resumeLink || null,
          status: eventForm.status,
          scheduled_on: eventForm.scheduledOn,
          from_time: eventForm.fromTime,
          to_time: eventForm.toTime,
          meeting_link: eventForm.meetingLink || null, // Add meeting link (Zoom, Google Meet, etc.)
          interview_details: eventForm.interviewers.map(interviewer => ({
            interviewer: interviewer
          }))
        },
        API_AUTH
      )

      if (response.data) {
        alert("Interview created successfully!")
        console.log("Created interview:", response.data)
        router.back()
      }
    } catch (error: any) {
      console.error("Error creating interview:", error)
      const errorMessage = error.response?.data?.exception || error.response?.data?.message || "Failed to create interview"
      alert(errorMessage)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-amber-50">
      <div className="container mx-auto p-8 space-y-8">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={() => router.back()}>
                Back
              </Button>
              <h1 className="text-3xl font-bold">New Interview</h1>
            </div>
          </div>
          <Badge className="bg-yellow-500 text-white px-4 py-2">Not Saved</Badge>
        </div>

        <div className="max-w-4xl">
          <Card className="border-0 shadow-lg bg-white">
            <CardHeader className="border-b">
              <CardTitle>Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Interview Round <span className="text-red-500">*</span></Label>
                  {interviewRounds.length > 0 ? (
                    <Select 
                      value={eventForm.interviewRound} 
                      onValueChange={(value) => setEventForm({ ...eventForm, interviewRound: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select round" />
                      </SelectTrigger>
                      <SelectContent>
                        {interviewRounds.map((round) => (
                          <SelectItem key={round.name} value={round.name}>
                            {round.round_name || round.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input 
                      value={eventForm.interviewRound}
                      onChange={(e) => setEventForm({ ...eventForm, interviewRound: e.target.value })}
                      placeholder="Loading rounds..." 
                    />
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Status <span className="text-red-500">*</span></Label>
                  <Select 
                    value={eventForm.status} 
                    onValueChange={(value) => setEventForm({ ...eventForm, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map((status) => (
                        <SelectItem key={status} value={status}>
                          {status}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Job Applicant <span className="text-red-500">*</span></Label>
                {jobApplicants.length > 0 ? (
                  <Select 
                    value={eventForm.jobApplicant} 
                    onValueChange={(value) => setEventForm({ ...eventForm, jobApplicant: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select applicant" />
                    </SelectTrigger>
                    <SelectContent>
                      {jobApplicants.map((applicant) => (
                        <SelectItem key={applicant.name} value={applicant.name}>
                          {applicant.applicant_name} ({applicant.email_id})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input 
                    value={eventForm.jobApplicant} 
                    onChange={(e) => setEventForm({ ...eventForm, jobApplicant: e.target.value })} 
                    placeholder="Loading applicants..." 
                  />
                )}
              </div>

              <div className="space-y-2">
                <Label>Resume link</Label>
                <Input 
                  type="url" 
                  value={eventForm.resumeLink} 
                  onChange={(e) => setEventForm({ ...eventForm, resumeLink: e.target.value })} 
                  placeholder="Enter resume URL" 
                />
              </div>

              <div className="space-y-2">
                <Label>Meeting Link (Zoom/Google Meet)</Label>
                <Input 
                  type="url" 
                  value={eventForm.meetingLink} 
                  onChange={(e) => setEventForm({ ...eventForm, meetingLink: e.target.value })} 
                  placeholder="https://meet.google.com/... or https://zoom.us/j/..." 
                />
                <p className="text-xs text-muted-foreground">
                  Add a video conferencing link for virtual interviews
                </p>
              </div>

              <div className="space-y-2">
                <Label>Scheduled On <span className="text-red-500">*</span></Label>
                <Input 
                  type="date" 
                  value={eventForm.scheduledOn} 
                  onChange={(e) => setEventForm({ ...eventForm, scheduledOn: e.target.value })} 
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>From Time <span className="text-red-500">*</span></Label>
                  <Input 
                    type="time" 
                    value={eventForm.fromTime} 
                    onChange={(e) => setEventForm({ ...eventForm, fromTime: e.target.value })} 
                  />
                </div>
                <div className="space-y-2">
                  <Label>To Time <span className="text-red-500">*</span></Label>
                  <Input 
                    type="time" 
                    value={eventForm.toTime} 
                    onChange={(e) => setEventForm({ ...eventForm, toTime: e.target.value })} 
                  />
                </div>
              </div>
            </CardContent>
          </Card>
          <div className="mt-6">
            <Button 
              onClick={handleSaveEvent} 
              disabled={isSaving} 
              className="bg-orange-600 hover:bg-orange-700 text-white px-8"
            >
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
