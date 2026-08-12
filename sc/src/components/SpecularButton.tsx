import type { ButtonHTMLAttributes, MouseEvent } from "react"
import { useCallback, useRef } from "react"
import "./SpecularButton.css"

type SpecularButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost"
}

export default function SpecularButton({
  className = "",
  children,
  onMouseMove,
  onMouseLeave,
  variant = "primary",
  ...props
}: SpecularButtonProps) {
  const buttonRef = useRef<HTMLButtonElement | null>(null)

  const handleMouseMove = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const button = buttonRef.current
      if (!button) return
      const rect = button.getBoundingClientRect()
      const x = ((event.clientX - rect.left) / rect.width) * 100
      const y = ((event.clientY - rect.top) / rect.height) * 100
      button.style.setProperty("--mouse-x", `${x}%`)
      button.style.setProperty("--mouse-y", `${y}%`)
      onMouseMove?.(event)
    },
    [onMouseMove]
  )

  const handleMouseLeave = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const button = buttonRef.current
      if (button) {
        button.style.setProperty("--mouse-x", "50%")
        button.style.setProperty("--mouse-y", "50%")
      }
      onMouseLeave?.(event)
    },
    [onMouseLeave]
  )

  return (
    <button
      ref={buttonRef}
      className={`specular-button specular-button--${variant} ${className}`.trim()}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {children}
    </button>
  )
}
