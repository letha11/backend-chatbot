import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import { AppDataSource } from '../config/database';
import { User, UserRole } from '../models/User';
import { asyncHandler } from '../middlewares/errorHandler';
import { ResponseHandler } from '../utils/response';

export const listUsers = asyncHandler(async (req: Request, res: Response) => {
  const repo = AppDataSource.getRepository(User);
  const users = await repo.find({ order: { created_at: 'DESC' } });
  return ResponseHandler.success(
    res,
    users.map((u) => ({
      id: u.id,
      name: u.name,
      username: u.username,
      role: u.role,
      is_active: u.is_active,
      created_at: u.created_at,
      updated_at: u.updated_at,
    }))
  );
});

export const getUserById = asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params as { id: string };
  const repo = AppDataSource.getRepository(User);
  const user = await repo.findOne({ where: { id } });
  if (!user) {
    return ResponseHandler.notFound(res, 'User not found');
  }
  return ResponseHandler.success(res, {
    id: user.id,
    name: user.name,
    username: user.username,
    role: user.role,
    is_active: user.is_active,
    created_at: user.created_at,
    updated_at: user.updated_at,
  });
});

export const createUser = asyncHandler(async (req: Request, res: Response) => {
  const { name, username, password, role, is_active } = req.body as {
    name?: string | null;
    username: string;
    password: string;
    role?: UserRole;
    is_active?: boolean;
  };

  const repo = AppDataSource.getRepository(User);

  const exists = await repo.findOne({ where: { username } });
  if (exists) {
    return ResponseHandler.conflict(res, 'Username already exists');
  }

  const saltRounds = 12;
  const password_hash = await bcrypt.hash(password, saltRounds);

  const user = repo.create({
    name: name ?? null,
    username,
    password_hash,
    role: (role || 'user') as UserRole,
    is_active: is_active ?? true,
  });

  await repo.save(user);

  return ResponseHandler.created(res, {
    user: {
      id: user.id,
      name: user.name,
      username: user.username,
      role: user.role,
      is_active: user.is_active,
      created_at: user.created_at,
      updated_at: user.updated_at,
    },
  }, 'User created');
});

export const updateUser = asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params as { id: string };
  const { name, username, password, role, is_active } = req.body as {
    name?: string | null;
    username?: string;
    password?: string;
    role?: UserRole;
    is_active?: boolean;
  };

  const repo = AppDataSource.getRepository(User);
  const user = await repo.findOne({ where: { id } });
  if (!user) {
    return ResponseHandler.notFound(res, 'User not found');
  }

  if (username && username !== user.username) {
    const exists = await repo.findOne({ where: { username } });
    if (exists) {
      return ResponseHandler.conflict(res, 'Username already exists');
    }
    user.username = username;
  }

  if (typeof name !== 'undefined') {
    user.name = name as any;
  }

  if (typeof role !== 'undefined') {
    user.role = role;
  }

  if (typeof is_active !== 'undefined') {
    user.is_active = is_active;
  }

  if (password && password !== '') {
    const saltRounds = 12;
    user.password_hash = await bcrypt.hash(password, saltRounds);
  }

  await repo.save(user);

  return ResponseHandler.success(res, {
    user: {
      id: user.id,
      name: user.name,
      username: user.username,
      role: user.role,
      is_active: user.is_active,
      created_at: user.created_at,
      updated_at: user.updated_at,
    },
  }, 'User updated');
});

export const deleteUser = asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params as { id: string };
  const repo = AppDataSource.getRepository(User);
  const user = await repo.findOne({ where: { id } });
  if (!user) {
    return ResponseHandler.notFound(res, 'User not found');
  }

  await repo.remove(user);
  return ResponseHandler.successMessage(res, 'User deleted', 200);
});


