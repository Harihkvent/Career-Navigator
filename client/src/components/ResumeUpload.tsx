import { useState } from 'react'
import { Button, Box, Typography, CircularProgress } from '@mui/material'
import { useQueryClient, useMutation } from '@tanstack/react-query'
import axios from 'axios'
import './ResumeUpload.css'

const API_URL = import.meta.env.VITE_API_URL

interface ResumeUploadProps {
  onUploadSuccess: (id: string) => void
}

export const ResumeUpload = ({ onUploadSuccess }: ResumeUploadProps) => {
  const [file, setFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await axios.post(`${API_URL}/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resume'] })
      onUploadSuccess(data.id)
    },
  })

  const handleUpload = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    uploadMutation.mutate(formData)
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Career Path Navigator
      </Typography>
      <div className="upload-container">
        <label htmlFor="resume-file" className="resume-label">Upload your resume</label>
        <input
          id="resume-file"
          className="resume-input"
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          title="Choose a resume file"
          placeholder="Select resume file"
        />
      </div>
      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={!file || uploadMutation.isPending}
      >
        {uploadMutation.isPending ? (
          <CircularProgress size={24} />
        ) : (
          'Upload Resume'
        )}
      </Button>
      {uploadMutation.isSuccess && (
        <Typography color="success.main" sx={{ mt: 2 }}>
          Resume uploaded successfully!
        </Typography>
      )}
      {uploadMutation.isError && (
        <Typography color="error.main" sx={{ mt: 2 }}>
          Error uploading resume. Please try again.
        </Typography>
      )}
    </Box>
  )
}