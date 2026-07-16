import ThemeToggle from './components/ThemeToggle'
import './globals.css'

export const metadata = {
  title: 'Log Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeToggle />
        {children}
      </body>
    </html>
  )
}
