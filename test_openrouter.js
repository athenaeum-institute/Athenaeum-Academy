
async function test() {
  const FALLBACK_API_KEY = 'sk-or-v1-YOUR_API_KEY_HERE';
  const openAiPayload = {
    model: 'openrouter/free',
    messages: [{role: 'user', content: 'hello'}],
  };

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${FALLBACK_API_KEY}`,
      'HTTP-Referer': 'https://athenaeumacademy.com',
      'X-Title': 'Athenaeum Assistant'
    },
    body: JSON.stringify(openAiPayload)
  });

  const text = await response.text();
  console.log('Status:', response.status);
  console.log('Response:', text);
}

test();
