import { Router } from 'express';
import multer from 'multer';
import {
  uploadDocument,
  getAllDocuments,
  getDocumentById,
  toggleDocumentStatus,
  deleteDocument,
} from '../controllers/documentController';
import { validateBody, validateParams } from '../middlewares/validation';
import { authenticateToken } from '../middlewares/auth';
import { 
  uploadDocumentSchema, 
  toggleDocumentSchema, 
  uuidSchema 
} from '../utils/validation';
import { config } from '../config/environment';

const router = Router();

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    // Allow common document types
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
      'text/csv',
      'application/csv',
      'image/jpeg',
      'image/png',
      'image/jpg',
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, DOCX, DOC, TXT, CSV, and image files are allowed.'));
    }
  },
});

// All routes require authentication
router.use(authenticateToken);

router.post('/upload', 
  upload.single('file'), 
   validateBody(uploadDocumentSchema), 
  uploadDocument
);
router.get('/', getAllDocuments);
router.get('/:id', validateParams(uuidSchema), getDocumentById);
router.patch('/:id/toggle', 
  validateParams(uuidSchema), 
  validateBody(toggleDocumentSchema), 
  toggleDocumentStatus
);
router.delete('/:id', validateParams(uuidSchema), deleteDocument);

export default router;
