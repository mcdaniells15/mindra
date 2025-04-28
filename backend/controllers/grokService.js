/**
 * FILE: grokService.js
 * DESCRIPTION:
 *   Sends user question to Grok API and returns plain, mid, and deep explanations.
 */

const axios = require('axios');

async function queryGrok(question) {
  const levels = ['plain', 'mid', 'deep'];
  const responses = {};

  for (const level of levels) {
    const prompt = `Explain this in a ${level} way: ${question}`;
    const res = await axios.post('https://api.grok.ai/query', {
      prompt,
      apiKey: process.env.GROK_API_KEY
    });
    responses[level] = res.data.output;
  }

  return responses;
}

module.exports = { queryGrok };
