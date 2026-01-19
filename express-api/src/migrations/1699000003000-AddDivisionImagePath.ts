import { MigrationInterface, QueryRunner } from 'typeorm';

export class AddDivisionImagePath1699000003000 implements MigrationInterface {
  name = 'AddDivisionImagePath1699000003000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      ALTER TABLE "divisions" 
      ADD COLUMN IF NOT EXISTS "image_path" varchar(255) NULL;
    `);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      ALTER TABLE "divisions" 
      DROP COLUMN IF EXISTS "image_path";
    `);
  }
}
