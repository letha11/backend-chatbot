import { Response } from 'express';
import { AppDataSource } from '../config/database';
import { Division } from '../models/Division';
import { asyncHandler } from '../middlewares/errorHandler';
import { AuthenticatedRequest } from '../middlewares/auth';
import { logger } from '../utils/logger';
import { ResponseHandler } from '../utils/response';
import { FindManyOptions } from 'typeorm';
import { config } from '../config/environment';

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
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  // Check if division name already exists
  const existingDivision = await divisionRepository.findOne({ where: { name } });
  if (existingDivision) {
    return ResponseHandler.conflict(res, 'Division name already exists');
  }
  
  // Create division
  const division = divisionRepository.create({
    name,
    description,
    is_active: is_active !== undefined ? is_active : true,
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
  
  // Update division
  await divisionRepository.update(id, updateData);
  
  const updatedDivision = await divisionRepository.findOne({ where: { id } });
  
  logger.info(`Division updated: ${id} by user ${req.user!.username}`);
  
  return ResponseHandler.success(res, updatedDivision, 'Division updated successfully');
});

export const deleteDivision = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { id } = req.params;
  
  const divisionRepository = AppDataSource.getRepository(Division);
  
  const division = await divisionRepository.findOne({ where: { id } });
  
  if (!division) {
    return ResponseHandler.notFound(res, 'Division not found');
  }
  
  // Soft delete by setting is_active to false
  await divisionRepository.update(id, { is_active: false });
  
  logger.info(`Division soft deleted: ${id} by user ${req.user!.username}`);
  
  return ResponseHandler.successMessage(res, 'Division deactivated successfully');
});
