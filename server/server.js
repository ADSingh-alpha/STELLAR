import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { testDbConnection } from './config/db.js';

import apiRoutes from './routes/api.js';

dotenv.config();

/**
 * Primary API Gateway (Node.js + Express.js)
 * Express application entry point with PostgreSQL Integration
 */
const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'Stellar AI Express API Gateway',
    database: 'PostgreSQL'
  });
});

app.use('/api/v1', apiRoutes);

app.listen(PORT, async () => {
  console.log(`Express Server running on port ${PORT}`);
  await testDbConnection();
});

