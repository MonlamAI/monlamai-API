/*
  Warnings:

  - Changed the type of `latency` on the `Chat` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Changed the type of `token` on the `Chat` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.

*/
-- AlterTable
ALTER TABLE "Chat" DROP COLUMN "latency",
ADD COLUMN     "latency" INTEGER NOT NULL,
DROP COLUMN "token",
ADD COLUMN     "token" INTEGER NOT NULL;
