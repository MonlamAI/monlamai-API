/*
  Warnings:

  - The primary key for the `Thread` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- DropForeignKey
ALTER TABLE "Chat" DROP CONSTRAINT "Chat_threadId_fkey";

-- AlterTable
ALTER TABLE "Chat" ALTER COLUMN "threadId" SET DATA TYPE TEXT;

-- AlterTable
ALTER TABLE "Thread" DROP CONSTRAINT "Thread_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "Thread_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "Thread_id_seq";

-- AddForeignKey
ALTER TABLE "Chat" ADD CONSTRAINT "Chat_threadId_fkey" FOREIGN KEY ("threadId") REFERENCES "Thread"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
