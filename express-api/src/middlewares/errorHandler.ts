import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { ResponseHandler } from '../utils/response';

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
}

export class ApiError extends Error implements AppError {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number = 500, isOperational: boolean = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  error: AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  let { statusCode = 500, message } = error;

  // Log error
  logger.error(`${req.method} ${req.path} - ${statusCode} - ${message}`, {
    error: error.stack,
    request: {
      method: req.method,
      url: req.url,
      headers: req.headers,
      body: req.body,
    },
  });

  // Handle specific error types
  if (error.name === 'ValidationError') {
    statusCode = 400;
    message = 'Validation error';
  } else if (error.name === 'UnauthorizedError') {
    statusCode = 401;
    message = 'Unauthorized';
  } else if (error.name === 'CastError') {
    statusCode = 400;
    message = 'Invalid ID format';
  }

  // Send error response
  if (process.env.NODE_ENV === 'development') {
    ResponseHandler.error(res, message, statusCode, [error.stack || 'No stack trace available']);
  } else {
    ResponseHandler.error(res, message, statusCode);
  }
};

export const notFoundHandler = (req: Request, res: Response): void => {
  ResponseHandler.notFound(res, `Route ${req.method} ${req.path} not found`);
};

export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
