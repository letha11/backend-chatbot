import { MigrationInterface, QueryRunner } from 'typeorm';

export class AddConversationTables1699000002000 implements MigrationInterface {
  name = 'AddConversationTables1699000002000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      CREATE TABLE IF NOT EXISTS "conversations" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "title" varchar(255) NOT NULL,
        "user_id" uuid NULL,
        "division_id" uuid NULL,
        "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
        "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `);

    await queryRunner.query(`
      CREATE TABLE IF NOT EXISTS "conversation_messages" (
        "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
        "conversation_id" uuid NOT NULL,
        "role" varchar(20) NOT NULL,
        "content" text NOT NULL,
        "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT "FK_conversation" FOREIGN KEY ("conversation_id") REFERENCES "conversations"("id") ON DELETE CASCADE
      );
    `);

    await queryRunner.query(`CREATE INDEX IF NOT EXISTS "IDX_conversation_messages_created_at" ON "conversation_messages" ("created_at");`);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP INDEX IF EXISTS "IDX_conversation_messages_created_at";`);
    await queryRunner.query(`DROP TABLE IF EXISTS "conversation_messages";`);
    await queryRunner.query(`DROP TABLE IF EXISTS "conversations";`);
  }
}


