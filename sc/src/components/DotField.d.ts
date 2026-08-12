declare module "@/components/DotField.jsx" {
  import { ComponentType, HTMLAttributes } from "react"

  export interface DotFieldProps extends HTMLAttributes<HTMLDivElement> {
    dotRadius?: number
    dotSpacing?: number
    cursorRadius?: number
    cursorForce?: number
    bulgeOnly?: boolean
    bulgeStrength?: number
    glowRadius?: number
    sparkle?: boolean
    waveAmplitude?: number
    gradientFrom?: string
    gradientTo?: string
    glowColor?: string
  }

  const DotField: ComponentType<DotFieldProps>
  export default DotField
}
