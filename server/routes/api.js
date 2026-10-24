import express from 'express';
import { internalAgentApi, forwardWithAuth } from '../config/internalApi.js';
import pool from '../config/db.js';

const router = express.Router();

/**
 * Heavy File Upload Bypass:
 * Issues presigned S3 / direct raster store upload URLs to the frontend.
 * Big satellite rasters stream directly to Cloud Storage / FastAPI raster store,
 * completely bypassing Express event loop memory.
 */
router.post('/storage/upload-url', async (req, res) => {
  try {
    const { filename, file_type } = req.body;
    const client = forwardWithAuth(req);
    const response = await client.post('/api/v1/storage/presigned-url', {
      filename: filename || 'satellite_image.tif',
      file_type: file_type || 'image/tiff',
    });
    return res.json(response.data);
  } catch (error) {
    const status = error.response ? error.response.status : 500;
    const message = error.response ? error.response.data : error.message;
    return res.status(status).json({
      error: 'Failed to generate direct upload URL',
      details: message,
    });
  }
});

/**
 * Asynchronous Query Orchestration:
 * Forwards spatial queries with internal service auth and user JWT token.
 * Returns HTTP 202 Accepted immediately with job_id for non-blocking execution.
 */
router.post('/query', async (req, res) => {
  try {
    const client = forwardWithAuth(req);
    const response = await client.post('/api/v1/query', req.body);
    return res.status(202).json(response.data);
  } catch (error) {
    const status = error.response ? error.response.status : 500;
    const message = error.response ? error.response.data : error.message;
    return res.status(status).json({
      error: 'Query submission error',
      details: message,
    });
  }
});

/**
 * Job Status Polling:
 * Allows frontend to poll job execution state without long HTTP connections.
 */
router.get('/jobs/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const client = forwardWithAuth(req);
    const response = await client.get(`/api/v1/jobs/${jobId}`);
    return res.json(response.data);
  } catch (error) {
    const status = error.response ? error.response.status : 404;
    return res.status(status).json({
      error: 'Job status fetch failed',
      details: error.message,
    });
  }
});

/**
 * Unified Spatial History for User:
 * Queries the shared PostgreSQL database linking users with spatial queries.
 */
router.get('/user/queries', async (req, res) => {
  try {
    const userId = req.headers['x-user-id'] || req.query.user_id;
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }

    const { rows } = await pool.query(
      `SELECT q.id, q.job_id, q.query_text, q.status, q.started_at, q.completed_at, q.result,
              u.email, u.username
       FROM queries q
       LEFT JOIN users u ON q.user_id = u.id
       WHERE q.user_id = $1
       ORDER BY q.started_at DESC
       LIMIT 50`,
      [userId]
    );

    return res.json({ status: 'success', queries: rows });
  } catch (error) {
    return res.status(500).json({
      error: 'Database query error',
      details: error.message,
    });
  }
});

export default router;
