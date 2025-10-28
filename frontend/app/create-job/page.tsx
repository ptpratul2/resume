// "use client"
// import { useEffect, useState } from "react"
// import type React from "react"
// import axios from "axios"
// import { Card, CardContent } from "@/components/ui/card"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Button } from "@/components/ui/button"
// import { Textarea } from "@/components/ui/textarea"
// import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
// import { Checkbox } from "@/components/ui/checkbox"
// import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
// import { Badge } from "@/components/ui/badge"
// import { Progress } from "@/components/ui/progress"
// import {
//   ArrowLeft,
//   Briefcase,
//   Building,
//   MapPin,
//   Users,
//   DollarSign,
//   Calendar,
//   CheckCircle,
//   AlertCircle,
//   Globe,
//   Clock,
//   FileText,
//   Sparkles,
// } from "lucide-react"
// import Link from "next/link"

// export const API_AUTH = {
//   headers: {
//     Authorization: `token 651df2850ec7830:ca679624badb5c4`,
//   },
// }

// export default function CreateJobOpeningForm() {
//   const [currentStep, setCurrentStep] = useState(1)
//   const [formData, setFormData] = useState({
//     job_title: "",
//     designation: "",
//     description: "",
//     currency: "INR",
//     lower_range: "",
//     upper_range: "",
//     publish_salary_range: false,
//     company: "",
//     employment_type: "",
//     department: "",
//     location: "",
//     publish_on_website: false,
//     posted_on: new Date().toISOString().split("T")[0],
//     closes_on: "",
//     status: "Open",
//     salary_per: "Month",
//   })

//   const [options, setOptions] = useState({
//     companies: [],
//     departments: [],
//     employment_types: [],
//     designations: [],
//     locations: [],
//   })
//   const [loading, setLoading] = useState(false)
//   const [status, setStatus] = useState<null | { type: "success" | "error"; message: string }>(null)

//   const steps = [
//     { id: 1, title: "Job Details", icon: <Briefcase className="h-5 w-5" /> },
//     { id: 2, title: "Company Info", icon: <Building className="h-5 w-5" /> },
//     { id: 3, title: "Requirements", icon: <FileText className="h-5 w-5" /> },
//     { id: 4, title: "Compensation", icon: <DollarSign className="h-5 w-5" /> },
//   ]

//   useEffect(() => {
//     async function fetchOptions() {
//       try {
//         const [companies, departments, employment_types, designations, locations] = await Promise.all([
//           axios.get('http://localhost:8000/api/resource/Company?fields=["name"]', API_AUTH),
//           axios.get('http://localhost:8000/api/resource/Department?fields=["name"]', API_AUTH),
//           axios.get('http://localhost:8000/api/resource/Employment Type?fields=["name"]', API_AUTH),
//           axios.get('http://localhost:8000/api/resource/Designation?fields=["name"]', API_AUTH),
//           axios.get('http://localhost:8000/api/resource/Location?fields=["name"]', API_AUTH),
//         ])
//         setOptions({
//           companies: companies.data.data.map((d: any) => d.name),
//           departments: departments.data.data.map((d: any) => d.name),
//           employment_types: employment_types.data.data.map((d: any) => d.name),
//           designations: designations.data.data.map((d: any) => d.name),
//           locations: locations.data.data.map((d: any) => d.name),
//         })
//       } catch (err) {
//         console.error("Error fetching dropdowns", err)
//         setStatus({ type: "error", message: "Failed to load dropdown options." })
//       }
//     }
//     fetchOptions()
//   }, [])

//   const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
//     setFormData({ ...formData, [e.target.name]: e.target.value })
//   }

//   const handleCheckbox = (name: string, value: boolean) => {
//     setFormData({ ...formData, [name]: value })
//   }

//   const handleSelect = (name: string, value: string) => {
//     setFormData({ ...formData, [name]: value })
//   }

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     setLoading(true)
//     setStatus(null)

//     const payload = {
//       ...formData,
//       lower_range: Number.parseFloat(formData.lower_range) || undefined,
//       upper_range: Number.parseFloat(formData.upper_range) || undefined,
//       status: formData.status,
//       salary_per: formData.salary_per,
//     }

//     if (!payload.job_title || !payload.designation) {
//       setStatus({ type: "error", message: "Job Title and Designation are required." })
//       setLoading(false)
//       return
//     }

