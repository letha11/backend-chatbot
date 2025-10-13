import { Request, Response } from 'express';
import { AppDataSource } from '../config/database';
import { Conversation } from '../models/Conversation';
import { ConversationMessage } from '../models/ConversationMessage';
import { asyncHandler } from '../middlewares/errorHandler';
import { ResponseHandler } from '../utils/response';
import { AuthenticatedRequest } from '../middlewares/auth';
import { config } from '../config/environment';
import { Division } from '../models/Division';

// Internal ingestion from FastAPI ML
export const ingestMessage = asyncHandler(async (req: Request, res: Response) => {
  let { conversation_id, division_id, title, user_id, messages } = req.body as {
    conversation_id?: string;
    division_id?: string | null;
    title?: string;
    user_id?: string | null;
    messages: Array<{ role: 'user' | 'assistant' | 'system'; content: string; sources: string }>;
  };

  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return ResponseHandler.validationError(res, 'messages array is required');
  }

  const conversationRepo = AppDataSource.getRepository(Conversation);
  const messageRepo = AppDataSource.getRepository(ConversationMessage);
  const divisionRepository = AppDataSource.getRepository(Division);

  let conversation: Conversation | null = null;

  if (!config.features.division) {
    division_id = (await divisionRepository.findOne({ where: { name: config.features.defaultDivisionName } }))?.id;
  }

  if (conversation_id) {
    conversation = await conversationRepo.findOne({ where: { id: conversation_id } });
  }

  if (!conversation) {
    if (!title) {
      return ResponseHandler.validationError(res, 'title is required when creating a new conversation');
    }
    conversation = conversationRepo.create({
      title,
      user_id: user_id || null,
      division_id: division_id || null,
    });
    conversation = await conversationRepo.save(conversation);
  }

  const toInsert = messages.map((m) =>
    messageRepo.create({
      conversation_id: conversation!.id,
      role: m.role,
      content: m.content,
      sources: m.sources,
    })
  );

  await messageRepo.save(toInsert);

  // Touch updated_at for conversation
  await conversationRepo.update({ id: conversation.id }, { updated_at: new Date() });

  return ResponseHandler.created(res, {
    conversation_id: conversation.id,
    title: conversation.title,
    inserted_messages: toInsert.length,
  }, 'Conversation messages ingested');
});

export const getHistoryInternal = asyncHandler(async (req: Request, res: Response) => {
  const { conversation_id } = req.params as { conversation_id: string };
  const limit = Math.min(parseInt((req.query.limit as string) || '6', 10), 20);

  if (!conversation_id) {
    return ResponseHandler.validationError(res, 'conversation_id is required');
  }

  const messageRepo = AppDataSource.getRepository(ConversationMessage);
  const conversationRepo = AppDataSource.getRepository(Conversation);

  const conversation = await conversationRepo.findOne({ where: { id: conversation_id } });
  if (!conversation) {
    return ResponseHandler.notFound(res, 'Conversation not found');
  }

  const messages = await messageRepo.find({
    where: { conversation_id },
    order: { created_at: 'DESC' },
    take: limit,
  });

  // Return in chronological order
  messages.reverse();

  return ResponseHandler.success(res, {
    conversation: {
      id: conversation.id,
      title: conversation.title,
      division_id: conversation.division_id,
      user_id: conversation.user_id,
      created_at: conversation.created_at,
    },
    messages: messages.map((m) => ({ id: m.id, role: m.role, content: m.content, sources: m.sources, created_at: m.created_at })),
  });
});

// Public API to fetch recent history for a conversation (for UI or RAG context)
export const getHistory = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { conversation_id } = req.params as { conversation_id: string };
  const limit = Math.min(parseInt((req.query.limit as string) || '6', 10), 20);


  if (!conversation_id) {
    return ResponseHandler.validationError(res, 'conversation_id is required');
  }

  const messageRepo = AppDataSource.getRepository(ConversationMessage);
  const conversationRepo = AppDataSource.getRepository(Conversation);

  const conversation = await conversationRepo.findOne({ where: { id: conversation_id } });
  if (!conversation) {
    return ResponseHandler.notFound(res, 'Conversation not found');
  }

  if (conversation.user_id !== req.user!.id) {
    return ResponseHandler.forbidden(res, 'You are not allowed to access this conversation');
  }

  const messages = await messageRepo.find({
    where: { conversation_id },
    order: { created_at: 'DESC' },
    take: limit,
  });

  // Return in chronological order
  messages.reverse();

  return ResponseHandler.success(res, {
    conversation: {
      id: conversation.id,
      title: conversation.title,
      division_id: conversation.division_id,
      user_id: conversation.user_id,
      created_at: conversation.created_at,
    },
    messages: messages.map((m) => ({ id: m.id, role: m.role, content: m.content, sources: m.sources, created_at: m.created_at })),
  });
});

// List conversations for current user, optionally filter by division, order by updated_at desc
export const listConversations = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const user = req.user!;
  let division_id = (req.query.division_id as string) || undefined;
  const limit = Math.min(parseInt((req.query.limit as string) || '50', 10), 200);

  const conversationRepo = AppDataSource.getRepository(Conversation);
  const divisionRepository = AppDataSource.getRepository(Division);

  if (!config.features.division) {
    division_id = (await divisionRepository.findOne({ where: { name: config.features.defaultDivisionName } }))?.id;
  }

  const where: any = { user_id: user.id };
  if (division_id) where.division_id = division_id;

  const conversations = await conversationRepo.find({
    where,
    order: { updated_at: 'DESC' },
    take: limit,
  });

  return ResponseHandler.success(res, {
    conversations: conversations.map((c) => ({
      id: c.id,
      title: c.title,
      division_id: c.division_id,
      user_id: c.user_id,
      created_at: c.created_at,
      updated_at: c.updated_at,
    })),
  }, 'Conversations retrieved successfully');
});


