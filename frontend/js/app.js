document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('search-form');
  const resultsContainer = document.getElementById('results');
  
  if (!form) return;
  
  const searchForm = new SearchForm(form);
  
  searchForm.handleSubmit(async (err, data) => {
    if (err) {
      resultsContainer.innerHTML = `<p class="error">${err.message}. Please update your search and try again.</p>`;
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

      // Check if response is successful
      if (!resp.ok) {
        // Handle validation or server errors
        const errorData = await resp.json();
        let errorMessage = 'Search validation failed. Please check your input and try again.';

        if (errorData.error) {
          if (errorData.error.details) {
            // Show specific validation errors
            const errors = Object.entries(errorData.error.details)
              .map(([field, msg]) => `${field}: ${msg}`)
              .join('<br>');
            errorMessage = `<strong>Please fix the following:</strong><br>${errors}`;
          } else if (errorData.error.message) {
            errorMessage = errorData.error.message;
          }
        }

        resultsContainer.innerHTML = `<p class="error">${errorMessage}</p>`;
        return;
      }

      const html = await resp.text();

      // Replace the page with results.html rendered from Flask
      document.open();
      document.write(html);
      document.close();
    } catch (e) {
      resultsContainer.innerHTML = `<p class="error">Search failed: ${e.message}. Please try again.</p>`;
    }
  });
});
