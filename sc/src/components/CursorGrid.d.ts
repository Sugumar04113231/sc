declare module "@/components/CursorGrid.jsx" {
  import { ComponentType } from "react"

  type CursorGridProps = {
    cellSize?: number
    color?: string
    radius?: number
    falloff?: "linear" | "smooth" | "sharp"
    holdTime?: number
    fadeDuration?: number
    lineWidth?: number
    maxOpacity?: number
    fillOpacity?: number
    gridOpacity?: number
    cellRadius?: number
    clickPulse?: boolean
    pulseSpeed?: number
    className?: string
  }

  const CursorGrid: ComponentType<CursorGridProps>
  export default CursorGrid
}
