import Joi from 'joi';

// User validation schemas
export const registerSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  password: Joi.string().min(6).required(),
  role: Joi.string().valid("admin", "super_admin", "user").default('user'),
});

export const loginSchema = Joi.object({
  username: Joi.string().required(),
  password: Joi.string().required(),
});

// Division validation schemas
export const createDivisionSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  description: Joi.string().allow(''),
  is_active: Joi.boolean().default(true),
});

export const updateDivisionSchema = Joi.object({
  name: Joi.string().min(1).max(255),
  description: Joi.string().allow(''),
  is_active: Joi.boolean(),
}).min(1);

// Document validation schemas
export const uploadDocumentSchema = Joi.object({
  division_id: Joi.string().uuid().required(),
});

export const toggleDocumentSchema = Joi.object({
  is_active: Joi.boolean().required(),
});

// Chat validation schemas
export const chatRequestSchema = Joi.object({
  division_id: Joi.string().uuid().required(),
  query: Joi.string().min(1).max(2000).required(),
  conversation_id: Joi.string().uuid().optional(),
});

// UUID validation
export const uuidSchema =  Joi.object({
  id: Joi.string().uuid().required(),
})
