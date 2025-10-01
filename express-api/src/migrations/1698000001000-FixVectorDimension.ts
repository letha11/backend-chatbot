import { MigrationInterface, QueryRunner } from 'typeorm';

export class FixVectorDimension1698000001000 implements MigrationInterface {
  name = 'FixVectorDimension1698000001000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    // Fix vector dimension from 1536 to 384 for SentenceTransformers compatibility
    
    // First, check if the embeddings table exists and has the old dimension
    const tableExists = await queryRunner.hasTable('embeddings');
    
    if (tableExists) {
      // Clear existing embeddings (they're incompatible anyway)
      await queryRunner.query(`TRUNCATE TABLE "embeddings"`);
      
      // Drop the existing vector column
      await queryRunner.query(`ALTER TABLE "embeddings" DROP COLUMN IF EXISTS "embedding"`);
      
      // Add the new vector column with 384 dimensions
      await queryRunner.query(`ALTER TABLE "embeddings" ADD COLUMN "embedding" vector(384) NOT NULL`);
      
      // Reset document status for re-embedding
      await queryRunner.query(`UPDATE "documents" SET "status" = 'parsed' WHERE "status" = 'embedded'`);
    }
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Revert back to 1536 dimensions (for OpenAI embeddings)
    const tableExists = await queryRunner.hasTable('embeddings');
    
    if (tableExists) {
      // Clear existing embeddings
      await queryRunner.query(`TRUNCATE TABLE "embeddings"`);
      
      // Drop the existing vector column
      await queryRunner.query(`ALTER TABLE "embeddings" DROP COLUMN IF EXISTS "embedding"`);
      
      // Add the vector column with 1536 dimensions
      await queryRunner.query(`ALTER TABLE "embeddings" ADD COLUMN "embedding" vector(1536) NOT NULL`);
      
      // Reset document status
      await queryRunner.query(`UPDATE "documents" SET "status" = 'parsed' WHERE "status" = 'embedded'`);
    }
  }
}




