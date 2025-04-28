// FILE: server.js
// DESCRIPTION: Entry point for the Mindra backend server

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

const queryRoutes = require('./api/routes/query');
const resultRoutes = require('./api/routes/results');
const userRoutes = require('./api/routes/user');

console.log('queryRoutes:', typeof queryRoutes);


// Load .env variables
dotenv.config();

// Create the app
const app = express();
const PORT = process.env.PORT || 5050;


console.log(queryRoutes)

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use('/api/query', queryRoutes);
app.use('/api/results', resultRoutes);
app.use('/api/user', userRoutes);

// Root route
app.get('/', (req, res) => {
  res.send('Mindra Backend API is running...');
});

// Start the server
app.listen(PORT, () => {
  console.log(` Mindra backend listening on http://localhost:${PORT}`);
});
