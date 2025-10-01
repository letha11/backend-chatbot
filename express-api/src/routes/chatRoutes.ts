import { Router } from 'express';
import { chat } from '../controllers/chatController';
import { authenticateToken } from '../middlewares/auth';
import { validateBody } from '../middlewares/validation';
import { chatRequestSchema } from '../utils/validation';

const router = Router();

// All routes require authentication
router.use(authenticateToken);

// Chat endpoint
router.post('/', validateBody(chatRequestSchema), chat);

export default router;
