import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { ConversationMessage } from './ConversationMessage';
import { Division } from './Division';

@Entity('conversations')
export class Conversation {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', length: 255 })
  title: string;

  @Column({ type: 'uuid', nullable: true })
  user_id: string | null;

  @Column({ type: 'uuid', nullable: true })
  division_id: string | null;

  @CreateDateColumn({ type: 'timestamp with time zone' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamp with time zone' })
  updated_at: Date;

  @OneToMany(() => ConversationMessage, (message) => message.conversation)
  messages: ConversationMessage[];

  @ManyToOne(() => Division, (division) => division.user_queries, { nullable: true })
  @JoinColumn({ name: 'division_id' })
  division: Division | null;
}


