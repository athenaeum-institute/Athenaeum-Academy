// api/gemini.js
// Vercel Serverless Function to proxy Gemini API securely with Open Source Fallback

module.exports = async function handler(req, res) {
  // CORS configuration (allow frontend to call this endpoint)
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*'); 
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
  if (!GEMINI_API_KEY) {
    return res.status(500).json({ error: 'GEMINI_API_KEY environment variable is missing.' });
  }

  try {
    const GEMINI_MODEL = 'gemini-2.5-flash';
    const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;

    const response = await fetch(GEMINI_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      // Fallback Interception: If quota exceeded or Too Many Requests
      if (response.status === 429 || (errorData.error && errorData.error.message && errorData.error.message.toLowerCase().includes('quota'))) {
        console.warn('Gemini Quota Exceeded. Switching to Fallback API...');
        return await handleFallback(req, res);
      }
      
      return res.status(response.status).json(errorData);
    }

    const data = await response.json();
    return res.status(200).json(data);

  } catch (error) {
    console.error('Error proxying to Gemini:', error);
    return res.status(500).json({ error: 'Internal Server Error', details: error.message });
  }
}

// ----------------------------------------------------------------------
// FALLBACK HANDLER (Uses Groq LLaMA-3 by default)
// ----------------------------------------------------------------------
async function handleFallback(req, res) {
  const FALLBACK_API_KEY = process.env.FALLBACK_API_KEY;
  if (!FALLBACK_API_KEY) {
    return res.status(429).json({ error: { message: 'API quota has been exceeded. No fallback key configured in Vercel environment.' } });
  }

  try {
    const geminiBody = req.body;
    const messages = [];

    // 1. Translate System Instruction
    if (geminiBody.system_instruction && geminiBody.system_instruction.parts && geminiBody.system_instruction.parts[0]) {
      messages.push({
        role: 'system',
        content: geminiBody.system_instruction.parts[0].text
      });
    }

    // 2. Translate Chat History (user/model -> user/assistant)
    if (geminiBody.contents && Array.isArray(geminiBody.contents)) {
      for (const msg of geminiBody.contents) {
        messages.push({
          role: msg.role === 'model' ? 'assistant' : 'user',
          content: msg.parts[0].text
        });
      }
    }

    // 3. Prepare OpenAI-compatible payload (works for OpenRouter, Groq, TogetherAI)
    const openAiPayload = {
      model: 'meta-llama/llama-3-8b-instruct:free', // OpenRouter's excellent free model
      messages: messages,
      temperature: geminiBody.generationConfig?.temperature || 0.7,
      max_tokens: geminiBody.generationConfig?.maxOutputTokens || 1024,
    };

    // 4. Execute Fetch to OpenRouter
    const fallbackResponse = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${FALLBACK_API_KEY}`,
        'HTTP-Referer': 'https://athenaeumacademy.com', // Recommended by OpenRouter
        'X-Title': 'Ustad AI'
      },
      body: JSON.stringify(openAiPayload)
    });

    if (!fallbackResponse.ok) {
      const err = await fallbackResponse.json().catch(() => ({}));
      return res.status(fallbackResponse.status).json({ 
        error: { message: `Fallback API failed: ${err.error?.message || 'Unknown error'}` } 
      });
    }

    const fallbackData = await fallbackResponse.json();
    const fallbackText = fallbackData.choices?.[0]?.message?.content || '';

    // 5. Repackage response into exact Gemini JSON schema
    const mockGeminiResponse = {
      candidates: [
        {
          content: {
            parts: [{ text: fallbackText }],
            role: "model"
          }
        }
      ]
    };

    // Send successful fallback response back to the frontend
    return res.status(200).json(mockGeminiResponse);

  } catch (err) {
    console.error('Fallback Error:', err);
    return res.status(500).json({ error: { message: 'Fallback failed due to internal error.' } });
  }
}
