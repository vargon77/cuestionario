// src/services/llm.ts
export async function callLLM(prompt: string): Promise<string> {
  const provider = import.meta.env.VITE_LLM_PROVIDER;
  if (!provider) {
    throw new Error('No LLM provider configured');
  }
  if (provider === 'deepseek') {
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + import.meta.env.VITE_DEEPSEEK_API_KEY,
      },
      body: JSON.stringify({
        model: import.meta.env.VITE_DEEPSEEK_MODEL,
        messages: [{ role: 'user', content: prompt }],
      }),
    });
    if (!response.ok) {
      throw new Error('DeepSeek API error: ' + response.status);
    }
    const data = await response.json();
    return data.choices[0].message.content;
  } else if (provider === 'gemini') {
    const response = await fetch(
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateMessage',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': import.meta.env.VITE_GEMINI_API_KEY,
        },
        body: JSON.stringify({
          prompt: { messages: [{ role: 'user', content: prompt }] },
        }),
      }
    );
    if (!response.ok) {
      throw new Error('Gemini API error: ' + response.status);
    }
    const data = await response.json();
    return data.candidates[0].content;
  }
  throw new Error('Unsupported LLM provider');
}