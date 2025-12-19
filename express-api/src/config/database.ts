import { DataSource } from 'typeorm';
import { config } from './environment';
import { User } from '../models/User';
import { Division } from '../models/Division';
import { Document } from '../models/Document';
import { Embedding } from '../models/Embedding';
import { UserQuery } from '../models/UserQuery';
import { Conversation } from '../models/Conversation';
import { ConversationMessage } from '../models/ConversationMessage';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: config.database.host,
  port: config.database.port,
  username: config.database.username,
  password: config.database.password,
  database: config.database.name,
  synchronize: config.nodeEnv === 'development', // Only for development
  logging: config.nodeEnv === 'development',
  entities: [User, Division, Document, Embedding, UserQuery, Conversation, ConversationMessage],
  migrations: config.nodeEnv === 'development' ? ['src/migrations/*.ts'] : ['dist/migrations/*.js'],
  subscribers: config.nodeEnv === 'development' ? ['src/subscribers/*.ts'] : ['dist/subscribers/*.js'],
});

export const initializeDatabase = async (): Promise<void> => {
  try {
    await AppDataSource.initialize();
    console.log('Database connection established successfully');
    
    // Enable pgvector extension
    await AppDataSource.query('CREATE EXTENSION IF NOT EXISTS vector;');
    console.log('pgvector extension enabled');
  } catch (error) {
    console.error('Error during database initialization:', error);
    throw error;
  }
};
