import './globals.css';
import Link from 'next/link';

export const metadata = { title: 'NutriRisk AI', description: 'Clinical malnutrition risk screening demo' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <Link className="logo" href="/">NutriRisk AI</Link>
          <div className="nav-links">
            <Link href="/">Dashboard</Link>
            <Link href="/patients">Patients</Link>
            <Link href="/analytics">Analytics</Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
