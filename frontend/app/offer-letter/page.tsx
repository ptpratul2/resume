// "use client"
// import { useState } from "react"
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Textarea } from "@/components/ui/textarea"
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
// import { Avatar, AvatarFallback } from "@/components/ui/avatar"
// import { FileText, Send, Download, Eye, ArrowLeft, Calendar, DollarSign, MapPin, Briefcase } from "lucide-react"
// import Link from "next/link"

// interface SelectedCandidate {
//   id: string
//   name: string
//   email: string
//   position: string
//   experience: string
//   expectedSalary: string
// }

// export default function OfferLetterPage() {
//   const [selectedCandidates] = useState<SelectedCandidate[]>([
//     {
//       id: "1",
//       name: "Sarah Johnson",
//       email: "sarah.johnson@email.com",
//       position: "Senior Developer",
//       experience: "5+ years",
//       expectedSalary: "₹12,00,000",
//     },
//     {
//       id: "2",
//       name: "Emily Rodriguez",
//       email: "emily.rodriguez@email.com",
//       position: "Senior Developer",
//       experience: "6+ years",
//       expectedSalary: "₹15,00,000",
//     },
//   ])

//   const [selectedCandidate, setSelectedCandidate] = useState<SelectedCandidate | null>(null)
//   const [offerDetails, setOfferDetails] = useState({
//     salary: "",
//     joiningDate: "",
//     location: "",
//     department: "",
//     reportingManager: "",
//     benefits: "",
//     additionalTerms: "",
//   })

//   const handleGenerateOffer = () => {
//     console.log("Generating offer for:", selectedCandidate?.name, offerDetails)
//     // Dummy offer generation
//   }

//   const handleSendOffer = () => {
//     console.log("Sending offer to:", selectedCandidate?.email)
//     // Dummy offer sending
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50">
//       <div className="container mx-auto p-8 space-y-8">
//         {/* Header */}
//         <div className="flex items-center justify-between">
//           <div className="space-y-2">
//             <div className="flex items-center space-x-4">
//               <Link href="/">
//                 <Button variant="outline" size="sm">
//                   <ArrowLeft className="h-4 w-4 mr-2" />
//                   Back to Dashboard
//                 </Button>
//               </Link>
//               <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
//                 Offer Letter Management
//               </h1>
//             </div>
//             <p className="text-muted-foreground">Generate and send offer letters to selected candidates</p>
//           </div>
//         </div>

//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
//           {/* Shortlisted Candidates */}
//           <div className="lg:col-span-1 space-y-4">
//             <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
//               <CardHeader>
//                 <CardTitle className="flex items-center space-x-2">
//                   <FileText className="h-5 w-5" />
//                   <span>Shortlisted Candidates</span>
//                 </CardTitle>
//                 <CardDescription>Ready for offer letters</CardDescription>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 {selectedCandidates.map((candidate) => (
//                   <Card
//                     key={candidate.id}
//                     className={`cursor-pointer transition-all duration-300 hover:shadow-md ${
//                       selectedCandidate?.id === candidate.id ? "ring-2 ring-emerald-500" : ""
//                     }`}
//                     onClick={() => setSelectedCandidate(candidate)}
//                   >
//                     <CardContent className="p-4">
//                       <div className="flex items-start space-x-3">
//                         <Avatar className="h-10 w-10">
//                           <AvatarFallback className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm">
//                             {candidate.name
//                               .split(" ")
//                               .map((n) => n[0])
//                               .join("")}
//                           </AvatarFallback>
//                         </Avatar>
//                         <div className="flex-1 space-y-1">
//                           <h3 className="font-semibold text-sm">{candidate.name}</h3>
//                           <p className="text-xs text-muted-foreground">{candidate.position}</p>
//                           <div className="flex items-center space-x-2 text-xs text-muted-foreground">
//                             <span>{candidate.experience}</span>
//                             <span>•</span>
//                             <span>{candidate.expectedSalary}</span>
//                           </div>
//                         </div>
//                       </div>
//                     </CardContent>
//                   </Card>
//                 ))}
//               </CardContent>
//             </Card>
//           </div>

