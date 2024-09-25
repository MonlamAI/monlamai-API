-- CreateEnum
CREATE TYPE "Gender" AS ENUM ('Male', 'Female', 'Other');

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "birth_date" TIMESTAMP(3),
ADD COLUMN     "city" TEXT,
ADD COLUMN     "country" TEXT,
ADD COLUMN     "gender" "Gender",
ADD COLUMN     "interest" TEXT,
ADD COLUMN     "profession" TEXT;
