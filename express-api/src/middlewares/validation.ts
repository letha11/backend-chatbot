import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { ResponseHandler } from '../utils/response';

export const validateBody = (schema: Joi.ObjectSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      const errorMessages = error.details.map((detail) => detail.message);
      const mainError = `Validation error: ${errorMessages[0]}`;
      ResponseHandler.validationError(res, mainError, errorMessages);
      return;
    }
    
    req.body = value;
    next();
  };
};

export const validateParams = (schema: Joi.Schema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const { error, value } = schema.validate(req.params);
    if (error) {
      const errorMessages = error.details.map((detail) => detail.message);
      const mainError = `Parameter validation error: ${errorMessages[0]}`;
      ResponseHandler.validationError(res, mainError, errorMessages);
      return;
    }
    
    req.params = value;
    next();
  };
};

export const validateQuery = (schema: Joi.ObjectSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const { error, value } = schema.validate(req.query);
    
    if (error) {
      const errorMessages = error.details.map((detail) => detail.message);
      const mainError = `Query validation error: ${errorMessages[0]}`;
      ResponseHandler.validationError(res, mainError, errorMessages);
      return;
    }
    
    req.query = value;
    next();
  };
};
