import axios from 'axios';
import { config } from '../config/environment';
import { logger } from '../utils/logger';

export interface VectorServiceResponse {
  success: boolean;
  message: string;
  data?: any;
}

export class VectorService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.fastapi.url;
  }

  /**
   * Update document active status in ChromaDB
   */
  async updateDocumentActiveStatus(documentId: string, isActive: boolean): Promise<boolean> {
    try {
      logger.info(`Updating document ${documentId} active status to ${isActive} in ChromaDB`);

      const response = await axios.patch(
        `${this.baseUrl}/vector/document/${documentId}/active`,
        null,
        {
          params: { is_active: isActive },
          timeout: 30000, // 30 second timeout
        }
      );

      const result: VectorServiceResponse = response.data;
      
      if (result.success) {
        logger.info(`Successfully updated document ${documentId} active status in ChromaDB`);
        return true;
      } else {
        logger.error(`Failed to update document ${documentId} active status in ChromaDB: ${result.message}`);
        return false;
      }
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED') {
        logger.error('FastAPI service is not available. Please ensure the FastAPI microservice is running.');
      } else if (error.response) {
        logger.error(`FastAPI returned error: ${error.response.status} - ${error.response.data?.error || error.response.statusText}`);
      } else {
        logger.error(`Error communicating with FastAPI service: ${error.message}`);
      }
      return false;
    }
  }

  /**
   * Delete document embeddings from ChromaDB
   */
  async deleteDocumentEmbeddings(documentId: string): Promise<boolean> {
    try {
      logger.info(`Deleting embeddings for document ${documentId} from ChromaDB`);

      const response = await axios.delete(
        `${this.baseUrl}/vector/document/${documentId}`,
        {
          timeout: 30000, // 30 second timeout
        }
      );

      const result: VectorServiceResponse = response.data;
      
      if (result.success) {
        logger.info(`Successfully deleted embeddings for document ${documentId} from ChromaDB`);
        return true;
      } else {
        logger.error(`Failed to delete embeddings for document ${documentId} from ChromaDB: ${result.message}`);
        return false;
      }
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED') {
        logger.error('FastAPI service is not available. Please ensure the FastAPI microservice is running.');
      } else if (error.response) {
        logger.error(`FastAPI returned error: ${error.response.status} - ${error.response.data?.error || error.response.statusText}`);
      } else {
        logger.error(`Error communicating with FastAPI service: ${error.message}`);
      }
      return false;
    }
  }

  /**
   * Check if FastAPI vector service is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(
        `${this.baseUrl}/vector/health`,
        { timeout: 5000 } // 5 second timeout for health check
      );

      return response.status === 200 && response.data.success;
    } catch (error) {
      logger.warn('FastAPI vector service health check failed');
      return false;
    }
  }
}

// Export singleton instance
export const vectorService = new VectorService();
