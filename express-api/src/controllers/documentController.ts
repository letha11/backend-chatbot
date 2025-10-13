import { Response } from 'express';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { AppDataSource } from '../config/database';
import { Document } from '../models/Document';
import { Division } from '../models/Division';
import { Embedding } from '../models/Embedding';
import { asyncHandler } from '../middlewares/errorHandler';
import { AuthenticatedRequest } from '../middlewares/auth';
import { storageService } from '../config/storage';
import { logger } from '../utils/logger';
import { vectorService } from '../services/vectorService';
import { sseService } from '../services/sseClientService';
import axios from 'axios';
import { config } from '../config/environment';
import { ResponseHandler } from '../utils/response';

export const uploadDocument = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  let { division_id } = req.body;
  const file = req.file;
  
  if (!file) {
    return ResponseHandler.validationError(res, 'No file uploaded');
  }
  
  const documentRepository = AppDataSource.getRepository(Document);
  const divisionRepository = AppDataSource.getRepository(Division);
  
  let division: Division | null = null;

  if (!config.features.division) {
    division = await divisionRepository.findOne({ where: { name: config.features.defaultDivisionName } });
  } else {
    division = await divisionRepository.findOne({ where: { id: division_id, is_active: true } });
  }
  
  // Verify division exists and is active
  // const division = await divisionRepository.findOne({ 
  //   where: { id: division_id, is_active: true } 
  // });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found or inactive');
  }
  
  division_id = division.id;
  // Generate unique filename
  const fileExtension = path.extname(file.originalname);
  const fileName = `${uuidv4()}${fileExtension}`;
  
  try {
    // Upload to storage
    const storagePath = await storageService.uploadFile(
      fileName,
      file.buffer,
      file.mimetype
    );
    
    // Create document record
    const document = documentRepository.create({
      division_id,
      original_filename: file.originalname,
      storage_path: storagePath,
      file_type: fileExtension.substring(1).toLowerCase(),
      status: 'uploaded',
      is_active: true,
      uploaded_by: req.user!.id,
    });
    
    await documentRepository.save(document);
    
    // Send initial SSE event to notify frontend that parsing is starting
    sseService.sendDocumentProcessingEvent(
      document.id,
      'parsing_started',
      'Document parsing has started',
      {
        filename: document.original_filename,
        fileType: document.file_type,
        divisionId: document.division_id
      }
    );

    // Trigger parsing via FastAPI microservice
    try {
      await axios.post(`${config.fastapi.url}/parse-document`, {
        document_id: document.id,
        storage_path: storagePath,
        file_type: document.file_type,
      });
      
      logger.info(`Document parsing initiated for ${document.id}`);
    } catch (parseError) {
      logger.error(`Failed to initiate parsing for document ${document.id}:`, parseError);
      // Update document status to parsing_failed
      await documentRepository.update(document.id, { status: 'parsing_failed' });
      
      // Send SSE event for parsing failure
      sseService.sendDocumentProcessingEvent(
        document.id,
        'parsing_failed',
        'Failed to start document parsing',
        {
          filename: document.original_filename,
          error: parseError instanceof Error ? parseError.message : 'Unknown error'
        }
      );
    }
    
    logger.info(`Document uploaded: ${file.originalname} by user ${req.user!.username}`);
    
    return ResponseHandler.created(res, {
      id: document.id,
      division_id: document.division_id,
      original_filename: document.original_filename,
      storage_path: document.storage_path,
      file_type: document.file_type,
      status: document.status,
      is_active: document.is_active,
      created_at: document.created_at,
    }, 'Document uploaded successfully');
  } catch (error) {
    logger.error('Error uploading document:', error);
    return ResponseHandler.internalError(res, 'Failed to upload document');
  }
});

export const getAllDocuments = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { division_id, is_active } = req.query;
  
  const documentRepository = AppDataSource.getRepository(Document);
  const divisionRepository = AppDataSource.getRepository(Division);

  let division: Division | null = null;

  console.log('config.features.division', config.features.division);
  console.log('division_id', division_id);
  console.log('is_active', is_active);
  
  // Handle division logic based on configuration and query parameters
  if (!config.features.division) {
    // If division feature is disabled, use default division
    division = await divisionRepository.findOne({ where: { name: config.features.defaultDivisionName } });
  } else if (division_id) {
    // If division feature is enabled and division_id is provided, find specific division
    division = await divisionRepository.findOne({ where: { id: division_id as string, is_active: true } });
    if (!division) {
      return ResponseHandler.notFound(res, 'Division not found or inactive');
    }
  }
  // If division feature is enabled but no division_id provided, query all documents
  
  const queryBuilder = documentRepository.createQueryBuilder('document')
    .leftJoinAndSelect('document.division', 'division')
    .orderBy('document.created_at', 'DESC');
  
  // Only filter by division if we have a specific division
  if (division) {
    queryBuilder.andWhere('document.division_id = :division_id', { division_id: division.id });
  }
  
  if (is_active !== undefined) {
    queryBuilder.andWhere('document.is_active = :is_active', { is_active });
  }
  
  const documents = await queryBuilder.getMany();
  
  return ResponseHandler.success(res, documents, 'Documents retrieved successfully');
});

