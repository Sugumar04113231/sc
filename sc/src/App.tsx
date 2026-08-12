import SpecularButton from "./components/SpecularButton"

export function App() {
  return (
    <div className="flex min-h-svh items-center justify-center p-6">
      <div className="flex max-w-xl min-w-0 flex-col gap-4 rounded-2xl border border-white/10 bg-background/70 p-8 text-sm leading-loose shadow-2xl backdrop-blur">
        <div>
          <h1 className="text-2xl font-semibold">Project ready!</h1>
          <p>Your custom cursor grid is now active as the global background.</p>
          <p>
            Move your pointer around the screen to see the effect ripple across
            the app.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <SpecularButton type="button">Primary action</SpecularButton>
          <SpecularButton type="button" variant="secondary">
            Secondary action
          </SpecularButton>
        </div>
        <div className="font-mono text-xs text-muted-foreground">
          (Press <kbd>d</kbd> to toggle dark mode)
        </div>
      </div>
    </div>
  )
}

export default App
