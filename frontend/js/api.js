// Placeholder API helpers
async function postSearch(payload) {
  const resp = await fetch('/search/results', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return resp.text();
}

export { postSearch };
