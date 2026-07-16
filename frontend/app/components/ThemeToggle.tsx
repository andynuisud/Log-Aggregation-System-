'use client'

import { useState, useEffect } from 'react'

export default function ThemeToggle() {
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('theme')
    if (saved === 'dark') {
      setDark(true)
      document.body.classList.add('dark')
    }
  }, [])

  const toggle = () => {
    setDark(!dark)
    if (!dark) {
      document.body.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.body.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return (
    <button className="theme-toggle" onClick={toggle}>
      {dark ? 'Light' : 'Dark'}
    </button>
  )
}
