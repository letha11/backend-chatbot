import { Router } from 'express';
import authRoutes from './authRoutes';
import divisionRoutes from './divisionRoutes';
import documentRoutes from './documentRoutes';
import chatRoutes from './chatRoutes';
import conversationRoutes from './conversationRoutes';
import { ResponseHandler } from '../utils/response';

const router = Router();

// API version prefix
const API_PREFIX = '/api/v1';

// Route mounting
router.use(`${API_PREFIX}/auth`, authRoutes);
router.use(`${API_PREFIX}/divisions`, divisionRoutes);
router.use(`${API_PREFIX}/documents`, documentRoutes);
router.use(`${API_PREFIX}/chat`, chatRoutes);
router.use(`${API_PREFIX}/conversations`, conversationRoutes);

// Health check endpoint
router.get('/health', (req, res) => {
  return ResponseHandler.success(res, {
    service: 'Chatbot Control Panel Backend',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  }, 'Service is healthy');
});

export default router;
