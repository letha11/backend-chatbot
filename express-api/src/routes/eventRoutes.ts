import { Router } from 'express';
import { initEvent, handleDocumentProcessingWebhook } from '../controllers/eventController';

const router = Router();

// SSE endpoint for frontend to connect to
router.get('/', initEvent);

// Webhook endpoint for FastAPI microservice to send notifications
router.post('/webhook/document-processing', handleDocumentProcessingWebhook);

export default router;