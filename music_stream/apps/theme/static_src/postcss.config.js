module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
    "postcss-simple-vars": {},
    "postcss-nested": {}
  },
  content: [
    '../../templates/**/*.html',  // Укажите пути к шаблонам
    '../../**/templates/**/*.html',
  ],
 
  theme: {
    extend: {
      animation: {
        'slide-in-right': 'slideInRight 0.5s ease-out forwards',
        'slide-out-right': 'slideOutRight 0.5s ease-in forwards',
      },
      keyframes: {
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideOutRight: {
          '0%': { transform: 'translateX(0)', opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' },
        },
      }
    }
  },
  // ...
}


