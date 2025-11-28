import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography, Stepper, Step, StepLabel, StepContent } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

interface RoadmapDialogProps {
  open: boolean
  onClose: () => void
  resumeId: string
  jobTitle: string
}

interface RoadmapData {
  skills_gap: string[]
  learning_path: {
    title: string
    duration: string
    tasks: string[]
  }[]
  certifications: string[]
  projects: {
    title: string
    description: string
  }[]
}

export const RoadmapDialog = ({ open, onClose, resumeId, jobTitle }: RoadmapDialogProps) => {
  const { data: roadmap, isLoading, error, isError } = useQuery<RoadmapData>({
    queryKey: ['roadmap', resumeId, jobTitle],
    queryFn: async () => {
      try {
        console.log('Requesting roadmap for:', { resumeId, jobTitle })
        const response = await axios.post(`${API_URL}/career/roadmap`, {
          resume_id: resumeId,
          target_role: jobTitle,
        })
        console.log('Roadmap response received:', response.data)
        console.log('Response structure:', {
          skills_gap: response.data?.skills_gap?.length || 0,
          learning_path: response.data?.learning_path?.length || 0,
          certifications: response.data?.certifications?.length || 0,
          projects: response.data?.projects?.length || 0
        })
        return response.data
      } catch (error) {
        console.error('Error fetching roadmap:', error)
        throw new Error(error instanceof Error ? error.message : 'Failed to fetch roadmap')
      }
    },
    enabled: open && !!resumeId && !!jobTitle, // Only fetch when dialog is open and we have required data
    retry: 2, // Retry failed requests twice
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  })

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>Career Roadmap: {jobTitle}</DialogTitle>
      <DialogContent>
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
            <Typography>Generating your personalized career roadmap...</Typography>
          </Box>
        )}
        
        {isError && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            p: 3, 
            color: 'error.main' 
          }}>
            <Typography variant="h6" gutterBottom>Error Loading Roadmap</Typography>
            <Typography sx={{ mb: 2, textAlign: 'center' }}>
              {error instanceof Error ? error.message : 'An error occurred while generating your career roadmap'}
            </Typography>
            <Typography variant="body2" sx={{ mb: 3, textAlign: 'center', color: 'text.secondary' }}>
              Please try again. If the problem persists, check the console for more details.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={onClose}
              >
                Close
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </Box>
          </Box>
        )}
        
        {!isLoading && !isError && roadmap && (
          <Box sx={{ mt: 2 }}>
            {/* Debug information */}
            {import.meta.env.DEV && (
              <Box sx={{ 
                mb: 2, 
                p: 2, 
                bgcolor: 'grey.100', 
                borderRadius: 1,
                fontSize: '0.8rem'
              }}>
                <Typography variant="caption" fontWeight="bold">Debug Info:</Typography>
                <Typography variant="caption" display="block">
                  Data received: {roadmap ? 'Yes' : 'No'} | 
                  Skills gap: {roadmap?.skills_gap?.length || 0} | 
                  Learning path: {roadmap?.learning_path?.length || 0} | 
                  Certifications: {roadmap?.certifications?.length || 0} | 
                  Projects: {roadmap?.projects?.length || 0}
                </Typography>
                <Box component="pre" sx={{ 
                  fontSize: '0.7rem', 
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '200px',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(roadmap, null, 2)}
                </Box>
              </Box>
            )}
            
            <Box sx={{ display: 'grid', gap: 4 }}>
              {/* Skills Gap Analysis */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ 
                  borderBottom: 1, 
                  borderColor: 'divider',
                  pb: 1 
                }}>
                  Skills Gap Analysis
                </Typography>
                <Box sx={{ 
                  display: 'grid', 
                  gap: 1,
                  bgcolor: 'background.paper',
                  p: 2,
                  borderRadius: 1
                }}>
                  {roadmap.skills_gap && Array.isArray(roadmap.skills_gap) && roadmap.skills_gap.length > 0 ? (
                    roadmap.skills_gap.map((skill: string, index: number) => (
                      <Typography 
                        key={`skill-${index}`} 
                        variant="body2" 
                        sx={{
                          color: skill?.startsWith?.('Required:') ? 'error.main' : 'info.main',
                          display: 'flex',
                          alignItems: 'center',
                          '&:before': {
                            content: '"•"',
                            mr: 1
                          }
                        }}
                      >
                        {skill || 'Unknown skill'}
                      </Typography>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No skills gap data available
                    </Typography>
                  )}
                </Box>
              </Box>

              {/* Learning Path */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ 
                  borderBottom: 1, 
                  borderColor: 'divider',
                  pb: 1 
                }}>
                  Learning Path
                </Typography>
                <Stepper orientation="vertical" sx={{ 
                  bgcolor: 'background.paper',
                  p: 2,
                  borderRadius: 1
                }}>
                  {roadmap.learning_path && Array.isArray(roadmap.learning_path) && roadmap.learning_path.length > 0 ? (
                    roadmap.learning_path.map((step, index) => (
                      <Step key={index} active={true}>
                        <StepLabel>
                          <Typography variant="subtitle1">{step?.title || `Phase ${index + 1}`}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {step?.duration || 'Duration not specified'}
                          </Typography>
                        </StepLabel>
                        <StepContent>
                          <Box sx={{ display: 'grid', gap: 1, mt: 1 }}>
                            {step?.tasks && Array.isArray(step.tasks) ? (
                              step.tasks.map((task, taskIndex) => (
                                <Typography 
                                  key={taskIndex} 
                                  variant="body2"
                                  sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    '&:before': {
                                      content: '"•"',
                                      mr: 1
                                    }
                                  }}
                                >
                                  {task || 'Task not specified'}
                                </Typography>
                              ))
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                No tasks defined for this phase
                              </Typography>
                            )}
                          </Box>
                        </StepContent>
                      </Step>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No learning path data available
                    </Typography>
                  )}
                </Stepper>
              </Box>

              {/* Certifications */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ 
                  borderBottom: 1, 
                  borderColor: 'divider',
                  pb: 1 
                }}>
                  Recommended Certifications
                </Typography>
                <Box sx={{ 
                  display: 'grid', 
                  gap: 1,
                  bgcolor: 'background.paper',
                  p: 2,
                  borderRadius: 1
                }}>
                  {roadmap.certifications && Array.isArray(roadmap.certifications) && roadmap.certifications.length > 0 ? (
                    roadmap.certifications.map((cert: string, index: number) => (
                      <Typography 
                        key={`cert-${index}`} 
                        variant="body2"
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          '&:before': {
                            content: '"•"',
                            mr: 1
                          }
                        }}
                      >
                        {cert || 'Certification not specified'}
                      </Typography>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No certification recommendations available
                    </Typography>
                  )}
                </Box>
              </Box>

              {/* Projects */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ 
                  borderBottom: 1, 
                  borderColor: 'divider',
                  pb: 1 
                }}>
                  Suggested Projects
                </Typography>
                <Box sx={{ 
                  display: 'grid', 
                  gap: 3,
                  bgcolor: 'background.paper',
                  p: 2,
                  borderRadius: 1
                }}>
                  {roadmap.projects && Array.isArray(roadmap.projects) && roadmap.projects.length > 0 ? (
                    roadmap.projects.map((project, index) => (
                      <Box key={index}>
                        <Typography 
                          variant="subtitle1" 
                          color="primary"
                          gutterBottom
                        >
                          {project?.title || `Project ${index + 1}`}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{ pl: 2, borderLeft: 2, borderColor: 'primary.main' }}
                        >
                          {project?.description || 'Project description not available'}
                        </Typography>
                      </Box>
                    ))
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No project suggestions available
                    </Typography>
                  )}
                </Box>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Button 
          onClick={onClose} 
          variant="outlined" 
          color="primary"
          disabled={isLoading}
        >
          Close
        </Button>
        {!isLoading && !isError && roadmap && (
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => {
              // Could add functionality to save or export roadmap
              console.log('Save roadmap:', roadmap)
            }}
          >
            Save Roadmap
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}