//           {/* Offer Letter Form */}
//           <div className="lg:col-span-2 space-y-6">
//             {selectedCandidate ? (
//               <>
//                 <Card className="border-0 shadow-lg bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
//                   <CardHeader>
//                     <CardTitle className="flex items-center space-x-2">
//                       <FileText className="h-5 w-5" />
//                       <span>Generate Offer Letter</span>
//                     </CardTitle>
//                     <CardDescription className="text-emerald-100">
//                       For {selectedCandidate.name} - {selectedCandidate.position}
//                     </CardDescription>
//                   </CardHeader>
//                 </Card>

//                 <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
//                   <CardHeader>
//                     <CardTitle>Offer Details</CardTitle>
//                     <CardDescription>Fill in the offer letter details</CardDescription>
//                   </CardHeader>
//                   <CardContent className="space-y-6">
//                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                       <div className="space-y-2">
//                         <Label htmlFor="salary" className="flex items-center space-x-2">
//                           <DollarSign className="h-4 w-4" />
//                           <span>Annual Salary (₹)</span>
//                         </Label>
//                         <Input
//                           id="salary"
//                           value={offerDetails.salary}
//                           onChange={(e) => setOfferDetails({ ...offerDetails, salary: e.target.value })}
//                           placeholder="e.g., 1200000"
//                         />
//                       </div>

//                       <div className="space-y-2">
//                         <Label htmlFor="joiningDate" className="flex items-center space-x-2">
//                           <Calendar className="h-4 w-4" />
//                           <span>Joining Date</span>
//                         </Label>
//                         <Input
//                           id="joiningDate"
//                           type="date"
//                           value={offerDetails.joiningDate}
//                           onChange={(e) => setOfferDetails({ ...offerDetails, joiningDate: e.target.value })}
//                         />
//                       </div>

//                       <div className="space-y-2">
//                         <Label htmlFor="location" className="flex items-center space-x-2">
//                           <MapPin className="h-4 w-4" />
//                           <span>Work Location</span>
//                         </Label>
//                         <Select onValueChange={(value) => setOfferDetails({ ...offerDetails, location: value })}>
//                           <SelectTrigger>
//                             <SelectValue placeholder="Select location" />
//                           </SelectTrigger>
//                           <SelectContent>
//                             <SelectItem value="bangalore">Bangalore</SelectItem>
//                             <SelectItem value="mumbai">Mumbai</SelectItem>
//                             <SelectItem value="delhi">Delhi</SelectItem>
//                             <SelectItem value="remote">Remote</SelectItem>
//                           </SelectContent>
//                         </Select>
//                       </div>

//                       <div className="space-y-2">
//                         <Label htmlFor="department" className="flex items-center space-x-2">
//                           <Briefcase className="h-4 w-4" />
//                           <span>Department</span>
//                         </Label>
//                         <Select onValueChange={(value) => setOfferDetails({ ...offerDetails, department: value })}>
//                           <SelectTrigger>
//                             <SelectValue placeholder="Select department" />
//                           </SelectTrigger>
//                           <SelectContent>
//                             <SelectItem value="engineering">Engineering</SelectItem>
//                             <SelectItem value="product">Product</SelectItem>
//                             <SelectItem value="design">Design</SelectItem>
//                             <SelectItem value="marketing">Marketing</SelectItem>
//                           </SelectContent>
//                         </Select>
//                       </div>
//                     </div>

//                     <div className="space-y-2">
//                       <Label htmlFor="reportingManager">Reporting Manager</Label>
//                       <Input
//                         id="reportingManager"
//                         value={offerDetails.reportingManager}
//                         onChange={(e) => setOfferDetails({ ...offerDetails, reportingManager: e.target.value })}
//                         placeholder="Manager's name"
//                       />
//                     </div>

