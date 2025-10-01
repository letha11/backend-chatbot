import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Division } from './Division';

@Entity('user_queries')
export class UserQuery {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', nullable: true })
  division_id: string;

  @Column({ type: 'text' })
  query_text: string;

  @Column({ type: 'text', nullable: true })
  response_text: string;

  @CreateDateColumn({ type: 'timestamp with time zone' })
  query_time: Date;

  @Column({ type: 'uuid', nullable: true })
  user_id: string;

  // Relations
  @ManyToOne(() => Division, (division) => division.user_queries, { nullable: true })
  @JoinColumn({ name: 'division_id' })
  division: Division;
}
