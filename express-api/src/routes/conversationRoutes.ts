import { Router } from 'express';
import { ingestMessage, getHistory, listConversations } from '../controllers/conversationController';
import { validateBody } from '../middlewares/validation';
import { authenticateToken } from '../middlewares/auth';
import { config } from '../config/environment';

const router = Router();

// Simple internal API key guard (apply per-route)
const internalKeyGuard = (req: any, res: any, next: any) => {
  const key = req.header('x-internal-api-key');
  const expected = config.internalApiKey;
  if (!expected || key !== expected) {
    return res.status(401).json({ status: 'error', error: 'Unauthorized', timestamp: new Date().toISOString() });
  }
  next();
};

// Ingest one or more messages; creates conversation if missing (internal only)
router.post('/ingest', internalKeyGuard, ingestMessage);

// Fetch recent messages for a conversation (internal only)
router.get('/:conversation_id/history', internalKeyGuard, getHistory);

// List conversations for the current user (JWT required), optional division filter
router.get('/', authenticateToken, listConversations);

export default router;


