document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('search-form');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    // Placeholder submit behavior
    const results = document.getElementById('results');
    results.textContent = 'Search submitted (frontend scaffold)';
  });
});
