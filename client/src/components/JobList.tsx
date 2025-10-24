import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  LinearProgress,
  Button,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import './JobList.css'
import { RoadmapDialog } from './RoadmapDialog'

const API_URL = import.meta.env.VITE_API_URL

interface Job {
  job_id: string
  title: string
  company: string
  score: number
  match_percentage: string
}

interface JobListProps {
  resumeId: string | null
}

export const JobList = ({ resumeId }: JobListProps) => {
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['jobs', resumeId],
    queryFn: async () => {
      if (!resumeId) return []
      const response = await axios.get(`${API_URL}/jobs/match/${resumeId}`)
      return response.data
    },
    enabled: !!resumeId,
  })

  if (!resumeId) {
    return null
  }

  if (isLoading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Typography color="error" sx={{ mt: 2 }}>
        Error loading job matches
      </Typography>
    )
  }

  return (
    <Box sx={{ mt: 4 }}>
      <RoadmapDialog
        open={!!selectedJob}
        onClose={() => setSelectedJob(null)}
        resumeId={resumeId}
        jobTitle={selectedJob || ''}
      />
      <Typography variant="h5" gutterBottom>
        Matching Jobs
      </Typography>
      {jobs?.length === 0 ? (
        <Typography color="text.secondary">
          No matching jobs found. Please try uploading a different resume.
        </Typography>
      ) : (
        <Box className="job-list">
          {jobs?.map((job: Job) => (
          <Card key={job.job_id} className="job-card">
            <CardContent>
              <Typography variant="h6">{job.title}</Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {job.company}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Match Score
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={job.score * 100}
                    sx={{ flexGrow: 1 }}
                  />
                  <Typography variant="body2">{job.match_percentage}</Typography>
                </Box>
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="outlined" 
                    size="small"
                    onClick={() => setSelectedJob(job.title)}
                  >
                    View Career Roadmap
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
      )}
    </Box>
  )
}