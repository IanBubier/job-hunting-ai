// Placeholder API helpers
async function postSearch(payload) {
  const resp = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return resp.json();
}

export { postSearch };
