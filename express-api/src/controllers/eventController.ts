import { Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { asyncHandler } from '../middlewares/errorHandler';
import { sseService } from '../services/sseClientService';
import { ResponseHandler } from '../utils/response';
import { logger } from '../utils/logger';
import { config } from '../config/environment';

export const initEvent = asyncHandler(async (req: Request, res: Response) => {
    // Generate unique client ID
    const clientId = uuidv4();
    
    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Cache-Control');

    // Flush headers to establish connection
    res.flushHeaders?.();

    // Add client to SSE service
    sseService.addClient(clientId, res);

    // Handle client disconnect
    res.on('close', () => {
        sseService.removeClient(clientId);
    });

    res.on('error', (error) => {
        logger.error(`SSE connection error for client ${clientId}:`, error);
        sseService.removeClient(clientId);
    });

    // Keep connection alive with periodic heartbeat
    const heartbeatInterval = setInterval(() => {
        try {
            res.write(`event: heartbeat\n`);
            res.write(`data: ${JSON.stringify({ timestamp: new Date().toISOString() })}\n\n`);
        } catch (error) {
            logger.error(`Heartbeat failed for client ${clientId}:`, error);
            clearInterval(heartbeatInterval);
            sseService.removeClient(clientId);
        }
    }, 30000); // Send heartbeat every 30 seconds

    // Clean up interval on disconnect
    res.on('close', () => {
        clearInterval(heartbeatInterval);
    });

    logger.info(`SSE connection established for client: ${clientId}`);
});

export const handleDocumentProcessingWebhook = asyncHandler(async (req: Request, res: Response) => {
    // Verify webhook authenticity (optional but recommended)
    const webhookKey = req.headers['x-webhook-key'] as string;
    if (webhookKey !== config.internalApiKey) {
        logger.warn('Unauthorized webhook request received');
        return ResponseHandler.unauthorized(res, 'Invalid webhook key');
    }

    const { documentId, status, message, metadata } = req.body;

    if (!documentId || !status) {
        return ResponseHandler.validationError(res, 'Missing required fields: documentId, status');
    }

    try {
        // Send SSE event to all connected clients
        sseService.sendDocumentProcessingEvent(documentId, status, message, metadata);
        
        logger.info(`Document processing webhook received: ${documentId} - ${status}`);
        
        return ResponseHandler.successMessage(res, 'Webhook processed successfully');
    } catch (error) {
        logger.error('Error processing document webhook:', error);
        return ResponseHandler.internalError(res, 'Failed to process webhook');
    }
});