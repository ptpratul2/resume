"use client"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Checkbox } from "@/components/ui/checkbox"
import { UserCheck, Send, Download, ArrowLeft, Calendar, FileText, Clock, Building } from "lucide-react"
import Link from "next/link"

interface AcceptedCandidate {
  id: string
  name: string
  email: string
  position: string
  salary: string
  joiningDate: string
  offerAcceptedDate: string
  status: "offer-accepted" | "documents-pending" | "appointment-ready"
}

export default function AppointmentPage() {
  const [acceptedCandidates] = useState<AcceptedCandidate[]>([
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.johnson@email.com",
      position: "Senior Developer",
      salary: "₹12,00,000",
      joiningDate: "2025-02-15",
      offerAcceptedDate: "2025-01-18",
      status: "offer-accepted",
    },
    {
      id: "2",
      name: "Emily Rodriguez",
      email: "emily.rodriguez@email.com",
      position: "Senior Developer",
      salary: "₹15,00,000",
      joiningDate: "2025-02-20",
      offerAcceptedDate: "2025-01-17",
      status: "appointment-ready",
    },
  ])

  const [selectedCandidate, setSelectedCandidate] = useState<AcceptedCandidate | null>(null)
  const [appointmentDetails, setAppointmentDetails] = useState({
    employeeId: "",
    workLocation: "",
    reportingManager: "",
    probationPeriod: "6",
    noticePeriod: "30",
    workingHours: "9:00 AM - 6:00 PM",
    additionalClauses: "",
  })

  const [documentsChecklist, setDocumentsChecklist] = useState({
    aadhar: false,
    pan: false,
    passport: false,
    education: false,
    experience: false,
    medical: false,
    bankDetails: false,
    photos: false,
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "appointment-ready":
        return "bg-green-500"
      case "documents-pending":
        return "bg-yellow-500"
      default:
        return "bg-blue-500"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "appointment-ready":
        return "Ready for Appointment"
      case "documents-pending":
        return "Documents Pending"
      default:
        return "Offer Accepted"
    }
  }

  const handleGenerateAppointment = () => {
    console.log("Generating appointment letter for:", selectedCandidate?.name, appointmentDetails)
  }

  const handleSendAppointment = () => {
    console.log("Sending appointment letter to:", selectedCandidate?.email)
  }

  const handleDocumentCheck = (document: string, checked: boolean) => {
    setDocumentsChecklist((prev) => ({
      ...prev,
      [document]: checked,
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
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
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Appointment Letters
              </h1>
            </div>
            <p className="text-muted-foreground">Generate appointment letters for candidates who accepted offers</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Accepted Candidates */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <UserCheck className="h-5 w-5" />
                  <span>Accepted Offers</span>
                </CardTitle>
                <CardDescription>Candidates ready for appointment</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {acceptedCandidates.map((candidate) => (
                  <Card
                    key={candidate.id}
                    className={`cursor-pointer transition-all duration-300 hover:shadow-md ${
                      selectedCandidate?.id === candidate.id ? "ring-2 ring-blue-500" : ""
                    }`}
                    onClick={() => setSelectedCandidate(candidate)}
                  >
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-start space-x-3">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm">
                              {candidate.name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 space-y-1">
                            <h3 className="font-semibold text-sm">{candidate.name}</h3>
                            <p className="text-xs text-muted-foreground">{candidate.position}</p>
                            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                              <Calendar className="h-3 w-3" />
                              <span>Joins: {candidate.joiningDate}</span>
                            </div>
                          </div>
                        </div>
                        <Badge className={getStatusColor(candidate.status)} size="sm">
                          {getStatusText(candidate.status)}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Appointment Letter Form */}
          <div className="lg:col-span-2 space-y-6">
            {selectedCandidate ? (
              <>
                <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <UserCheck className="h-5 w-5" />
                      <span>Generate Appointment Letter</span>
                    </CardTitle>
                    <CardDescription className="text-blue-100">
                      For {selectedCandidate.name} - {selectedCandidate.position}
                    </CardDescription>
                  </CardHeader>
                </Card>

                {/* Document Verification */}
                <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FileText className="h-5 w-5" />
                      <span>Document Verification</span>
                    </CardTitle>
                    <CardDescription>Verify all required documents are received</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(documentsChecklist).map(([doc, checked]) => (
                        <div key={doc} className="flex items-center space-x-2">
                          <Checkbox
                            id={doc}
                            checked={checked}
                            onCheckedChange={(checked) => handleDocumentCheck(doc, !!checked)}
                          />
                          <Label htmlFor={doc} className="text-sm capitalize">
                            {doc.replace(/([A-Z])/g, " $1").trim()}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Appointment Details */}
                <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle>Appointment Details</CardTitle>
                    <CardDescription>Fill in the appointment letter details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="employeeId">Employee ID</Label>
                        <Input
                          id="employeeId"
                          value={appointmentDetails.employeeId}
                          onChange={(e) => setAppointmentDetails({ ...appointmentDetails, employeeId: e.target.value })}
                          placeholder="e.g., EMP001"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="workLocation" className="flex items-center space-x-2">
                          <Building className="h-4 w-4" />
                          <span>Work Location</span>
                        </Label>
                        <Select
                          onValueChange={(value) =>
                            setAppointmentDetails({ ...appointmentDetails, workLocation: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select location" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bangalore">Bangalore Office</SelectItem>
                            <SelectItem value="mumbai">Mumbai Office</SelectItem>
                            <SelectItem value="delhi">Delhi Office</SelectItem>
                            <SelectItem value="remote">Remote Work</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="reportingManager">Reporting Manager</Label>
                        <Input
                          id="reportingManager"
                          value={appointmentDetails.reportingManager}
                          onChange={(e) =>
                            setAppointmentDetails({ ...appointmentDetails, reportingManager: e.target.value })
                          }
                          placeholder="Manager's name"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="workingHours" className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span>Working Hours</span>
                        </Label>
                        <Input
                          id="workingHours"
                          value={appointmentDetails.workingHours}
                          onChange={(e) =>
                            setAppointmentDetails({ ...appointmentDetails, workingHours: e.target.value })
                          }
                          placeholder="e.g., 9:00 AM - 6:00 PM"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="probationPeriod">Probation Period (months)</Label>
                        <Select
                          onValueChange={(value) =>
                            setAppointmentDetails({ ...appointmentDetails, probationPeriod: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="3">3 months</SelectItem>
                            <SelectItem value="6">6 months</SelectItem>
                            <SelectItem value="12">12 months</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="noticePeriod">Notice Period (days)</Label>
                        <Select
                          onValueChange={(value) =>
                            setAppointmentDetails({ ...appointmentDetails, noticePeriod: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="30">30 days</SelectItem>
                            <SelectItem value="60">60 days</SelectItem>
                            <SelectItem value="90">90 days</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="additionalClauses">Additional Terms & Conditions</Label>
                      <Textarea
                        id="additionalClauses"
                        value={appointmentDetails.additionalClauses}
                        onChange={(e) =>
                          setAppointmentDetails({ ...appointmentDetails, additionalClauses: e.target.value })
                        }
                        placeholder="Any additional terms, policies, or conditions..."
                        rows={4}
                      />
                    </div>

                    <div className="flex space-x-4">
                      <Button onClick={handleGenerateAppointment} className="flex-1 bg-blue-600 hover:bg-blue-700">
                        <FileText className="h-4 w-4 mr-2" />
                        Generate Letter
                      </Button>
                      <Button onClick={handleGenerateAppointment} variant="outline" className="flex-1 bg-transparent">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
                      </Button>
                      <Button onClick={handleSendAppointment} className="flex-1 bg-green-600 hover:bg-green-700">
                        <Send className="h-4 w-4 mr-2" />
                        Send Letter
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Appointment Preview */}
                <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle>Appointment Letter Preview</CardTitle>
                    <CardDescription>Preview of the appointment letter</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-50 p-6 rounded-lg border-2 border-dashed border-gray-300">
                      <div className="space-y-4 text-sm">
                        <div className="text-center">
                          <h2 className="text-xl font-bold">APPOINTMENT LETTER</h2>
                          <p className="text-muted-foreground">Company Name</p>
                        </div>

                        <div className="space-y-2">
                          <p>
                            <strong>Dear {selectedCandidate.name},</strong>
                          </p>
                          <p>
                            We are pleased to confirm your appointment as <strong>{selectedCandidate.position}</strong>{" "}
                            with our organization.
                          </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 bg-white p-4 rounded border">
                          <div>
                            <strong>Employee ID:</strong> {appointmentDetails.employeeId || "TBD"}
                          </div>
                          <div>
                            <strong>Position:</strong> {selectedCandidate.position}
                          </div>
                          <div>
                            <strong>Salary:</strong> {selectedCandidate.salary} per annum
                          </div>
                          <div>
                            <strong>Joining Date:</strong> {selectedCandidate.joiningDate}
                          </div>
                          <div>
                            <strong>Work Location:</strong> {appointmentDetails.workLocation || "TBD"}
                          </div>
                          <div>
                            <strong>Working Hours:</strong> {appointmentDetails.workingHours}
                          </div>
                          <div>
                            <strong>Probation:</strong> {appointmentDetails.probationPeriod} months
                          </div>
                          <div>
                            <strong>Notice Period:</strong> {appointmentDetails.noticePeriod} days
                          </div>
                        </div>

                        <p className="text-xs text-muted-foreground">
                          This is a preview. The actual appointment letter will contain complete terms and conditions.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                <CardContent className="p-12 text-center">
                  <UserCheck className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">Select a Candidate</h3>
                  <p className="text-muted-foreground">
                    Choose a candidate who has accepted the offer to generate their appointment letter.
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
