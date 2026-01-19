import { Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { AppDataSource } from '../config/database';
import { Division } from '../models/Division';
import { asyncHandler } from '../middlewares/errorHandler';
import { AuthenticatedRequest } from '../middlewares/auth';
import { logger } from '../utils/logger';
import { ResponseHandler } from '../utils/response';
import { FindManyOptions } from 'typeorm';
import { config } from '../config/environment';
import { Document } from '../models/Document';
import { deleteDocumentFromStorageAndOpensearch } from './documentController';
import { storageService } from '../config/storage';

export const getDefaultDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const divisionRepository = AppDataSource.getRepository(Division);
  const division = await divisionRepository.findOne({ where: { name: config.features.defaultDivisionName } });
  if (!division) {
    return ResponseHandler.notFound(res, 'Default division not found');
  }
  return ResponseHandler.success(res, division, 'Default division retrieved successfully');
});

export const createDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { name, description, is_active } = req.body;
  const file = req.file;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  // Check if division name already exists
  const existingDivision = await divisionRepository.findOne({ where: { name } });
  if (existingDivision) {
    return ResponseHandler.conflict(res, 'Division name already exists');
  }


  let imagePath: string | null = null;

  // Handle image upload if provided
  if (file) {
    try {
      const fileExtension = file.originalname.split('.').pop()?.toLowerCase() || 'jpg';
      const fileName = `divisions/${uuidv4()}.${fileExtension}`;
      await storageService.uploadFile(fileName, file.buffer, file.mimetype);
      imagePath = fileName;
      logger.info(`Division image uploaded: ${fileName}`);
    } catch (error) {
      logger.error('Error uploading division image:', error);
      return ResponseHandler.internalError(res, 'Failed to upload division image');
    }
  }
  
  // Create division
  const division = divisionRepository.create({
    name,
    description,
    is_active: is_active !== undefined ? is_active : true,
    image_path: imagePath,
  });
  
  await divisionRepository.save(division);
  
  logger.info(`Division created: ${name} by user ${req.user!.username}`);
  
  return ResponseHandler.created(res, division, 'Division created successfully');
});

export const getAllDivisions = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { is_active } = req.query;

  const divisionRepository = AppDataSource.getRepository(Division);

  const filter = {
    order: { created_at: 'DESC' },
  } as FindManyOptions<Division>;

  if (is_active !== undefined) {
    filter.where = { ...filter.where, is_active: is_active === 'true' };
  }
  
  const divisions = await divisionRepository.find(filter);
  
  return ResponseHandler.success(res, divisions, 'Divisions retrieved successfully');
});

export const getDivisionById = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  const division = await divisionRepository.findOne({ where: { id } });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  
  return ResponseHandler.success(res, division, 'Division retrieved successfully');
});

export const updateDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  const updateData = req.body;
  const file = req.file;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  const division = await divisionRepository.findOne({ where: { id } });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  
  // Check if name is being updated and already exists
  if (updateData.name && updateData.name !== division.name) {
    const existingDivision = await divisionRepository.findOne({ 
      where: { name: updateData.name } 
    });
    if (existingDivision) {
      return ResponseHandler.conflict(res, 'Division name already exists');
    }
  }

  // Handle image upload if provided
  if (file) {
    try {
      // Delete old image if exists
      if (division.image_path) {
        try {
          await storageService.deleteFile(division.image_path);
          logger.info(`Old division image deleted: ${division.image_path}`);
        } catch (deleteError) {
          logger.warn(`Failed to delete old division image: ${division.image_path}`, deleteError);
        }
      }

      const fileExtension = file.originalname.split('.').pop()?.toLowerCase() || 'jpg';
      const fileName = `divisions/${uuidv4()}.${fileExtension}`;
      await storageService.uploadFile(fileName, file.buffer, file.mimetype);
      updateData.image_path = fileName;
      logger.info(`Division image uploaded: ${fileName}`);
    } catch (error) {
      logger.error('Error uploading division image:', error);
      return ResponseHandler.internalError(res, 'Failed to upload division image');
    }
  }
  
  // Update division
  await divisionRepository.update(id, updateData);
  
  const updatedDivision = await divisionRepository.findOne({ where: { id } });
  
  logger.info(`Division updated: ${id} by user ${req.user!.username}`);
  
  return ResponseHandler.success(res, updatedDivision, 'Division updated successfully');
});

