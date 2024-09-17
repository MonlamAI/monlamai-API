-- AlterTable
ALTER TABLE "OCR" ALTER COLUMN "responseTime" DROP NOT NULL,
ALTER COLUMN "ipAddress" DROP NOT NULL;

-- AlterTable
ALTER TABLE "SpeechToTexts" ALTER COLUMN "responseTime" DROP NOT NULL,
ALTER COLUMN "ipAddress" DROP NOT NULL;

-- AlterTable
ALTER TABLE "TextToSpeech" ALTER COLUMN "responseTime" DROP NOT NULL,
ALTER COLUMN "ipAddress" DROP NOT NULL;

-- AlterTable
ALTER TABLE "Translation" ALTER COLUMN "responseTime" DROP NOT NULL,
ALTER COLUMN "ipAddress" DROP NOT NULL;
