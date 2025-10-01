import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../config/environment';
import { AppDataSource } from '../config/database';
import { User, UserRole } from '../models/User';
import { logger } from '../utils/logger';
import { ResponseHandler } from '../utils/response';

export interface AuthenticatedRequest extends Request {
  user?: User;
}

export const authenticateToken = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      ResponseHandler.unauthorized(res, 'Access token required');
      return;
    }

    const decoded = jwt.verify(token, config.jwt.secret) as { userId: string; username: string };
    
    const userRepository = AppDataSource.getRepository(User);
    const user = await userRepository.findOne({
      where: { id: decoded.userId, is_active: true },
    });

    if (!user) {
      ResponseHandler.unauthorized(res, 'Invalid or expired token');
      return;
    }

    req.user = user;
    next();
  } catch (error) {
    logger.error('Authentication error:', error);
    ResponseHandler.forbidden(res, 'Invalid token');
  }
};

export const requireRole = (roles: UserRole[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      ResponseHandler.unauthorized(res, 'Authentication required');
      return;
    }

    if (!roles.includes(req.user.role)) {
      ResponseHandler.forbidden(res, 'Insufficient permissions');
      return;
    }

    next();
  };
};