//     if (payload.lower_range !== undefined && payload.upper_range !== undefined) {
//       if (isNaN(payload.lower_range) || payload.lower_range <= 0) {
//         setStatus({ type: "error", message: "Lower Range must be a positive number." })
//         setLoading(false)
//         return
//       }
//       if (isNaN(payload.upper_range) || payload.upper_range <= 0) {
//         setStatus({ type: "error", message: "Upper Range must be a positive number." })
//         setLoading(false)
//         return
//       }
//       if (payload.lower_range >= payload.upper_range) {
//         setStatus({ type: "error", message: "Lower Range must be less than Upper Range." })
//         setLoading(false)
//         return
//       }
//     }

//     try {
//       const res = await axios.post(
//         "http://localhost:8000/api/method/resume.api.job_opening.create_job_opening",
//         payload,
//         API_AUTH,
//       )
//       setStatus({ type: "success", message: res.data.message })
//       setFormData({
//         job_title: "",
//         designation: "",
//         description: "",
//         currency: "INR",
//         lower_range: "",
//         upper_range: "",
//         publish_salary_range: false,
//         company: "",
//         employment_type: "",
//         department: "",
//         location: "",
//         publish_on_website: false,
//         posted_on: new Date().toISOString().split("T")[0],
//         closes_on: "",
//         status: "Open",
//         salary_per: "Month",
//       })
//     } catch (err: any) {
//       console.error("Create job failed", err.response?.data || err)
//       setStatus({
//         type: "error",
//         message: err.response?.data?.message || "Failed to create job opening. Check server logs.",
//       })
//     } finally {
//       setLoading(false)
//     }
//   }

//   const getStepStatus = (stepId: number) => {
//     if (stepId < currentStep) return "completed"
//     if (stepId === currentStep) return "current"
//     return "pending"
//   }

//   const renderStepContent = () => {
//     switch (currentStep) {
//       case 1:
//         return (
//           <div className="space-y-6">
//             <div className="text-center space-y-2">
//               <Sparkles className="h-12 w-12 text-blue-500 mx-auto" />
//               <h3 className="text-2xl font-bold">Let's Create Something Amazing</h3>
//               <p className="text-muted-foreground">Start by defining the core details of your job opening</p>
//             </div>

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//               <div className="space-y-2">
//                 <Label htmlFor="job_title" className="flex items-center space-x-2">
//                   <Briefcase className="h-4 w-4" />
//                   <span>Job Title</span>
//                 </Label>
//                 <Input
//                   id="job_title"
//                   name="job_title"
//                   value={formData.job_title}
//                   onChange={handleChange}
//                   placeholder="e.g., Senior Full Stack Developer"
//                   className="h-12 text-lg"
//                   required
//                 />
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="designation" className="flex items-center space-x-2">
//                   <Users className="h-4 w-4" />
//                   <span>Designation</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("designation", val)} value={formData.designation}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Designation" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {options.designations.length === 0 && (
//                       <SelectItem value="no-designations" disabled>
//                         No designations available
//                       </SelectItem>
//                     )}
//                     {options.designations.map((d) => (
//                       <SelectItem key={d} value={d}>
//                         {d}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="status" className="flex items-center space-x-2">
//                   <AlertCircle className="h-4 w-4" />
//                   <span>Status</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("status", val)} value={formData.status}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Status" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="Open">
//                       <div className="flex items-center space-x-2">
//                         <div className="w-2 h-2 bg-green-500 rounded-full"></div>
//                         <span>Open</span>
//                       </div>
//                     </SelectItem>
//                     <SelectItem value="Closed">
//                       <div className="flex items-center space-x-2">
//                         <div className="w-2 h-2 bg-red-500 rounded-full"></div>
//                         <span>Closed</span>
//                       </div>
//                     </SelectItem>
//                     <SelectItem value="On Hold">
//                       <div className="flex items-center space-x-2">
//                         <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
//                         <span>On Hold</span>
//                       </div>
//                     </SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="closes_on" className="flex items-center space-x-2">
//                   <Calendar className="h-4 w-4" />
//                   <span>Application Deadline</span>
//                 </Label>
//                 <Input
//                   id="closes_on"
//                   name="closes_on"
//                   value={formData.closes_on}
//                   onChange={handleChange}
//                   type="date"
//                   className="h-12"
//                 />
//               </div>
//             </div>
//           </div>
//         )

