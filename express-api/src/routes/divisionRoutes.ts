import { Router } from 'express';
import multer from 'multer';
import {
  createDivision,
  getAllDivisions,
  getDivisionById,
  updateDivision,
  deleteDivision,
  getDefaultDivision,
  getDivisionImage,
  deleteDivisionImage,
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

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit for images
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/svg+xml',
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only JPEG, PNG, GIF, WebP, and SVG images are allowed.'));
    }
  },
});

// Public route - no authentication required
if (config.features.division) {
  router.get('/:id/image', validateParams(uuidSchema), getDivisionImage);
}

// All routes below require authentication
router.use(authenticateToken);

if (config.features.division) {  
  router.post('/', upload.single('image'), validateBody(createDivisionSchema), createDivision);
  router.get('/', getAllDivisions);
  router.get('/:id', validateParams(uuidSchema), getDivisionById);
  router.put('/:id', validateParams(uuidSchema), upload.single('image'), validateBody(updateDivisionSchema), updateDivision);
  router.delete('/:id', validateParams(uuidSchema), deleteDivision);
  router.delete('/:id/image', validateParams(uuidSchema), deleteDivisionImage);
} else {
  router.get('/default', getDefaultDivision);
}

export default router;
