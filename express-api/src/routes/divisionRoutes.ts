import { Router } from 'express';
import {
  createDivision,
  getAllDivisions,
  getDivisionById,
  updateDivision,
  deleteDivision,
  getDefaultDivision,
} from '../controllers/divisionController';
import { validateBody, validateParams } from '../middlewares/validation';
import { authenticateToken } from '../middlewares/auth';
import { 
  createDivisionSchema, 
  updateDivisionSchema, 
  uuidSchema 
} from '../utils/validation';
import { config } from '../config/environment';

const router = Router();

// All routes require authentication
router.use(authenticateToken);

if (config.features.division) {  
  router.post('/', validateBody(createDivisionSchema), createDivision);
  router.get('/', getAllDivisions);
  router.get('/:id', validateParams(uuidSchema), getDivisionById);
  router.put('/:id', validateParams(uuidSchema), validateBody(updateDivisionSchema), updateDivision);
  router.delete('/:id', validateParams(uuidSchema), deleteDivision);
} else {
  router.get('/default', getDefaultDivision);
}

export default router;
