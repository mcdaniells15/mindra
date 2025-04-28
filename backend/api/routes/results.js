/**
 * FILE: results.js
 * DESCRIPTION:
 *   Handles routes for fetching past session results and scoring data.
 */

// FILE: api/routes/results.js
// DESCRIPTION: Handles ML scoring of tokenized responses

const express = require('express');
const router = express.Router();
const { scoreComprehension } = require('../../controllers/scoringController');

router.post('/score', async (req, res) => {
  const { tokenized, metadata } = req.body;

  if (!tokenized || !metadata) {
    return res.status(400).json({ error: 'Missing tokenized input or metadata' });
  }

  try {
    const result = await scoreComprehension(tokenized, metadata);
    res.json(result); // { comprehensionScore, recommendedHintType }
  } catch (error) {
    console.error('Scoring error:', error);
    res.status(500).json({ error: 'Scoring engine failed' });
  }
});

module.exports = router;