//       case 2:
//         return (
//           <div className="space-y-6">
//             <div className="text-center space-y-2">
//               <Building className="h-12 w-12 text-emerald-500 mx-auto" />
//               <h3 className="text-2xl font-bold">Company & Location Details</h3>
//               <p className="text-muted-foreground">Define where and how your team will work</p>
//             </div>

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//               <div className="space-y-2">
//                 <Label htmlFor="company" className="flex items-center space-x-2">
//                   <Building className="h-4 w-4" />
//                   <span>Company</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("company", val)} value={formData.company}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Company" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {options.companies.length === 0 && (
//                       <SelectItem value="no-companies" disabled>
//                         No companies available
//                       </SelectItem>
//                     )}
//                     {options.companies.map((c) => (
//                       <SelectItem key={c} value={c}>
//                         {c}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="department" className="flex items-center space-x-2">
//                   <Users className="h-4 w-4" />
//                   <span>Department</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("department", val)} value={formData.department}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Department" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {options.departments.length === 0 && (
//                       <SelectItem value="no-departments" disabled>
//                         No departments available
//                       </SelectItem>
//                     )}
//                     {options.departments.map((d) => (
//                       <SelectItem key={d} value={d}>
//                         {d}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="location" className="flex items-center space-x-2">
//                   <MapPin className="h-4 w-4" />
//                   <span>Work Location</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("location", val)} value={formData.location}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Location" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {options.locations.length === 0 && (
//                       <SelectItem value="no-locations" disabled>
//                         No locations available
//                       </SelectItem>
//                     )}
//                     {options.locations.map((l) => (
//                       <SelectItem key={l} value={l}>
//                         {l}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="employment_type" className="flex items-center space-x-2">
//                   <Clock className="h-4 w-4" />
//                   <span>Employment Type</span>
//                 </Label>
//                 <Select onValueChange={(val) => handleSelect("employment_type", val)} value={formData.employment_type}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Employment Type" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {options.employment_types.length === 0 && (
//                       <SelectItem value="no-employment-types" disabled>
//                         No employment types available
//                       </SelectItem>
//                     )}
//                     {options.employment_types.map((e) => (
//                       <SelectItem key={e} value={e}>
//                         {e}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>
//             </div>

//             <div className="space-y-4">
//               <div className="flex items-center space-x-2">
//                 <Checkbox
//                   checked={formData.publish_on_website}
//                   onCheckedChange={(val) => handleCheckbox("publish_on_website", !!val)}
//                   id="publish_on_website"
//                 />
//                 <Label htmlFor="publish_on_website" className="flex items-center space-x-2">
//                   <Globe className="h-4 w-4" />
//                   <span>Publish on company website</span>
//                 </Label>
//               </div>
//             </div>
//           </div>
//         )

//       case 3:
//         return (
//           <div className="space-y-6">
//             <div className="text-center space-y-2">
//               <FileText className="h-12 w-12 text-purple-500 mx-auto" />
//               <h3 className="text-2xl font-bold">Job Requirements</h3>
//               <p className="text-muted-foreground">Describe what you're looking for in detail</p>
//             </div>

//             <div className="space-y-4">
//               <Label htmlFor="description" className="text-lg font-semibold">
//                 Job Description
//               </Label>
//               <Textarea
//                 id="description"
//                 name="description"
//                 value={formData.description}
//                 onChange={handleChange}
//                 placeholder="Describe the role, responsibilities, qualifications, and what makes this opportunity exciting..."
//                 rows={12}
//                 className="text-base leading-relaxed"
//               />
//               <p className="text-sm text-muted-foreground">
//                 💡 Tip: Include key responsibilities, required skills, experience level, and company culture highlights
//               </p>
//             </div>
//           </div>
//         )

