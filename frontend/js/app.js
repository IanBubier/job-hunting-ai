document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('search-form');
  const resultsContainer = document.getElementById('results');
  
  if (!form) return;
  
  const searchForm = new SearchForm(form);
  
  searchForm.handleSubmit(async (err, data) => {
    if (err) {
      alert(err.message);
      return;
    }
    // DEBUG: print data before sending
    console.log('Submitting search:', data);
    resultsContainer.innerHTML = '<p>Loading...</p>';

    try {
      const resp = await fetch('/search/results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const html = await resp.text();

      // Replace the page with results.html rendered from Flask
      document.open();
      document.write(html);
      document.close();
    } catch (e) {
      resultsContainer.innerHTML = `<p class="error">Search failed: ${e.message}</p>`;
    }
  });
});
