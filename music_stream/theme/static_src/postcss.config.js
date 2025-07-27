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
    extend: {},
  },

}