//       case 4:
//         return (
//           <div className="space-y-6">
//             <div className="text-center space-y-2">
//               <DollarSign className="h-12 w-12 text-green-500 mx-auto" />
//               <h3 className="text-2xl font-bold">Compensation Package</h3>
//               <p className="text-muted-foreground">Define the salary range and benefits</p>
//             </div>

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//               <div className="space-y-2">
//                 <Label htmlFor="currency">Currency</Label>
//                 <Select onValueChange={(val) => handleSelect("currency", val)} value={formData.currency}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Currency" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="INR">🇮🇳 INR - Indian Rupee</SelectItem>
//                     <SelectItem value="USD">🇺🇸 USD - US Dollar</SelectItem>
//                     <SelectItem value="EUR">🇪🇺 EUR - Euro</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="salary_per">Salary Period</Label>
//                 <Select onValueChange={(val) => handleSelect("salary_per", val)} value={formData.salary_per}>
//                   <SelectTrigger className="h-12">
//                     <SelectValue placeholder="Select Period" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="Month">Per Month</SelectItem>
//                     <SelectItem value="Year">Per Year</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="lower_range">Minimum Salary</Label>
//                 <Input
//                   id="lower_range"
//                   name="lower_range"
//                   value={formData.lower_range}
//                   onChange={handleChange}
//                   type="number"
//                   placeholder="0"
//                   min="0"
//                   step="1000"
//                   className="h-12 text-lg"
//                   required
//                 />
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="upper_range">Maximum Salary</Label>
//                 <Input
//                   id="upper_range"
//                   name="upper_range"
//                   value={formData.upper_range}
//                   onChange={handleChange}
//                   type="number"
//                   placeholder="0"
//                   min="0"
//                   step="1000"
//                   className="h-12 text-lg"
//                   required
//                 />
//               </div>
//             </div>

//             <div className="flex items-center space-x-2">
//               <Checkbox
//                 checked={formData.publish_salary_range}
//                 onCheckedChange={(val) => handleCheckbox("publish_salary_range", !!val)}
//                 id="publish_salary_range"
//               />
//               <Label htmlFor="publish_salary_range">Make salary range visible to candidates</Label>
//             </div>

//             {formData.lower_range && formData.upper_range && (
//               <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
//                 <CardContent className="p-4">
//                   <div className="text-center">
//                     <p className="text-sm text-muted-foreground">Salary Range Preview</p>
//                     <p className="text-2xl font-bold text-green-700">
//                       {formData.currency} {Number(formData.lower_range).toLocaleString()} -{" "}
//                       {Number(formData.upper_range).toLocaleString()}
//                     </p>
//                     <p className="text-sm text-muted-foreground">per {formData.salary_per.toLowerCase()}</p>
//                   </div>
//                 </CardContent>
//               </Card>
//             )}
//           </div>
//         )

//       default:
//         return null
//     }
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
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
//               <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
//                 Create Job Opening
//               </h1>
//             </div>
//             <p className="text-muted-foreground">Build your perfect job posting step by step</p>
//           </div>
//         </div>

//         {/* Progress Steps */}
//         <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
//           <CardContent className="p-6">
//             <div className="flex items-center justify-between mb-6">
//               <h3 className="font-semibold">Creation Progress</h3>
//               <Badge variant="outline">
//                 Step {currentStep} of {steps.length}
//               </Badge>
//             </div>
//             <Progress value={(currentStep / steps.length) * 100} className="h-2 mb-6" />

//             <div className="flex items-center justify-between">
//               {steps.map((step, index) => (
//                 <div key={step.id} className="flex items-center">
//                   <div className="flex flex-col items-center space-y-2">
//                     <div
//                       className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
//                         getStepStatus(step.id) === "completed"
//                           ? "bg-green-500 text-white"
//                           : getStepStatus(step.id) === "current"
//                             ? "bg-blue-500 text-white"
//                             : "bg-gray-200 text-gray-500"
//                       }`}
//                     >
//                       {getStepStatus(step.id) === "completed" ? <CheckCircle className="h-6 w-6" /> : step.icon}
//                     </div>
//                     <div className="text-center">
//                       <p className="text-sm font-medium">{step.title}</p>
//                     </div>
//                   </div>
//                   {index < steps.length - 1 && <div className="w-24 h-0.5 bg-gray-200 mx-4 mt-6"></div>}
//                 </div>
//               ))}
//             </div>
//           </CardContent>
//         </Card>

//         {/* Main Form */}
//         <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm">
//           <CardContent className="p-8">
//             <form onSubmit={handleSubmit}>
//               {renderStepContent()}

//               {/* Navigation Buttons */}
//               <div className="flex justify-between mt-8 pt-6 border-t">
//                 <Button
//                   type="button"
//                   variant="outline"
//                   onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
//                   disabled={currentStep === 1}
//                   className="px-8"
//                 >
//                   Previous
//                 </Button>

