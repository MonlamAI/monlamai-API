/*
  Warnings:

  - Added the required column `latency` to the `Chat` table without a default value. This is not possible if the table is not empty.
  - Added the required column `model` to the `Chat` table without a default value. This is not possible if the table is not empty.
  - Added the required column `token` to the `Chat` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Chat" ADD COLUMN     "edit_input" TEXT,
ADD COLUMN     "edit_output" TEXT,
ADD COLUMN     "latency" TEXT NOT NULL,
ADD COLUMN     "model" TEXT NOT NULL,
ADD COLUMN     "token" TEXT NOT NULL;
