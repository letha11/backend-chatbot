import { Router } from 'express';
import { register, login, getMe } from '../controllers/authController';
import { validateBody } from '../middlewares/validation';
import { authenticateToken, requireRole } from '../middlewares/auth';
import { registerSchema, loginSchema } from '../utils/validation';

const router = Router();

// Public routes
router.post('/register', validateBody(registerSchema), requireRole(["super_admin"]), register);
router.post('/login', validateBody(loginSchema), login);

// Protected routes
router.get('/me', authenticateToken, getMe);

export default router;