//                     <div className="space-y-2">
//                       <Label htmlFor="benefits">Benefits & Perks</Label>
//                       <Textarea
//                         id="benefits"
//                         value={offerDetails.benefits}
//                         onChange={(e) => setOfferDetails({ ...offerDetails, benefits: e.target.value })}
//                         placeholder="Health insurance, PF, gratuity, flexible hours..."
//                         rows={3}
//                       />
//                     </div>

//                     <div className="space-y-2">
//                       <Label htmlFor="additionalTerms">Additional Terms</Label>
//                       <Textarea
//                         id="additionalTerms"
//                         value={offerDetails.additionalTerms}
//                         onChange={(e) => setOfferDetails({ ...offerDetails, additionalTerms: e.target.value })}
//                         placeholder="Probation period, notice period, confidentiality..."
//                         rows={3}
//                       />
//                     </div>

//                     <div className="flex space-x-4">
//                       <Button onClick={handleGenerateOffer} className="flex-1 bg-emerald-600 hover:bg-emerald-700">
//                         <Eye className="h-4 w-4 mr-2" />
//                         Preview Offer
//                       </Button>
//                       <Button onClick={handleGenerateOffer} variant="outline" className="flex-1 bg-transparent">
//                         <Download className="h-4 w-4 mr-2" />
//                         Download PDF
//                       </Button>
//                       <Button onClick={handleSendOffer} className="flex-1 bg-blue-600 hover:bg-blue-700">
//                         <Send className="h-4 w-4 mr-2" />
//                         Send Offer
//                       </Button>
//                     </div>
//                   </CardContent>
//                 </Card>

//                 {/* Offer Preview */}
//                 <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
//                   <CardHeader>
//                     <CardTitle>Offer Letter Preview</CardTitle>
//                     <CardDescription>Preview of the offer letter to be sent</CardDescription>
//                   </CardHeader>
//                   <CardContent className="space-y-4">
//                     <div className="bg-gray-50 p-6 rounded-lg border-2 border-dashed border-gray-300">
//                       <div className="space-y-4 text-sm">
//                         <div className="text-center">
//                           <h2 className="text-xl font-bold">OFFER LETTER</h2>
//                           <p className="text-muted-foreground">Company Name</p>
//                         </div>

//                         <div className="space-y-2">
//                           <p>
//                             <strong>Dear {selectedCandidate.name},</strong>
//                           </p>
//                           <p>
//                             We are pleased to offer you the position of <strong>{selectedCandidate.position}</strong> at
//                             our company.
//                           </p>
//                         </div>

//                         <div className="grid grid-cols-2 gap-4 bg-white p-4 rounded border">
//                           <div>
//                             <strong>Position:</strong> {selectedCandidate.position}
//                           </div>
//                           <div>
//                             <strong>Department:</strong> {offerDetails.department || "TBD"}
//                           </div>
//                           <div>
//                             <strong>Salary:</strong> ₹{offerDetails.salary || "TBD"} per annum
//                           </div>
//                           <div>
//                             <strong>Location:</strong> {offerDetails.location || "TBD"}
//                           </div>
//                           <div>
//                             <strong>Joining Date:</strong> {offerDetails.joiningDate || "TBD"}
//                           </div>
//                           <div>
//                             <strong>Reporting To:</strong> {offerDetails.reportingManager || "TBD"}
//                           </div>
//                         </div>

//                         <p className="text-xs text-muted-foreground">
//                           This is a preview. The actual offer letter will contain complete terms and conditions.
//                         </p>
//                       </div>
//                     </div>
//                   </CardContent>
//                 </Card>
//               </>
//             ) : (
//               <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
//                 <CardContent className="p-12 text-center">
//                   <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
//                   <h3 className="text-xl font-semibold mb-2">Select a Candidate</h3>
//                   <p className="text-muted-foreground">
//                     Choose a shortlisted candidate to generate and send an offer letter.
//                   </p>
//                 </CardContent>
//               </Card>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }













"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { useRouter } from "next/navigation"
import axios from "axios"
import { API_AUTH, API_BASE_URL } from "../create-job/page"

interface JobApplicant {
  name: string
  applicant_name: string
  email_id: string
}

