import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { Conversation } from './Conversation';

export type ConversationRole = 'user' | 'assistant' | 'system';

@Entity('conversation_messages')
export class ConversationMessage {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid' })
  conversation_id: string;

  @ManyToOne(() => Conversation, (conversation) => conversation.messages, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'conversation_id' })
  conversation: Conversation;

  @Column({ type: 'varchar', length: 20 })
  role: ConversationRole;

  @Column({ type: 'text' })
  content: string;

  @Index()
  @CreateDateColumn({ type: 'timestamp with time zone' })
  created_at: Date;
}


