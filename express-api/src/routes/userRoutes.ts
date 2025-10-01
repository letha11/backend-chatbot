import { Router } from 'express';
import { authenticateToken, requireRole } from '../middlewares/auth';
import { validateBody, validateParams } from '../middlewares/validation';
import { createUser, deleteUser, getUserById, listUsers, updateUser } from '../controllers/userController';
import { createUserSchema, updateUserSchema, uuidSchema } from '../utils/validation';

const router = Router();

// All routes require super_admin
router.use(authenticateToken, requireRole(['super_admin']));

router.get('/', listUsers);
router.get('/:id', validateParams(uuidSchema), getUserById);
router.post('/', validateBody(createUserSchema), createUser);
router.put('/:id', validateParams(uuidSchema), validateBody(updateUserSchema), updateUser);
router.delete('/:id', validateParams(uuidSchema), deleteUser);

export default router;



