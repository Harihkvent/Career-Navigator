import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider, createTheme } from '@mui/material'
import CssBaseline from '@mui/material/CssBaseline'
import { ResumeUpload } from './components/ResumeUpload'
import { JobList } from './components/JobList'

const queryClient = new QueryClient()

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  const [resumeId, setResumeId] = useState<string | null>(null)

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div className="app-container">
          <div className="content-wrapper">
            <ResumeUpload onUploadSuccess={(id) => setResumeId(id)} />
            <JobList resumeId={resumeId} />
          </div>
        </div>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
