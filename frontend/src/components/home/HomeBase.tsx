import type { ReactNode } from 'react';

interface HomeBaseProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function HomeBase({ title, subtitle, children }: HomeBaseProps) {
  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>{title}</h1>
      {subtitle && (
        <p style={{ color: '#666', marginBottom: 24 }}>{subtitle}</p>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
        {children}
      </div>
    </div>
  );
}