//                 {currentStep < steps.length ? (
//                   <Button
//                     type="button"
//                     onClick={() => setCurrentStep(Math.min(steps.length, currentStep + 1))}
//                     className="px-8 bg-blue-600 hover:bg-blue-700"
//                   >
//                     Next Step
//                   </Button>
//                 ) : (
//                   <Button
//                     type="submit"
//                     disabled={loading}
//                     className="px-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
//                   >
//                     {loading ? "Creating..." : "Create Job Opening"}
//                   </Button>
//                 )}
//               </div>
//             </form>
//           </CardContent>
//         </Card>

//         {/* Status Alert */}
//         {status && (
//           <Alert variant={status.type === "error" ? "destructive" : "default"} className="border-0 shadow-lg">
//             <AlertCircle className="h-4 w-4" />
//             <AlertTitle>{status.type === "success" ? "Success!" : "Error"}</AlertTitle>
//             <AlertDescription>
//               {typeof status.message === "string" ? status.message : JSON.stringify(status.message)}
//             </AlertDescription>
//           </Alert>
//         )}
//       </div>
//     </div>
//   )
// }





"use client"
import { useEffect, useState } from "react"
import type React from "react"
import axios from "axios"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import {
  ArrowLeft,
  Briefcase,
  Building,
  MapPin,
  Users,
  DollarSign,
  Calendar,
  CheckCircle,
  AlertCircle,
  Globe,
  Clock,
  FileText,
  Sparkles,
} from "lucide-react"
import Link from "next/link"

// API Configuration - Update these with your credentials
export const API_BASE_URL = 'http://localhost:8000';
export const API_AUTH = {
  headers: {
    Authorization: `token 19381cf6f577ae0:b2ca674abcc0259`,
    'Content-Type': 'application/json',
  },
  withCredentials: true,
}

