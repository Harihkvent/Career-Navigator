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
        const response = await axios.post(`${API_URL}/career/roadmap`, {
          resume_id: resumeId,
          target_role: jobTitle,
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
            <Typography>{error instanceof Error ? error.message : 'An error occurred'}</Typography>
            <Button 
              variant="contained" 
              color="primary" 
              sx={{ mt: 2 }}
              onClick={onClose}
            >
              Close
            </Button>
          </Box>
        )}
        
        {!isLoading && !isError && roadmap && (
          <Box sx={{ mt: 2 }}>
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
                  {roadmap.skills_gap.map((skill: string) => (
                    <Typography 
                      key={skill} 
                      variant="body2" 
                      sx={{
                        color: skill.startsWith('Required:') ? 'error.main' : 'info.main',
                        display: 'flex',
                        alignItems: 'center',
                        '&:before': {
                          content: '"•"',
                          mr: 1
                        }
                      }}
                    >
                      {skill}
                    </Typography>
                  ))}
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
                  {roadmap.learning_path.map((step, index) => (
                    <Step key={index} active={true}>
                      <StepLabel>
                        <Typography variant="subtitle1">{step.title}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {step.duration}
                        </Typography>
                      </StepLabel>
                      <StepContent>
                        <Box sx={{ display: 'grid', gap: 1, mt: 1 }}>
                          {step.tasks.map((task, taskIndex) => (
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
                              {task}
                            </Typography>
                          ))}
                        </Box>
                      </StepContent>
                    </Step>
                  ))}
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
                  {roadmap.certifications.map((cert: string) => (
                    <Typography 
                      key={cert} 
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
                      {cert}
                    </Typography>
                  ))}
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
                  {roadmap.projects.map((project, index) => (
                    <Box key={index}>
                      <Typography 
                        variant="subtitle1" 
                        color="primary"
                        gutterBottom
                      >
                        {project.title}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{ pl: 2, borderLeft: 2, borderColor: 'primary.main' }}
                      >
                        {project.description}
                      </Typography>
                    </Box>
                  ))}
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
