/*
  Warnings:

  - The primary key for the `Translation` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- AlterTable
ALTER TABLE "Translation" DROP CONSTRAINT "Translation_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "Translation_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "Translation_id_seq";
