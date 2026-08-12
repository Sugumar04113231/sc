import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import "./index.css"
import App from "./App.tsx"
import { ThemeProvider } from "@/components/theme-provider.tsx"
import DotField from "@/components/DotField.jsx"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
        <div className="pointer-events-none fixed inset-0 z-0">
          <DotField
            dotRadius={1.5}
            dotSpacing={14}
            bulgeStrength={67}
            glowRadius={160}
            sparkle={false}
            waveAmplitude={0}
          />
        </div>
        <div className="relative z-10 min-h-screen">
          <App />
        </div>
      </div>
    </ThemeProvider>
  </StrictMode>
)
