import type { Response } from 'express';
import { logger } from '../utils/logger';

interface SseClient {
  id: string;
  response: Response;
  connectedAt: Date;
}

export class SseService {
  private sseClients: Map<string, SseClient> = new Map();

  constructor() {
    this.sseClients = new Map();
  }

  addClient(clientId: string, response: Response) {
    const client: SseClient = {
      id: clientId,
      response,
      connectedAt: new Date()
    };
    
    this.sseClients.set(clientId, client);
    logger.info(`SSE client connected: ${clientId}`);
    
    // Send initial connection event
    this.sendEventToClient(clientId, 'connected', {
      message: 'Connected to document processing events',
      clientId,
      timestamp: new Date().toISOString()
    });
  }

  removeClient(clientId: string) {
    const client = this.sseClients.get(clientId);
    if (client) {
      this.sseClients.delete(clientId);
      try {
        client.response.end();
      } catch (error) {
        logger.warn(`Error closing SSE client ${clientId}:`, error);
      }
      logger.info(`SSE client disconnected: ${clientId}`);
    }
  }

  sendEventToClient(clientId: string, event: string, payload: any) {
    const client = this.sseClients.get(clientId);
    if (client) {
      try {
        const data = JSON.stringify(payload);
        client.response.write(`event: ${event}\n`);
        client.response.write(`data: ${data}\n\n`);
        logger.debug(`SSE event sent to ${clientId}: ${event}`);
      } catch (error) {
        logger.error(`Error sending SSE event to ${clientId}:`, error);
        this.removeClient(clientId);
      }
    }
  }

  sendEventToAllClients(event: string, payload: any) {
    const data = JSON.stringify(payload);
    const disconnectedClients: string[] = [];
    
    this.sseClients.forEach((client, clientId) => {
      try {
        client.response.write(`event: ${event}\n`);
        client.response.write(`data: ${data}\n\n`);
        logger.debug(`SSE event sent to ${clientId}: ${event}`);
      } catch (error) {
        logger.error(`Error sending SSE event to ${clientId}:`, error);
        disconnectedClients.push(clientId);
      }
    });
    
    // Clean up disconnected clients
    disconnectedClients.forEach(clientId => this.removeClient(clientId));
  }

  sendDocumentProcessingEvent(documentId: string, status: string, message: string, metadata?: any) {
    const payload = {
      documentId,
      status,
      message,
      timestamp: new Date().toISOString(),
      ...metadata
    };
    
    this.sendEventToAllClients('document_processing', payload);
    logger.info(`Document processing event sent: ${documentId} - ${status}`);
  }

  getConnectedClientsCount(): number {
    return this.sseClients.size;
  }

  getConnectedClients(): string[] {
    return Array.from(this.sseClients.keys());
  }
}

export const sseService = new SseService();