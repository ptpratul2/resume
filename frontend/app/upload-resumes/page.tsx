"use client"
import { useEffect, useState } from "react"
import type React from "react"
import axios from "axios"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { API_AUTH, API_BASE_URL } from "../create-job/page"
import {
  Upload,
  FileText,
  ArrowLeft,
  Briefcase,
  Users,
  MapPin,
  CheckCircle,
  Cloud,
  Zap,
  Target,
  TrendingUp,
  Clock,
  Building,
  X,
  FileCheck,
  Trash2,
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface JobOpening {
  name: string
  job_title: string
  designation: string
  company?: string
  location?: string
  department?: string
}

export default function ResumeUploader() {
  const [jobs, setJobs] = useState<JobOpening[]>([])
  const [selectedJobId, setSelectedJobId] = useState("")
  const [selectedJob, setSelectedJob] = useState<JobOpening | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const [processedFiles, setProcessedFiles] = useState<string[]>([])
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await axios.get(
          `${API_BASE_URL}/api/resource/Job Opening?fields=["name","job_title","designation","company","location","department"]`,
          API_AUTH,
        )
        setJobs(res.data.data)

        toast({
          title: "Job Openings Loaded",
          description: `Found ${res.data.data.length} active job openings.`,
          duration: 3000,
        })
      } catch (err) {
        console.error("Failed to fetch jobs", err)
        toast({
          variant: "destructive",
          title: "Failed to Load Jobs",
          description: "Could not fetch job openings. Please refresh the page.",
          duration: 5000,
        })
      }
    }
    fetchJobs()
  }, [toast])

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    const pdfFiles = droppedFiles.filter((file) => file.type === "application/pdf")
    const nonPdfFiles = droppedFiles.filter((file) => file.type !== "application/pdf")

    if (nonPdfFiles.length > 0) {
      toast({
        variant: "destructive",
        title: "Invalid File Types",
        description: `${nonPdfFiles.length} file(s) were skipped. Only PDF files are allowed.`,
        duration: 4000,
      })
    }

    if (pdfFiles.length > 0) {
      setFiles((prev) => [...prev, ...pdfFiles])
      toast({
        title: "Files Added",
        description: `${pdfFiles.length} PDF file(s) added successfully.`,
        duration: 3000,
      })
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      const pdfFiles = selectedFiles.filter((file) => file.type === "application/pdf")
      const nonPdfFiles = selectedFiles.filter((file) => file.type !== "application/pdf")

      if (nonPdfFiles.length > 0) {
        toast({
          variant: "destructive",
          title: "Invalid File Types",
          description: `${nonPdfFiles.length} file(s) were skipped. Only PDF files are allowed.`,
          duration: 4000,
        })
      }

      if (pdfFiles.length > 0) {
        setFiles((prev) => [...prev, ...pdfFiles])
        toast({
          title: "Files Selected",
          description: `${pdfFiles.length} PDF file(s) selected for upload.`,
          duration: 3000,
        })
      }
    }
  }

  const removeFile = (index: number) => {
    const fileName = files[index].name
    setFiles((prev) => prev.filter((_, i) => i !== index))
    toast({
      title: "File Removed",
      description: `${fileName} has been removed from the upload queue.`,
      duration: 2000,
    })
  }

  const clearAllFiles = () => {
    const fileCount = files.length
    setFiles([])
    toast({
      title: "All Files Cleared",
      description: `${fileCount} file(s) removed from the upload queue.`,
      duration: 3000,
    })
  }

  const handleJobSelect = (jobId: string) => {
    setSelectedJobId(jobId)
    const job = jobs.find((j) => j.name === jobId)
    setSelectedJob(job || null)

    if (job) {
      toast({
        title: "Job Selected",
        description: `Selected "${job.job_title}" for resume uploads.`,
        duration: 3000,
      })
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (files.length === 0) {
      toast({
        variant: "destructive",
        title: "No Files Selected",
        description: "Please select at least one PDF resume file to upload.",
        duration: 4000,
      })
      return
    }

    if (!selectedJobId) {
      toast({
        variant: "destructive",
        title: "No Job Selected",
        description: "Please select a job opening before uploading resumes.",
        duration: 4000,
      })
      return
    }

    setIsLoading(true)
    setUploadProgress(0)
    setProcessedFiles([])

    // Show initial loading toast
    toast({
      title: "🚀 Starting Upload Process",
      description: `Processing ${files.length} resume(s) with AI analysis...`,
      duration: 3000,
    })

    try {
      const successfulUploads: string[] = []
      const failedUploads: string[] = []

      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        try {
          const formData = new FormData()
          formData.append("files", file)
          formData.append("job_opening", selectedJobId)
          
          // Special config for file upload to avoid 417 error
          const uploadConfig = {
            headers: {
              Authorization: API_AUTH.headers.Authorization,
              // Don't set Content-Type - let browser set it with boundary
            },
            withCredentials: true,
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
            timeout: 300000, // 5 minutes timeout for large files
          }
          
          await axios.post(
            `${API_BASE_URL}/api/method/resume.api.upload_and_process.upload_and_process`, 
            formData, 
            uploadConfig
          )
          successfulUploads.push(file.name)
          setProcessedFiles((prev) => [...prev, file.name])
          
          const progress = ((i + 1) / files.length) * 100
          setUploadProgress(progress)

          // Show progress toast for each file
          toast({
            title: `Processing ${file.name}`,
            description: `File ${i + 1} of ${files.length} processed successfully.`,
            duration: 2000,
          })

          //navigation


        } catch (fileError) {
          console.error(`Failed to upload ${file.name}:`, fileError)
          failedUploads.push(file.name)
        }
      }

      // Final success/error summary
      if (successfulUploads.length === files.length) {
        toast({
          title: "🎉 All Resumes Processed Successfully!",
          description: `${successfulUploads.length} resume(s) uploaded and analyzed. Candidates are now in your pipeline.`,
          duration: 6000,
          className: "bg-green-50 border-green-200",
        })

// Navigate to interview schedule
        setTimeout(() => {
        router.push("/interview")
        }, 2000)


      } else if (successfulUploads.length > 0) {
        toast({
          title: "⚠️ Partial Upload Success",
          description: `${successfulUploads.length} of ${files.length} resumes processed successfully.`,
          duration: 5000,
          className: "bg-yellow-50 border-yellow-200",
        })
      }

      if (failedUploads.length > 0) {
        toast({
          variant: "destructive",
          title: "Some Uploads Failed",
          description: `${failedUploads.length} file(s) failed to upload: ${failedUploads.slice(0, 2).join(", ")}${failedUploads.length > 2 ? "..." : ""}`,
          duration: 8000,
          action: (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                toast({
                  title: "Retry Failed Uploads",
                  description: "Please check the files and try uploading them again.",
                  duration: 3000,
                })
              }}
            >
              Retry
            </Button>
          ),
        })
      }

      // Clear successful uploads
      if (successfulUploads.length > 0) {
        setFiles((prev) => prev.filter((file) => !successfulUploads.includes(file.name)))

        if (successfulUploads.length === files.length) {
          setSelectedJobId("")
          setSelectedJob(null)

          // Show next steps toast
          setTimeout(() => {
            toast({
              title: "What's Next?",
              description: "You can now review candidates and schedule interviews.",
              duration: 4000,
            })
          }, 2000)
        }
      }
    } catch (err) {
      console.error("Upload failed", err)
      toast({
        variant: "destructive",
        title: "❌ Upload Process Failed",
        description: "An unexpected error occurred during the upload process.",
        duration: 6000,
        action: (
          <Button variant="outline" size="sm" onClick={() => handleUpload(e)}>
            Retry All
          </Button>
        ),
      })
    } finally {
      setIsLoading(false)
      setUploadProgress(0)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50">
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
              <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                Resume Collection Hub
              </h1>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Briefcase className="h-5 w-5 text-emerald-600" />
                <span className="text-2xl font-bold text-emerald-600">{jobs.length}</span>
              </div>
              <div className="text-sm text-muted-foreground">Active Job Openings</div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Zap className="h-5 w-5 text-yellow-600" />
                <span className="text-2xl font-bold text-yellow-600">Fast</span>
              </div>
              <div className="text-sm text-muted-foreground">Processing</div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Target className="h-5 w-5 text-purple-600" />
                <span className="text-2xl font-bold text-purple-600">Smart</span>
              </div>
              <div className="text-sm text-muted-foreground">Screening</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Job Selection */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Briefcase className="h-5 w-5" />
                  <span>Select Job Opening</span>
                </CardTitle>
                <CardDescription>Choose the position you're hiring for</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select value={selectedJobId} onValueChange={handleJobSelect}>
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Choose a job opening..." />
                  </SelectTrigger>
                  <SelectContent>
                    {jobs.map((job) => (
                      <SelectItem key={job.name} value={job.name}>
                        <div className="flex flex-col items-start">
                          <span className="font-medium">{job.job_title}</span>
                          <span className="text-sm text-muted-foreground">{job.designation}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {selectedJob && (
                  <Card className="bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-emerald-600" />
                        <span className="font-semibold text-emerald-800">Selected Position</span>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center space-x-2">
                          <Briefcase className="h-3 w-3 text-emerald-600" />
                          <span>{selectedJob.job_title}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Users className="h-3 w-3 text-emerald-600" />
                          <span>{selectedJob.designation}</span>
                        </div>
                        {selectedJob.company && (
                          <div className="flex items-center space-x-2">
                            <Building className="h-3 w-3 text-emerald-600" />
                            <span>{selectedJob.company}</span>
                          </div>
                        )}
                        {selectedJob.location && (
                          <div className="flex items-center space-x-2">
                            <MapPin className="h-3 w-3 text-emerald-600" />
                            <span>{selectedJob.location}</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>

            {/* Upload Progress */}
            {isLoading && (
              <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Processing Resumes</span>
                      <span className="text-sm text-muted-foreground">{Math.round(uploadProgress)}%</span>
                    </div>
                    <Progress value={uploadProgress} className="h-2" />
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <TrendingUp className="h-4 w-4" />
                      <span>AI is analyzing and matching candidates...</span>
                    </div>
                    {processedFiles.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Recently processed:</p>
                        {processedFiles.slice(-3).map((fileName, index) => (
                          <div key={index} className="flex items-center space-x-2 text-xs">
                            <FileCheck className="h-3 w-3 text-green-500" />
                            <span className="truncate">{fileName}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* File Upload */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>Upload Resumes</span>
                </CardTitle>
                <CardDescription>Drag & drop PDF files or click to browse</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpload} className="space-y-6">
                  {/* Drag & Drop Area */}
                  <div
                    className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
                      dragActive
                        ? "border-emerald-500 bg-emerald-50"
                        : "border-gray-300 hover:border-emerald-400 hover:bg-emerald-50/50"
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <input
                      type="file"
                      multiple
                      accept="application/pdf"
                      onChange={handleFileSelect}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="space-y-4">
                      <div className="flex justify-center">
                        <div className="p-4 bg-emerald-100 rounded-full">
                          <Cloud className="h-8 w-8 text-emerald-600" />
                        </div>
                      </div>
                      <div>
                        <p className="text-lg font-semibold">Drop your resume files here</p>
                        <p className="text-muted-foreground">or click to browse your computer</p>
                      </div>
                      <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <FileText className="h-4 w-4" />
                          <span>PDF only</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Upload className="h-4 w-4" />
                          <span>Multiple files</span>
                        </div>
                        {/* <div className="flex items-center space-x-1">
                          <Zap className="h-4 w-4" />
                          <span>AI powered</span>
                        </div> */}
                      </div>
                    </div>
                  </div>

                  {/* File List */}
                  {files.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-base font-semibold">Selected Files ({files.length})</Label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={clearAllFiles}
                          className="text-red-500 hover:text-red-700 bg-transparent"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Clear All
                        </Button>
                      </div>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {files.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <FileText className="h-5 w-5 text-red-500" />
                              <div>
                                <p className="font-medium text-sm">{file.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                              </div>
                            </div>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFile(index)}
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isLoading || files.length === 0 || !selectedJobId}
                    className="w-full h-12 text-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Processing...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Upload className="h-5 w-5" />
                        <span>Upload & Process Resumes</span>
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Features
            <Card className="border-0 shadow-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-4">AI-Powered Resume Processing</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <Target className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold">Smart Matching</p>
                      <p className="text-sm text-emerald-100">AI matches skills to job requirements</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <Zap className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold">Instant Processing</p>
                      <p className="text-sm text-emerald-100">Get results in seconds</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <TrendingUp className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold">Score Ranking</p>
                      <p className="text-sm text-emerald-100">Automatic candidate scoring</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <Clock className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold">Time Saving</p>
                      <p className="text-sm text-emerald-100">Reduce screening time by 80%</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card> */}
          </div>
        </div>
      </div>

      {/* Toast Container */}
      <Toaster />
    </div>
  )
}
