import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  OneToMany,
} from 'typeorm';
import { Division } from './Division';
import { User } from './User';
import { Embedding } from './Embedding';

@Entity('documents')
export class Document {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', nullable: true })
  division_id: string | null;

  @Column({ type: 'varchar', length: 255 })
  original_filename: string;

  @Column({ type: 'varchar', length: 255 })
  storage_path: string;

  @Column({ type: 'varchar', length: 50 })
  file_type: string;

  @Column({ type: 'varchar', length: 50, default: 'uploaded' })
  status: string; // 'uploaded', 'parsed', 'embedded', 'failed', 'parsing_failed', 'embedding_failed', 'deleted'

  @Column({ type: 'boolean', default: false })
  is_active: boolean;

  @Column({ type: 'uuid', nullable: true })
  uploaded_by: string;

  @CreateDateColumn({ type: 'timestamp with time zone' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamp with time zone' })
  updated_at: Date;

  // Relations
  @ManyToOne(() => Division, (division) => division.documents, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'division_id' })
  division: Division;

  @ManyToOne(() => User, (user) => user.uploaded_documents, { nullable: true })
  @JoinColumn({ name: 'uploaded_by' })
  uploaded_by_user: User;

  @OneToMany(() => Embedding, (embedding) => embedding.document)
  embeddings: Embedding[];
}
