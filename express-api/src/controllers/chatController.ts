import { Response } from 'express';
import { AppDataSource } from '../config/database';
import { Division } from '../models/Division';
import { asyncHandler } from '../middlewares/errorHandler';
import { AuthenticatedRequest } from '../middlewares/auth';
import { logger } from '../utils/logger';
import axios from 'axios';
import { config } from '../config/environment';
import { ResponseHandler } from '../utils/response';

export const chat = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { division_id, query, conversation_id, title } = req.body;
  
  if (!division_id || !query) {
    return ResponseHandler.validationError(res, 'Division ID and query are required');
  }
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  // Verify division exists and is active
  const division = await divisionRepository.findOne({ 
    where: { id: division_id, is_active: true } 
  });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found or inactive');
  }
  
  try {
    logger.info(`Processing chat query for division ${division_id}: ${query.substring(0, 100)}...`);
    
    // Send request to FastAPI ML service
    const response = await axios.post(`${config.fastapi.url}/chat`, {
      division_id,
      query,
      conversation_id,
      title,
      user_id: req.user?.id,
    });
    
    if (response.data.status === 'success') {
      logger.info(`Successfully processed chat query for division ${division_id}`);
      
      return ResponseHandler.success(res, {
        query: response.data.data.query,
        answer: response.data.data.answer,
        sources: response.data.data.sources,
        division: {
          id: division.id,
          name: division.name,
        },
        model_used: response.data.data.model_used,
        total_sources: response.data.data.total_sources,
        conversation_id: response.data.data.conversation_id,
      }, 'Chat query processed successfully');
    } else {
      logger.error(`FastAPI returned error status: ${response.data.status}`);
      return ResponseHandler.internalError(res, 'Failed to process chat query');
    }
    
  } catch (error) {
    logger.error('Error processing chat query:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        return ResponseHandler.notFound(res, 'No relevant documents found for this query');
      } else if (error.response?.status === 503) {
        return ResponseHandler.internalError(res, 'ML service is currently unavailable');
      }
    }
    
    return ResponseHandler.internalError(res, 'Failed to process chat query');
  }
});