// Public endpoint - no authentication required
export const getDivisionImage = asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  const division = await divisionRepository.findOne({ where: { id } });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  
  if (!division.image_path) {
    return ResponseHandler.notFound(res, 'Division has no image');
  }
  
  try {
    const imageBuffer = await storageService.downloadFile(division.image_path);
    
    // Determine content type from file extension
    const extension = division.image_path.split('.').pop()?.toLowerCase();
    let contentType = 'image/jpeg';
    if (extension === 'png') contentType = 'image/png';
    else if (extension === 'gif') contentType = 'image/gif';
    else if (extension === 'webp') contentType = 'image/webp';
    else if (extension === 'svg') contentType = 'image/svg+xml';
    
    res.setHeader('Content-Type', contentType);
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.setHeader('Cross-Origin-Resource-Policy', 'cross-origin');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.send(imageBuffer);
  } catch (error) {
    logger.error(`Error retrieving division image: ${division.image_path}`, error);
    return ResponseHandler.notFound(res, 'Division image not found');
  }
});

export const deleteDivisionImage = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  const division = await divisionRepository.findOne({ where: { id } });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  
  if (!division.image_path) {
    return ResponseHandler.notFound(res, 'Division has no image');
  }
  
  try {
    await storageService.deleteFile(division.image_path);
    await divisionRepository.update(id, { image_path: null });
    
    logger.info(`Division image deleted: ${division.image_path} by user ${req.user!.username}`);
    
    return ResponseHandler.successMessage(res, 'Division image deleted successfully');
  } catch (error) {
    logger.error(`Error deleting division image: ${division.image_path}`, error);
    return ResponseHandler.internalError(res, 'Failed to delete division image');
  }
});

export const deactivateDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  const divisionRepository = AppDataSource.getRepository(Division);
  
  const division = await divisionRepository.findOne({ where: { id } });
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  await divisionRepository.update(id, { is_active: false });
  return ResponseHandler.successMessage(res, 'Division deactivated successfully');

});

export const deleteDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  const divisionRepository = AppDataSource.getRepository(Division);
  const division = await divisionRepository.findOne({ where: { id } });

  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }

  try {
    const documentRepository = AppDataSource.getRepository(Document);
    const documents = await documentRepository.find({ where: { division_id: id } });
    logger.info("Start deleting document related to division ${id}");

    logger.info(`Found ${documents.length} documents related to division ${id}`);

    // const promises = documents.map(document => deleteDocumentFromStorageAndOpensearch(document));
    // await Promise.all(promises);

    for (const document of documents) {
      await deleteDocumentFromStorageAndOpensearch(document);
      await documentRepository.remove(document);
      logger.info(`Document ${document.id} deleted from storage and opensearch by user ${req.user!.username}`);
    }

    // Delete division image if exists
    if (division.image_path) {
      try {
        await storageService.deleteFile(division.image_path);
        logger.info(`Division image deleted: ${division.image_path}`);
      } catch (imageDeleteError) {
        logger.warn(`Failed to delete division image: ${division.image_path}`, imageDeleteError);
      }
    }

    await divisionRepository.remove(division);
    logger.info(`Division ${id} deleted by user ${req.user!.username}`);
    return ResponseHandler.successMessage(res, 'Division deleted successfully');
  } catch (error) {
    logger.error(`Error deleting division ${id}:`, error);
    return ResponseHandler.internalError(res, 'Failed to delete division');
  }
});
