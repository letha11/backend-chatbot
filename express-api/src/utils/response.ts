import { Response } from 'express';

export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
  error?: string;
  errors?: string[];
  timestamp: string;
}

export class ResponseHandler {
  /**
   * Send success response with data
   */
  static success<T>(res: Response, data: T, message?: string, statusCode: number = 200): Response {
    const response: ApiResponse<T> = {
      status: 'success',
      data,
      timestamp: new Date().toISOString(),
    };

    if (message) {
      response.message = message;
    }

    return res.status(statusCode).json(response);
  }

  /**
   * Send success response without data (for operations like delete)
   */
  static successMessage(res: Response, message: string, statusCode: number = 200): Response {
    const response: ApiResponse = {
      status: 'success',
      message,
      timestamp: new Date().toISOString(),
    };

    return res.status(statusCode).json(response);
  }

  /**
   * Send created response (201)
   */
  static created<T>(res: Response, data: T, message?: string): Response {
    return ResponseHandler.success(res, data, message, 201);
  }

  /**
   * Send error response
   */
  static error(res: Response, error: string, statusCode: number = 500, errors?: string[]): Response {
    const response: ApiResponse = {
      status: 'error',
      error,
      timestamp: new Date().toISOString(),
    };

    if (errors && errors.length > 0) {
      response.errors = errors;
    }

    return res.status(statusCode).json(response);
  }

  /**
   * Send validation error response (400)
   */
  static validationError(res: Response, error: string, errors?: string[]): Response {
    return ResponseHandler.error(res, error, 400, errors);
  }

  /**
   * Send unauthorized error response (401)
   */
  static unauthorized(res: Response, error: string = 'Unauthorized'): Response {
    return ResponseHandler.error(res, error, 401);
  }

  /**
   * Send forbidden error response (403)
   */
  static forbidden(res: Response, error: string = 'Forbidden'): Response {
    return ResponseHandler.error(res, error, 403);
  }

  /**
   * Send not found error response (404)
   */
  static notFound(res: Response, error: string = 'Resource not found'): Response {
    return ResponseHandler.error(res, error, 404);
  }

  /**
   * Send conflict error response (409)
   */
  static conflict(res: Response, error: string): Response {
    return ResponseHandler.error(res, error, 409);
  }

  /**
   * Send internal server error response (500)
   */
  static internalError(res: Response, error: string = 'Internal server error'): Response {
    return ResponseHandler.error(res, error, 500);
  }
}

// Export convenience methods
export const {
  success,
  successMessage,
  created,
  error,
  validationError,
  unauthorized,
  forbidden,
  notFound,
  conflict,
  internalError,
} = ResponseHandler;
