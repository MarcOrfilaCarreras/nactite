module.exports = {
  content: [
    "./routes/**/*.html",
    "./routes/**/*.js",
    "./templates/**/*.html",
    "./templates/**/*.js",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      animation: {
        fadeInUp: 'fadeInUp 0.5s',
        fadeOutUp: 'fadeOutUp 0.5s forwards'
      }
    },
  },
  plugins: [],
};
