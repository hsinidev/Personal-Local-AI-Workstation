import './globals.css';
import React from 'react';

export const metadata = {
  title: 'Workstation Control | Personal Local AI Workstation',
  description: 'Local AI Workstation Infrastructure Control Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-950 text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
