import { MigrationInterface, QueryRunner } from 'typeorm';

export class InitialSchema1698000000000 implements MigrationInterface {
  name = 'InitialSchema1698000000000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    // Enable pgvector extension
    await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS "vector"`);
    await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`);

    // Create users table
    await queryRunner.query(`
      CREATE TABLE "users" (
        "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
        "username" character varying(255) NOT NULL,
        "password_hash" character varying(255) NOT NULL,
        "role" character varying(50) NOT NULL DEFAULT 'admin',
        "is_active" boolean NOT NULL DEFAULT true,
        "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        CONSTRAINT "UQ_users_username" UNIQUE ("username"),
        CONSTRAINT "PK_users_id" PRIMARY KEY ("id")
      )
    `);

    // Create divisions table
    await queryRunner.query(`
      CREATE TABLE "divisions" (
        "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
        "name" character varying(255) NOT NULL,
        "description" text,
        "is_active" boolean NOT NULL DEFAULT true,
        "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        CONSTRAINT "UQ_divisions_name" UNIQUE ("name"),
        CONSTRAINT "PK_divisions_id" PRIMARY KEY ("id")
      )
    `);

    // Create documents table
    await queryRunner.query(`
      CREATE TABLE "documents" (
        "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
        "division_id" uuid NOT NULL,
        "original_filename" character varying(255) NOT NULL,
        "storage_path" character varying(255) NOT NULL,
        "file_type" character varying(50) NOT NULL,
        "status" character varying(50) NOT NULL DEFAULT 'uploaded',
        "is_active" boolean NOT NULL DEFAULT false,
        "uploaded_by" uuid,
        "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        CONSTRAINT "PK_documents_id" PRIMARY KEY ("id"),
        CONSTRAINT "FK_documents_division_id" FOREIGN KEY ("division_id") REFERENCES "divisions"("id") ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT "FK_documents_uploaded_by" FOREIGN KEY ("uploaded_by") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE
      )
    `);

    // Create embeddings table
    await queryRunner.query(`
      CREATE TABLE "embeddings" (
        "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
        "document_id" uuid NOT NULL,
        "chunk_text" text NOT NULL,
        "embedding" vector(384) NOT NULL,
        "chunk_index" integer NOT NULL,
        "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        CONSTRAINT "PK_embeddings_id" PRIMARY KEY ("id"),
        CONSTRAINT "FK_embeddings_document_id" FOREIGN KEY ("document_id") REFERENCES "documents"("id") ON DELETE CASCADE ON UPDATE CASCADE
      )
    `);

    // Create user_queries table
    await queryRunner.query(`
      CREATE TABLE "user_queries" (
        "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
        "division_id" uuid,
        "query_text" text NOT NULL,
        "response_text" text,
        "query_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        "user_id" uuid,
        CONSTRAINT "PK_user_queries_id" PRIMARY KEY ("id"),
        CONSTRAINT "FK_user_queries_division_id" FOREIGN KEY ("division_id") REFERENCES "divisions"("id") ON DELETE SET NULL ON UPDATE CASCADE
      )
    `);

    // Create indexes for performance
    await queryRunner.query(`CREATE INDEX "IDX_documents_division_id" ON "documents" ("division_id")`);
    await queryRunner.query(`CREATE INDEX "IDX_documents_status" ON "documents" ("status")`);
    await queryRunner.query(`CREATE INDEX "IDX_documents_is_active" ON "documents" ("is_active")`);
    await queryRunner.query(`CREATE INDEX "IDX_embeddings_document_id" ON "embeddings" ("document_id")`);
    await queryRunner.query(`CREATE INDEX "IDX_user_queries_division_id" ON "user_queries" ("division_id")`);
    
    // Create vector similarity index for embeddings
    await queryRunner.query(`CREATE INDEX "IDX_embeddings_embedding_cosine" ON "embeddings" USING ivfflat ("embedding" vector_cosine_ops) WITH (lists = 100)`);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Drop tables in reverse order
    await queryRunner.query(`DROP TABLE "user_queries"`);
    await queryRunner.query(`DROP TABLE "embeddings"`);
    await queryRunner.query(`DROP TABLE "documents"`);
    await queryRunner.query(`DROP TABLE "divisions"`);
    await queryRunner.query(`DROP TABLE "users"`);
    
    // Drop extensions
    await queryRunner.query(`DROP EXTENSION IF EXISTS "vector"`);
    await queryRunner.query(`DROP EXTENSION IF EXISTS "uuid-ossp"`);
  }
}
