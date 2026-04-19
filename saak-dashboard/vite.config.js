import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

function terminalLogsPlugin() {
  return {
    name: 'terminal-logs-plugin',
    configureServer(server) {
      server.middlewares.use('/api/terminal-logs', (req, res) => {
        try {
          const logPath = path.resolve(__dirname, '../terminal_stream.log')
          if (!fs.existsSync(logPath)) {
             res.statusCode = 200
             res.end(JSON.stringify({ logs: ['Esperando inicialización de terminal...'] }))
             return
          }
          const data = fs.readFileSync(logPath, 'utf8')
          // Extract last 100 lines
          const lines = data.trim().split('\n').slice(-100)
          res.statusCode = 200
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ logs: lines }))
        } catch (err) {
          res.statusCode = 500
          res.end(JSON.stringify({ error: err.message }))
        }
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), terminalLogsPlugin()],
  envDir: '../',
})