export const getDocumentById = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  
  const documentRepository = AppDataSource.getRepository(Document);
  
  const document = await documentRepository.findOne({
    where: { id },
    relations: ['division'],
  });
  
  if (!document) {
    return ResponseHandler.notFound(res, 'Document not found');
  }
  
  return ResponseHandler.success(res, document, 'Document retrieved successfully');
});

export const toggleDocumentStatus = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  const { is_active } = req.body;
  
  const documentRepository = AppDataSource.getRepository(Document);
  
  const document = await documentRepository.findOne({ where: { id } });
  
  if (!document) {
    return ResponseHandler.notFound(res, 'Document not found');
  }
  
  // Only allow activation if document is embedded
  if (is_active && document.status !== 'embedded') {
    return ResponseHandler.validationError(res, 'Document must be embedded before activation');
  }
  
  try {
    // Update document status in PostgreSQL
    await documentRepository.update(id, { is_active });
    
    // Sync with ChromaDB vector database
    const vectorUpdateSuccess = await vectorService.updateDocumentActiveStatus(id, is_active);
    
    if (!vectorUpdateSuccess) {
      logger.warn(`Failed to update document ${id} active status in ChromaDB, but PostgreSQL update succeeded`);
      // We don't fail the request since PostgreSQL update succeeded
      // The vector database sync can be retried later if needed
    }
    
    const updatedDocument = await documentRepository.findOne({ where: { id } });
    
    logger.info(`Document ${is_active ? 'activated' : 'deactivated'}: ${id} by user ${req.user!.username}`);
    
    const message = `Document ${is_active ? 'activated' : 'deactivated'} successfully`;
    const warningMessage = !vectorUpdateSuccess 
      ? ` (Note: Vector database sync failed, but document status updated in main database)`
      : '';
    
    return ResponseHandler.success(res, updatedDocument, message + warningMessage);
  } catch (error) {
    logger.error(`Error updating document ${id} status:`, error);
    return ResponseHandler.internalError(res, 'Failed to update document status');
  }
});

export const deleteDocument = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  
  const documentRepository = AppDataSource.getRepository(Document);
  // const embeddingRepository = AppDataSource.getRepository(Embedding);
  
  const document = await documentRepository.findOne({ where: { id } });
  
  if (!document) {
    return ResponseHandler.notFound(res, 'Document not found');
  }
  
  try {
    // Remove associated embeddings from PostgreSQL
    // await embeddingRepository.delete({ document_id: id });
    
    // Remove embeddings from ChromaDB vector database
    const vectorDeleteSuccess = await vectorService.deleteDocumentEmbeddings(id);
    
    if (!vectorDeleteSuccess) {
      logger.warn(`Failed to delete embeddings for document ${id} from ChromaDB, but PostgreSQL deletion succeeded`);
      // We don't fail the request since PostgreSQL deletion succeeded
    }
    
    // Update document status to deleted
    await documentRepository.delete(id);
    
    // Optionally delete from storage (uncomment if you want to delete files)
    try {
      await storageService.deleteFile(document.storage_path);
    } catch (storageError) {
      logger.warn(`Failed to delete file from storage: ${document.storage_path}`, storageError);
    }

    // Delete from ChromaDB vector and OpenSearch database
    // Trigger deletion via FastAPI microservice
    try {
      await axios.delete(`${config.fastapi.url}/delete-document/${id}`);
    } catch (vectorError) {
      logger.error(`Failed to delete document ${id} from ChromaDB and OpenSearch: ${vectorError}`);
    }
    
    logger.info(`Document deleted: ${id} by user ${req.user!.username}`);
    
    const message = 'Document deleted successfully';
    const warningMessage = !vectorDeleteSuccess 
      ? ' (Note: Vector database cleanup failed, but document deleted from main database)'
      : '';
    
    return ResponseHandler.successMessage(res, message + warningMessage);
  } catch (error) {
    logger.error(`Error deleting document ${id}:`, error);
    return ResponseHandler.internalError(res, 'Failed to delete document');
  }
});
