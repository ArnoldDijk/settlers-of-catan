import type { ButtonHTMLAttributes, CSSProperties } from 'react';

// Port of the design system's Button (components/core/Button.jsx).

type Variant = 'primary' | 'accent' | 'secondary' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  pill?: boolean;
}

const SIZES: Record<Size, { fontSize: number; padding: string; gap: number; radius: number }> = {
  sm: { fontSize: 14, padding: '8px 16px', gap: 8, radius: 10 },
  md: { fontSize: 16, padding: '12px 22px', gap: 10, radius: 12 },
  lg: { fontSize: 18, padding: '15px 30px', gap: 12, radius: 14 },
};

const VARIANTS: Record<Variant, CSSProperties> = {
  primary: { background: 'var(--bb-ink-900)', color: '#fff', border: '2px solid var(--bb-ink-900)' },
  accent: { background: 'var(--bb-mauve)', color: '#fff', border: '2px solid var(--bb-mauve)' },
  secondary: { background: '#fff', color: 'var(--bb-ink-900)', border: '2px solid var(--bb-ink-900)' },
  ghost: { background: 'transparent', color: 'var(--bb-ink-700)', border: '2px solid transparent' },
};

export function Button({ variant = 'primary', size = 'md', pill = false, disabled = false, style, children, ...rest }: Props) {
  const s = SIZES[size];
  return (
    <button
      type="button"
      disabled={disabled}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: s.gap,
        fontFamily: 'var(--font-display)',
        fontWeight: 600,
        fontSize: s.fontSize,
        lineHeight: 1,
        padding: s.padding,
        borderRadius: pill ? 999 : s.radius,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.45 : 1,
        transition:
          'transform var(--duration-fast) var(--ease-standard), filter var(--duration-fast) var(--ease-standard), box-shadow var(--duration-fast) var(--ease-standard)',
        ...VARIANTS[variant],
        ...style,
      }}
      onMouseDown={e => { if (!disabled) e.currentTarget.style.transform = 'scale(0.97)'; }}
      onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)'; }}
      onMouseEnter={e => { if (!disabled) e.currentTarget.style.filter = 'brightness(1.06)'; }}
      onMouseLeave={e => { e.currentTarget.style.filter = 'none'; e.currentTarget.style.transform = 'scale(1)'; }}
      {...rest}
    >
      {children}
    </button>
  );
}
