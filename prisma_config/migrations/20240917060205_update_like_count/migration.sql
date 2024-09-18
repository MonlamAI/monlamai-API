/*
  Warnings:

  - You are about to drop the `_DislikesOCR` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_DislikesSpeechToTexts` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_DislikesTextToSpeechs` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_DislikesTranslations` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_LikesOCRs` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_LikesSpeechToTexts` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_LikesTextToSpeechs` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `_LikesTranslations` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "_DislikesOCR" DROP CONSTRAINT "_DislikesOCR_A_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesOCR" DROP CONSTRAINT "_DislikesOCR_B_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesSpeechToTexts" DROP CONSTRAINT "_DislikesSpeechToTexts_A_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesSpeechToTexts" DROP CONSTRAINT "_DislikesSpeechToTexts_B_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesTextToSpeechs" DROP CONSTRAINT "_DislikesTextToSpeechs_A_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesTextToSpeechs" DROP CONSTRAINT "_DislikesTextToSpeechs_B_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesTranslations" DROP CONSTRAINT "_DislikesTranslations_A_fkey";

-- DropForeignKey
ALTER TABLE "_DislikesTranslations" DROP CONSTRAINT "_DislikesTranslations_B_fkey";

-- DropForeignKey
ALTER TABLE "_LikesOCRs" DROP CONSTRAINT "_LikesOCRs_A_fkey";

-- DropForeignKey
ALTER TABLE "_LikesOCRs" DROP CONSTRAINT "_LikesOCRs_B_fkey";

-- DropForeignKey
ALTER TABLE "_LikesSpeechToTexts" DROP CONSTRAINT "_LikesSpeechToTexts_A_fkey";

-- DropForeignKey
ALTER TABLE "_LikesSpeechToTexts" DROP CONSTRAINT "_LikesSpeechToTexts_B_fkey";

-- DropForeignKey
ALTER TABLE "_LikesTextToSpeechs" DROP CONSTRAINT "_LikesTextToSpeechs_A_fkey";

-- DropForeignKey
ALTER TABLE "_LikesTextToSpeechs" DROP CONSTRAINT "_LikesTextToSpeechs_B_fkey";

-- DropForeignKey
ALTER TABLE "_LikesTranslations" DROP CONSTRAINT "_LikesTranslations_A_fkey";

-- DropForeignKey
ALTER TABLE "_LikesTranslations" DROP CONSTRAINT "_LikesTranslations_B_fkey";

-- AlterTable
ALTER TABLE "OCR" ADD COLUMN     "disliked_count" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "liked_count" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "SpeechToTexts" ADD COLUMN     "disliked_count" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "liked_count" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "TextToSpeech" ADD COLUMN     "disliked_count" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "liked_count" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "Translation" ADD COLUMN     "disliked_count" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "liked_count" INTEGER NOT NULL DEFAULT 0;

-- DropTable
DROP TABLE "_DislikesOCR";

-- DropTable
DROP TABLE "_DislikesSpeechToTexts";

-- DropTable
DROP TABLE "_DislikesTextToSpeechs";

-- DropTable
DROP TABLE "_DislikesTranslations";

-- DropTable
DROP TABLE "_LikesOCRs";

-- DropTable
DROP TABLE "_LikesSpeechToTexts";

-- DropTable
DROP TABLE "_LikesTextToSpeechs";

-- DropTable
DROP TABLE "_LikesTranslations";
