import { Router } from 'express';
import { ingestMessage, getHistory, listConversations, getHistoryInternal, listAllConversations } from '../controllers/conversationController';
import { validateBody } from '../middlewares/validation';
import { authenticateToken, requireRole } from '../middlewares/auth';
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
router.get('/:conversation_id/history-internal', internalKeyGuard, getHistoryInternal);

// Fetch recent messages for a conversation (internal JWT)
router.get('/:conversation_id/history', authenticateToken, getHistory);

// List conversations for the current user (JWT required), optional division filter
router.get('/', authenticateToken, listConversations);

// List all conversations (admin and super_admin only)
router.get('/all', authenticateToken, requireRole(['admin', 'super_admin']), listAllConversations);

export default router;


