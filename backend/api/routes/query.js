/**
 * FILE: query.js
 * DESCRIPTION:
 *   Handles POST/GET routes for submitting user questions and receiving Grok responses.
 */

// FILE: api/routes/query.js
// DESCRIPTION: Handles user query input and returns Grok responses

const express = require('express');
const router = express.Router();
const { queryGrok } = require('../../controllers/grokService');

router.post('/', async (req, res) => {
  const { question } = req.body;

  if (!question) {
    return res.status(400).json({ error: 'Missing question' });
  }

  try {
    const responses = await queryGrok(question); // { plain, mid, deep }
    res.json({
      question,
      responses
    });
  } catch (error) {
    console.error('Grok query failed:', error);
    res.status(500).json({ error: 'Failed to process question' });
  }
});

module.exports = router;
