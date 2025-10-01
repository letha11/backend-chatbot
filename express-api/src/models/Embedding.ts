import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Document } from './Document';

@Entity('embeddings')
export class Embedding {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid' })
  document_id: string;

  @Column({ type: 'text' })
  chunk_text: string;

  @Column({ type: 'vector', length: 384 })
  embedding: number[];

  @Column({ type: 'integer' })
  chunk_index: number;

  @CreateDateColumn({ type: 'timestamp with time zone' })
  created_at: Date;

  // Relations
  @ManyToOne(() => Document, (document) => document.embeddings)
  @JoinColumn({ name: 'document_id' })
  document: Document;
}
