export default {
  darkMode: 'class',

  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans KR"', 'ui-sans-serif', 'system-ui'],
      },

      colors: {
        /* ========== BACKGROUND SYSTEM ========== */
        bg: {
          DEFAULT: '#f8fafc',   // светлый фон (мягче чем white)
          dark: '#020617',      // глубокий тёмный фон
        },

        surface: {
          DEFAULT: '#ffffff',
          muted: '#f1f5f9',
          dark: '#0f172a',
          'dark-muted': '#111c2e',
        },

        /* ========== TEXT SYSTEM ========== */
        text: {
          DEFAULT: '#0f172a',
          muted: '#64748b',
          soft: '#94a3b8',
          dark: '#e2e8f0',
        },

        /* ========== BORDER / RING ========== */
        border: {
          DEFAULT: '#e2e8f0',
          soft: '#f1f5f9',
          dark: '#1e293b',
        },

        ring: {
          DEFAULT: '#22d3ee',
          dark: '#67e8f9',
        },

        /* ========== PRIMARY (УЛУЧШЕННЫЙ) ========== */
        primary: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4', // основной
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },

        /* hover/active alias */
        accent: '#22d3ee',

        /* ========== SECONDARY (НОРМАЛЬНЫЙ СЕРЫЙ) ========== */
        secondary: {
          DEFAULT: '#e2e8f0',
          hover: '#cbd5e1',
          dark: '#1e293b',
          'dark-hover': '#334155',
        },

        /* ========== STATUS COLORS ========== */
        success: {
          DEFAULT: '#22c55e',
          soft: '#dcfce7',
        },
        warning: {
          DEFAULT: '#f59e0b',
          soft: '#fef3c7',
        },
        error: {
          DEFAULT: '#ef4444',
          soft: '#fee2e2',
        },
      },

      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,0.08)',
        glow: '0 0 0 3px rgba(34,211,238,0.25)',
      },

      borderRadius: {
        xl: '1rem',
        '2xl': '1.25rem',
      },
    },
  },
}