export default function CreateJobOpeningForm() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    job_title: "",
    designation: "",
    description: "",
    currency: "INR",
    lower_range: "",
    upper_range: "",
    publish_salary_range: false,
    company: "",
    employment_type: "",
    department: "",
    location: "",
    publish_on_website: false,
    posted_on: new Date().toISOString().split("T")[0],
    closes_on: "",
    status: "Open",
    salary_per: "Month",
  })

  const [options, setOptions] = useState({
    companies: [],
    departments: [],
    employment_types: [],
    designations: [],
    locations: [],
  })
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const steps = [
    { id: 1, title: "Job Details", icon: <Briefcase className="h-5 w-5" /> },
    { id: 2, title: "Company Info", icon: <Building className="h-5 w-5" /> },
    { id: 3, title: "Requirements", icon: <FileText className="h-5 w-5" /> },
    { id: 4, title: "Compensation", icon: <DollarSign className="h-5 w-5" /> },
  ]

  useEffect(() => {
    async function fetchOptions() {
      try {
        const [companies, departments, employment_types, designations, locations] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/resource/Company?fields=["name"]`, API_AUTH),
          axios.get(`${API_BASE_URL}/api/resource/Department?fields=["name"]`, API_AUTH),
          axios.get(`${API_BASE_URL}/api/resource/Employment Type?fields=["name"]`, API_AUTH),
          axios.get(`${API_BASE_URL}/api/resource/Designation?fields=["name"]`, API_AUTH),
          axios.get(`${API_BASE_URL}/api/resource/Location?fields=["name"]`, API_AUTH),
        ])
        setOptions({
          companies: companies.data.data.map((d: any) => d.name),
          departments: departments.data.data.map((d: any) => d.name),
          employment_types: employment_types.data.data.map((d: any) => d.name),
          designations: designations.data.data.map((d: any) => d.name),
          locations: locations.data.data.map((d: any) => d.name),
        })

        // Success toast for loading data
        toast({
          title: "Data Loaded Successfully",
          description: "All dropdown options have been loaded.",
          duration: 3000,
        })
      } catch (err) {
        console.error("Error fetching dropdowns", err)
        toast({
          variant: "destructive",
          title: "Failed to Load Data",
          description: "Could not load dropdown options. Please refresh the page.",
          duration: 5000,
        })
      }
    }
    fetchOptions()
  }, [toast])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleCheckbox = (name: string, value: boolean) => {
    setFormData({ ...formData, [name]: value })
  }

  const handleSelect = (name: string, value: string) => {
    setFormData({ ...formData, [name]: value })
  }

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!formData.job_title.trim()) {
          toast({
            variant: "destructive",
            title: "Job Title Required",
            description: "Please enter a job title to continue.",
            duration: 4000,
          })
          return false
        }
        if (!formData.designation) {
          toast({
            variant: "destructive",
            title: "Designation Required",
            description: "Please select a designation to continue.",
            duration: 4000,
          })
          return false
        }
        return true
      case 2:
        if (!formData.company) {
          toast({
            variant: "destructive",
            title: "Company Required",
            description: "Please select a company to continue.",
            duration: 4000,
          })
          return false
        }
        return true
      case 3:
        if (!formData.description.trim()) {
          toast({
            variant: "destructive",
            title: "Job Description Required",
            description: "Please provide a detailed job description.",
            duration: 4000,
          })
          return false
        }
        return true
      case 4:
        if (!formData.lower_range || !formData.upper_range) {
          toast({
            variant: "destructive",
            title: "Salary Range Required",
            description: "Please provide both minimum and maximum salary.",
            duration: 4000,
          })
          return false
        }
        const lowerRange = Number.parseFloat(formData.lower_range)
        const upperRange = Number.parseFloat(formData.upper_range)

        if (isNaN(lowerRange) || lowerRange <= 0) {
          toast({
            variant: "destructive",
            title: "Invalid Minimum Salary",
            description: "Minimum salary must be a positive number.",
            duration: 4000,
          })
          return false
        }
        if (isNaN(upperRange) || upperRange <= 0) {
          toast({
            variant: "destructive",
            title: "Invalid Maximum Salary",
            description: "Maximum salary must be a positive number.",
            duration: 4000,
          })
          return false
        }
        if (lowerRange >= upperRange) {
          toast({
            variant: "destructive",
            title: "Invalid Salary Range",
            description: "Minimum salary must be less than maximum salary.",
            duration: 4000,
          })
          return false
        }
        return true
      default:
        return true
    }
  }

  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(Math.min(steps.length, currentStep + 1))
      toast({
        title: "Step Completed",
        description: `${steps[currentStep - 1].title} information saved successfully.`,
        duration: 2000,
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateStep(currentStep)) {
      return
    }

    setLoading(true)

    // Show loading toast
    toast({
      title: "Creating Job Opening",
      description: "Please wait while we process your request...",
      duration: 2000,
    })

    const payload = {
      ...formData,
      lower_range: Number.parseFloat(formData.lower_range) || undefined,
      upper_range: Number.parseFloat(formData.upper_range) || undefined,
      status: formData.status,
      salary_per: formData.salary_per,
    }

    try {
      const res = await axios.post(
        `${API_BASE_URL}/api/method/resume.api.job_opening.create_job_opening`,
        payload,
        API_AUTH,
      )

      // Success toast with custom styling
      toast({
        title: "🎉 Job Opening Created Successfully!",
        description: `"${formData.job_title}" has been posted and is now live.`,
        duration: 6000,
        className: "bg-green-50 border-green-200",
      })

      // Reset form
      setFormData({
        job_title: "",
        designation: "",
        description: "",
        currency: "INR",
        lower_range: "",
        upper_range: "",
        publish_salary_range: false,
        company: "",
        employment_type: "",
        department: "",
        location: "",
        publish_on_website: false,
        posted_on: new Date().toISOString().split("T")[0],
        closes_on: "",
        status: "Open",
        salary_per: "Month",
      })

      // Reset to first step
      setCurrentStep(1)

      // Additional success actions
      setTimeout(() => {
        toast({
          title: "What's Next?",
          description: "You can now start collecting resumes for this position.",
          duration: 4000,
        })
      }, 2000)
    } catch (err: any) {
      console.error("Create job failed", err.response?.data || err)

      // Error toast with detailed information
      const errorMessage = err.response?.data?.message || "An unexpected error occurred while creating the job opening."

      toast({
        variant: "destructive",
        title: "❌ Failed to Create Job Opening",
        description: errorMessage,
        duration: 8000,
        action: (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // Retry logic could go here
              toast({
                title: "Retry",
                description: "Please check your information and try again.",
                duration: 3000,
              })
            }}
          >
            Retry
          </Button>
        ),
      })

      // Additional error handling
      if (err.response?.status === 401) {
        toast({
          variant: "destructive",
          title: "Authentication Error",
          description: "Your session may have expired. Please refresh the page.",
          duration: 6000,
        })
      } else if (err.response?.status >= 500) {
        toast({
          variant: "destructive",
          title: "Server Error",
          description: "There's an issue with our servers. Please try again later.",
          duration: 6000,
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const getStepStatus = (stepId: number) => {
    if (stepId < currentStep) return "completed"
    if (stepId === currentStep) return "current"
    return "pending"
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <Sparkles className="h-12 w-12 text-blue-500 mx-auto" />
              <h3 className="text-2xl font-bold">Let's Create Something Amazing</h3>
              <p className="text-muted-foreground">Start by defining the core details of your job opening</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="job_title" className="flex items-center space-x-2">
                  <Briefcase className="h-4 w-4" />
                  <span>Job Title</span>
                </Label>
                <Input
                  id="job_title"
                  name="job_title"
                  value={formData.job_title}
                  onChange={handleChange}
                  placeholder="e.g., Senior Full Stack Developer"
                  className="h-12 text-lg"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="designation" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Designation</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("designation", val)} value={formData.designation}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Designation" />
                  </SelectTrigger>
                  <SelectContent>
                    {options.designations.length === 0 && (
                      <SelectItem value="no-designations" disabled>
                        No designations available
                      </SelectItem>
                    )}
                    {options.designations.map((d) => (
                      <SelectItem key={d} value={d}>
                        {d}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="status" className="flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4" />
                  <span>Status</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("status", val)} value={formData.status}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Open">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Open</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="Closed">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>Closed</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="On Hold">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <span>On Hold</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="closes_on" className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4" />
                  <span>Application Deadline</span>
                </Label>
                <Input
                  id="closes_on"
                  name="closes_on"
                  value={formData.closes_on}
                  onChange={handleChange}
                  type="date"
                  className="h-12"
                />
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <Building className="h-12 w-12 text-emerald-500 mx-auto" />
              <h3 className="text-2xl font-bold">Company & Location Details</h3>
              <p className="text-muted-foreground">Define where and how your team will work</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="company" className="flex items-center space-x-2">
                  <Building className="h-4 w-4" />
                  <span>Company</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("company", val)} value={formData.company}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Company" />
                  </SelectTrigger>
                  <SelectContent>
                    {options.companies.length === 0 && (
                      <SelectItem value="no-companies" disabled>
                        No companies available
                      </SelectItem>
                    )}
                    {options.companies.map((c) => (
                      <SelectItem key={c} value={c}>
                        {c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Department</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("department", val)} value={formData.department}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Department" />
                  </SelectTrigger>
                  <SelectContent>
                    {options.departments.length === 0 && (
                      <SelectItem value="no-departments" disabled>
                        No departments available
                      </SelectItem>
                    )}
                    {options.departments.map((d) => (
                      <SelectItem key={d} value={d}>
                        {d}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="location" className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Work Location</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("location", val)} value={formData.location}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Location" />
                  </SelectTrigger>
                  <SelectContent>
                    {options.locations.length === 0 && (
                      <SelectItem value="no-locations" disabled>
                        No locations available
                      </SelectItem>
                    )}
                    {options.locations.map((l) => (
                      <SelectItem key={l} value={l}>
                        {l}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="employment_type" className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Employment Type</span>
                </Label>
                <Select onValueChange={(val) => handleSelect("employment_type", val)} value={formData.employment_type}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Employment Type" />
                  </SelectTrigger>
                  <SelectContent>
                    {options.employment_types.length === 0 && (
                      <SelectItem value="no-employment-types" disabled>
                        No employment types available
                      </SelectItem>
                    )}
                    {options.employment_types.map((e) => (
                      <SelectItem key={e} value={e}>
                        {e}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  checked={formData.publish_on_website}
                  onCheckedChange={(val) => handleCheckbox("publish_on_website", !!val)}
                  id="publish_on_website"
                />
                <Label htmlFor="publish_on_website" className="flex items-center space-x-2">
                  <Globe className="h-4 w-4" />
                  <span>Publish on company website</span>
                </Label>
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <FileText className="h-12 w-12 text-purple-500 mx-auto" />
              <h3 className="text-2xl font-bold">Job Requirements</h3>
              <p className="text-muted-foreground">Describe what you're looking for in detail</p>
            </div>

            <div className="space-y-4">
              <Label htmlFor="description" className="text-lg font-semibold">
                Job Description
              </Label>
              <Textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe the role, responsibilities, qualifications, and what makes this opportunity exciting..."
                rows={12}
                className="text-base leading-relaxed"
              />
              <p className="text-sm text-muted-foreground">
                💡 Tip: Include key responsibilities, required skills, experience level, and company culture highlights
              </p>
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <DollarSign className="h-12 w-12 text-green-500 mx-auto" />
              <h3 className="text-2xl font-bold">Compensation Package</h3>
              <p className="text-muted-foreground">Define the salary range and benefits</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <Select onValueChange={(val) => handleSelect("currency", val)} value={formData.currency}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Currency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INR">🇮🇳 INR - Indian Rupee</SelectItem>
                    <SelectItem value="USD">🇺🇸 USD - US Dollar</SelectItem>
                    <SelectItem value="EUR">🇪🇺 EUR - Euro</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="salary_per">Salary Period</Label>
                <Select onValueChange={(val) => handleSelect("salary_per", val)} value={formData.salary_per}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select Period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Month">Per Month</SelectItem>
                    <SelectItem value="Year">Per Year</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="lower_range">Minimum Salary</Label>
                <Input
                  id="lower_range"
                  name="lower_range"
                  value={formData.lower_range}
                  onChange={handleChange}
                  type="number"
                  placeholder="0"
                  min="0"
                  step="1000"
                  className="h-12 text-lg"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="upper_range">Maximum Salary</Label>
                <Input
                  id="upper_range"
                  name="upper_range"
                  value={formData.upper_range}
                  onChange={handleChange}
                  type="number"
                  placeholder="0"
                  min="0"
                  step="1000"
                  className="h-12 text-lg"
                  required
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                checked={formData.publish_salary_range}
                onCheckedChange={(val) => handleCheckbox("publish_salary_range", !!val)}
                id="publish_salary_range"
              />
              <Label htmlFor="publish_salary_range">Make salary range visible to candidates</Label>
            </div>

            {formData.lower_range && formData.upper_range && (
              <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
                <CardContent className="p-4">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Salary Range Preview</p>
                    <p className="text-2xl font-bold text-green-700">
                      {formData.currency} {Number(formData.lower_range).toLocaleString()} -{" "}
                      {Number(formData.upper_range).toLocaleString()}
                    </p>
                    <p className="text-sm text-muted-foreground">per {formData.salary_per.toLowerCase()}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )

      default:
        return null
    }
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
                Create Job Opening
              </h1>
            </div>
            <p className="text-muted-foreground">Build your perfect job posting step by step</p>
          </div>
        </div>

        {/* Progress Steps */}
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold">Creation Progress</h3>
              <Badge variant="outline">
                Step {currentStep} of {steps.length}
              </Badge>
            </div>
            <Progress value={(currentStep / steps.length) * 100} className="h-2 mb-6" />

            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className="flex flex-col items-center space-y-2">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
                        getStepStatus(step.id) === "completed"
                          ? "bg-green-500 text-white"
                          : getStepStatus(step.id) === "current"
                            ? "bg-blue-500 text-white"
                            : "bg-gray-200 text-gray-500"
                      }`}
                    >
                      {getStepStatus(step.id) === "completed" ? <CheckCircle className="h-6 w-6" /> : step.icon}
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-medium">{step.title}</p>
                    </div>
                  </div>
                  {index < steps.length - 1 && <div className="w-24 h-0.5 bg-gray-200 mx-4 mt-6"></div>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Form */}
        <Card className="border-0 shadow-xl bg-white/90 backdrop-blur-sm">
          <CardContent className="p-8">
            <form onSubmit={handleSubmit}>
              {renderStepContent()}

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8 pt-6 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                  disabled={currentStep === 1}
                  className="px-8"
                >
                  Previous
                </Button>

                {currentStep < steps.length ? (
                  <Button type="button" onClick={handleNextStep} className="px-8 bg-blue-600 hover:bg-blue-700">
                    Next Step
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    disabled={loading}
                    className="px-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Creating...</span>
                      </div>
                    ) : (
                      "Create Job Opening"
                    )}
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Toast Container */}
      <Toaster />
    </div>
  )
}
