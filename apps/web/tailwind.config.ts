import type { Config } from 'tailwindcss';

/**
 * Tailwind theme keys map to the CSS custom properties declared in
 * `src/styles/tokens.css` (every value transcribed from DRD §2). Components
 * reference tokens through utility classes (e.g. `bg-card`, `text-primary`,
 * `rounded-lg`) so a future theme swap only touches the token file — never the
 * component styles. Spacing is left at Tailwind's default 4px-based scale,
 * which already matches DRD §2.11.
 */
const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--primary)',
          hover: 'var(--primary-hover)',
          light: 'var(--primary-light)',
          lighter: 'var(--primary-lighter)',
          text: 'var(--primary-text)',
        },
        logo: 'var(--logo-color)',
        bg: {
          app: 'var(--bg-app)',
          sidebar: 'var(--bg-sidebar)',
          card: 'var(--bg-card)',
          surface: 'var(--bg-surface)',
          hover: 'var(--bg-hover)',
          input: 'var(--bg-input)',
          column: 'var(--bg-column)',
          login: 'var(--login-bg)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
          surface: 'var(--text-on-surface)',
          sidebar: 'var(--sidebar-text)',
        },
        border: {
          DEFAULT: 'var(--border-color)',
          input: 'var(--border-input)',
          sidebar: 'var(--border-sidebar)',
        },
        divider: 'var(--divider)',
        // Status (DRD §2.6) — fg/bg pairs.
        status: {
          backlog: 'var(--status-backlog-fg)',
          'backlog-bg': 'var(--status-backlog-bg)',
          todo: 'var(--status-todo-fg)',
          'todo-bg': 'var(--status-todo-bg)',
          progress: 'var(--status-progress-fg)',
          'progress-bg': 'var(--status-progress-bg)',
          review: 'var(--status-review-fg)',
          'review-bg': 'var(--status-review-bg)',
          done: 'var(--status-done-fg)',
          'done-bg': 'var(--status-done-bg)',
          cancelled: 'var(--status-cancelled-fg)',
          'cancelled-bg': 'var(--status-cancelled-bg)',
        },
        // Priority (DRD §2.7).
        priority: {
          urgent: 'var(--priority-urgent)',
          high: 'var(--priority-high)',
          medium: 'var(--priority-medium)',
          low: 'var(--priority-low)',
        },
        // Semantic (DRD §2.8).
        semantic: {
          error: 'var(--semantic-error)',
          'error-bg': 'var(--semantic-error-bg)',
          success: 'var(--semantic-success)',
          warning: 'var(--semantic-warning)',
        },
        // Fixed label palette (DRD §2.9).
        label: {
          blue: 'var(--label-blue)',
          green: 'var(--label-green)',
          red: 'var(--label-red)',
          purple: 'var(--label-purple)',
          amber: 'var(--label-amber)',
          pink: 'var(--label-pink)',
          cyan: 'var(--label-cyan)',
          orange: 'var(--label-orange)',
        },
        // Fixed avatar palette (DRD §2.10).
        avatar: {
          purple: 'var(--avatar-purple)',
          blue: 'var(--avatar-blue)',
          green: 'var(--avatar-green)',
          amber: 'var(--avatar-amber)',
          rose: 'var(--avatar-rose)',
          cyan: 'var(--avatar-cyan)',
        },
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        DEFAULT: 'var(--radius)',
        lg: 'var(--radius-lg)',
        badge: '10px',
        chip: '12px',
      },
      boxShadow: {
        card: 'var(--shadow-card)',
        'card-hover': 'var(--shadow-card-hover)',
        panel: 'var(--shadow-panel)',
        modal: 'var(--shadow-modal)',
        dropdown: 'var(--shadow-dropdown)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', "'Segoe UI'", 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
      ringColor: {
        primary: 'var(--primary-ring)',
      },
    },
  },
  plugins: [],
};

export default config;
