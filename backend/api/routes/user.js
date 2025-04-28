/**
 * FILE: user.js
 * DESCRIPTION:
 *   Handles user registration, login, and metadata updates.
 */

const express = require('express');
const router = express.Router();

// Test route to confirm it works
router.get('/', (req, res) => {
  res.json({ message: 'User route is working!' });
});

module.exports = router;
