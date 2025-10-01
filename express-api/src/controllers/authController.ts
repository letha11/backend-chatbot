import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { AppDataSource } from '../config/database';
import { User, UserRole } from '../models/User';
import { config } from '../config/environment';
import { asyncHandler } from '../middlewares/errorHandler';
import { AuthenticatedRequest } from '../middlewares/auth';
import { logger } from '../utils/logger';
import { ResponseHandler } from '../utils/response';

export const register = asyncHandler(async (req: Request, res: Response) => {
  const { username, password, role } = req.body;
  
  const userRepository = AppDataSource.getRepository(User);
  
  // Check if user already exists
  const existingUser = await userRepository.findOne({ where: { username } });
  if (existingUser) {
    return ResponseHandler.conflict(res, 'Username already exists');
  }
  
  // Hash password
  const saltRounds = 12;
  const password_hash = await bcrypt.hash(password, saltRounds);
  
  // Create user
  const user = userRepository.create({
    username,
    password_hash,
    role: role as UserRole,
  });
  
  await userRepository.save(user);
  
  logger.info(`User registered: ${username}`);
  
  return ResponseHandler.created(res, {
    user: {
      id: user.id,
      name: user.name,
      username: user.username,
      role: user.role,
    },
  }, 'User registered successfully');
});

export const login = asyncHandler(async (req: Request, res: Response) => {
  const { username, password } = req.body;
  
  const userRepository = AppDataSource.getRepository(User);
  
  // Find user
  const user = await userRepository.findOne({ 
    where: { username, is_active: true } 
  });
  
  if (!user) {
    return ResponseHandler.unauthorized(res, 'Invalid credentials');
  }
  
  // Verify password
  const isValidPassword = await bcrypt.compare(password, user.password_hash);
  if (!isValidPassword) {
    return ResponseHandler.unauthorized(res, 'Invalid credentials');
  }
  
  // Generate JWT
  const payload = { userId: user.id, username: user.username };
  const secret = config.jwt.secret;
  
  const token = jwt.sign(payload, secret, { 
    expiresIn: config.jwt.expiresIn 
  } as jwt.SignOptions);
  
  logger.info(`User logged in: ${username}`);
  
  return ResponseHandler.success(res, {
    token,
    user: {
      id: user.id,
      name: user.name,
      username: user.username,
      role: user.role,
    },
  }, 'Login successful');
});

export const getMe = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const user = req.user!;
  
  return ResponseHandler.success(res, {
    id: user.id,
    name: user.name,
    username: user.username,
    role: user.role,
    is_active: user.is_active,
    created_at: user.created_at,
  }, 'User profile retrieved successfully');
});
