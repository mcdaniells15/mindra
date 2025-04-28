/**
 * FILE: scoringController.js
 * DESCRIPTION:
 *   Sends extracted token data and metadata to ML model to score comprehension.
 */


const axios = require('axios'); // If using REST
// const { spawn } = require('child_process'); // If using local Python process

async function scoreComprehension(tokenizedData, userMetadata) {
  try {
    const payload = {
      tokens: tokenizedData,
      metadata: userMetadata
    };

    // If using a RESTful ML API (e.g., FastAPI)
    const res = await axios.post(process.env.ML_SERVICE_URL, payload);
    return res.data;

    // If using Python subprocess:
    // const py = spawn('python3', ['backend/ml/inference.py']);
    // py.stdin.write(JSON.stringify(payload));
    // py.stdin.end();
    // return new Promise((resolve) => {
    //   py.stdout.on('data', data => resolve(JSON.parse(data)));
    // });

  } catch (err) {
    console.error('ML scoring failed:', err);
    return { comprehensionScore: 0, recommendedHintType: 'unknown' };
  }
}

module.exports = { scoreComprehension };
