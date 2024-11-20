/*
  Warnings:

  - The primary key for the `Chat` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - The primary key for the `OCR` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - The primary key for the `SpeechToTexts` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - The primary key for the `TextToSpeech` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- AlterTable
ALTER TABLE "Chat" DROP CONSTRAINT "Chat_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "Chat_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "Chat_id_seq";

-- AlterTable
ALTER TABLE "OCR" DROP CONSTRAINT "OCR_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "OCR_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "OCR_id_seq";

-- AlterTable
ALTER TABLE "SpeechToTexts" DROP CONSTRAINT "SpeechToTexts_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "SpeechToTexts_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "SpeechToTexts_id_seq";

-- AlterTable
ALTER TABLE "TextToSpeech" DROP CONSTRAINT "TextToSpeech_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ADD CONSTRAINT "TextToSpeech_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "TextToSpeech_id_seq";