interface JobOfferTemplate {
  name: string
  offer_term_template_name: string
}

interface OfferTerm {
  id: string
  offer_term: string
  value_description: string
}

export default function JobOfferPage() {
  const router = useRouter()
  const [offerForm, setOfferForm] = useState({
    jobApplicant: "",
    applicantName: "",
    applicantEmail: "",
    status: "Awaiting Response",
    offerDate: "",
    designation: "",
    company: "",
    jobOfferTemplate: "",
  })

  const [offerTerms, setOfferTerms] = useState<OfferTerm[]>([])
  const [jobApplicants, setJobApplicants] = useState<JobApplicant[]>([])
  const [templates, setTemplates] = useState<JobOfferTemplate[]>([])
  const [isSaving, setIsSaving] = useState(false)

  const statusOptions = [
    "Awaiting Response",
    "Accepted",
    "Rejected",
    "Pending"
  ]

  useEffect(() => {
    fetchJobApplicants()
    fetchTemplates()
  }, [])

  const fetchJobApplicants = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/resource/Job Applicant`,
        {
          params: {
            fields: JSON.stringify(["name","applicant_name","email_id"]),
            limit_page_length: 100
          },
          ...API_AUTH
        }
      )
      
      if (response.data && response.data.data) {
        setJobApplicants(response.data.data)
        console.log("Fetched job applicants:", response.data.data)
      }
    } catch (error) {
      console.error("Error fetching job applicants:", error)
      setJobApplicants([])
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/resource/Job Offer Term Template`,
        {
          params: {
            fields: JSON.stringify(["name","offer_term_template_name"]),
            limit_page_length: 100
          },
          ...API_AUTH
        }
      )
      
      if (response.data && response.data.data) {
        setTemplates(response.data.data)
        console.log("Fetched templates:", response.data.data)
      }
    } catch (error) {
      console.error("Error fetching templates:", error)
      setTemplates([])
    }
  }

  const handleJobApplicantChange = (value: string) => {
    const applicant = jobApplicants.find(a => a.name === value)
    if (applicant) {
      setOfferForm({
        ...offerForm,
        jobApplicant: value,
        applicantName: applicant.applicant_name,
        applicantEmail: applicant.email_id
      })
    }
  }

  const addOfferTerm = () => {
    const newTerm: OfferTerm = {
      id: Date.now().toString(),
      offer_term: "",
      value_description: ""
    }
    setOfferTerms([...offerTerms, newTerm])
  }

  const removeOfferTerm = (id: string) => {
    setOfferTerms(offerTerms.filter(term => term.id !== id))
  }

  const updateOfferTerm = (id: string, field: keyof OfferTerm, value: string) => {
    setOfferTerms(offerTerms.map(term => 
      term.id === id ? { ...term, [field]: value } : term
    ))
  }

  const handleSave = async () => {
    if (!offerForm.jobApplicant || !offerForm.applicantName || !offerForm.designation || !offerForm.company) {
      alert("Please fill all required fields")
      return
    }

    setIsSaving(true)
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/resource/Job Offer`,
        {
          job_applicant: offerForm.jobApplicant,
          applicant_name: offerForm.applicantName,
          applicant_email: offerForm.applicantEmail || null,
          offer_date: offerForm.offerDate || null,
          designation: offerForm.designation,
          company: offerForm.company,
          status: offerForm.status,
          job_offer_term_template: offerForm.jobOfferTemplate || null,
          offer_terms: offerTerms.map(term => ({
            offer_term: term.offer_term,
            value: term.value_description
          }))
        },
        API_AUTH
      )

      if (response.data) {
        alert("Job Offer created successfully!")
        console.log("Created job offer:", response.data)
        router.back()
      }
    } catch (error: any) {
      console.error("Error creating job offer:", error)
      const errorMessage = error.response?.data?.exception || error.response?.data?.message || "Failed to create job offer"
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
              <h1 className="text-3xl font-bold">New Job Offer</h1>
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
                  <Label>Job Applicant <span className="text-red-500">*</span></Label>
                  {jobApplicants.length > 0 ? (
                    <Select 
                      value={offerForm.jobApplicant} 
                      onValueChange={handleJobApplicantChange}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select applicant" />
                      </SelectTrigger>
                      <SelectContent>
                        {jobApplicants.map((applicant) => (
                          <SelectItem key={applicant.name} value={applicant.name}>
                            {applicant.email_id}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input 
                      value={offerForm.jobApplicant}
                      onChange={(e) => setOfferForm({ ...offerForm, jobApplicant: e.target.value })}
                      placeholder="Loading applicants..."
                    />
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Status <span className="text-red-500">*</span></Label>
                  <Select 
                    value={offerForm.status} 
                    onValueChange={(value) => setOfferForm({ ...offerForm, status: value })}
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

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Applicant Name <span className="text-red-500">*</span></Label>
                  <Input 
                    value={offerForm.applicantName}
                    onChange={(e) => setOfferForm({ ...offerForm, applicantName: e.target.value })}
                    placeholder="Enter applicant name"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Offer Date <span className="text-red-500">*</span></Label>
                  <Input 
                    type="date"
                    value={offerForm.offerDate}
                    onChange={(e) => setOfferForm({ ...offerForm, offerDate: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Applicant Email Address</Label>
                  <Input 
                    type="email"
                    value={offerForm.applicantEmail}
                    onChange={(e) => setOfferForm({ ...offerForm, applicantEmail: e.target.value })}
                    placeholder="Enter email"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Designation <span className="text-red-500">*</span></Label>
                  <Input 
                    value={offerForm.designation}
                    onChange={(e) => setOfferForm({ ...offerForm, designation: e.target.value })}
                    placeholder="Enter designation"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Job Offer Term Template</Label>
                  {templates.length > 0 ? (
                    <Select 
                      value={offerForm.jobOfferTemplate} 
                      onValueChange={(value) => setOfferForm({ ...offerForm, jobOfferTemplate: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select template" />
                      </SelectTrigger>
                      <SelectContent>
                        {templates.map((template) => (
                          <SelectItem key={template.name} value={template.name}>
                            {template.offer_term_template_name || template.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input 
                      value={offerForm.jobOfferTemplate}
                      onChange={(e) => setOfferForm({ ...offerForm, jobOfferTemplate: e.target.value })}
                      placeholder="Loading templates..."
                    />
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Company <span className="text-red-500">*</span></Label>
                  <Input 
                    value={offerForm.company}
                    onChange={(e) => setOfferForm({ ...offerForm, company: e.target.value })}
                    placeholder="Enter company name"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="mt-6 border-0 shadow-lg bg-white">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle>Job Offer Terms</CardTitle>
                <Button 
                  onClick={addOfferTerm}
                  size="sm"
                  className="bg-orange-600 hover:bg-orange-700 text-white"
                >
                  Add Row
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b">
                    <tr>
                      <th className="text-left p-4 text-sm font-medium w-12">No.</th>
                      <th className="text-left p-4 text-sm font-medium">
                        Offer Term <span className="text-red-500">*</span>
                      </th>
                      <th className="text-left p-4 text-sm font-medium">
                        Value / Description <span className="text-red-500">*</span>
                      </th>
                      <th className="w-12"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {offerTerms.map((term, index) => (
                      <tr key={term.id} className="border-b">
                        <td className="p-4">{index + 1}</td>
                        <td className="p-4">
                          <Input 
                            value={term.offer_term}
                            onChange={(e) => updateOfferTerm(term.id, 'offer_term', e.target.value)}
                            placeholder="Enter offer term"
                          />
                        </td>
                        <td className="p-4">
                          <Textarea 
                            value={term.value_description}
                            onChange={(e) => updateOfferTerm(term.id, 'value_description', e.target.value)}
                            placeholder="Enter value or description"
                            className="min-h-[60px]"
                            rows={2}
                          />
                        </td>
                        <td className="p-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeOfferTerm(term.id)}
                          >
                            Delete
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="mt-6">
            <Button 
              onClick={handleSave} 
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