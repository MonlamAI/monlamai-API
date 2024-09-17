-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('Admin', 'User', 'Subscriber');

-- CreateTable
CREATE TABLE "User" (
    "id" SERIAL NOT NULL,
    "username" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "picture" TEXT,
    "role" "UserRole" NOT NULL DEFAULT 'User',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Translation" (
    "id" SERIAL NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "inputLang" TEXT NOT NULL,
    "outputLang" TEXT NOT NULL,
    "responseTime" TEXT NOT NULL,
    "ipAddress" TEXT NOT NULL,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "editOutput" TEXT,
    "userId" INTEGER,

    CONSTRAINT "Translation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SpeechToTexts" (
    "id" SERIAL NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "responseTime" TEXT NOT NULL,
    "ipAddress" TEXT NOT NULL,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "editOutput" TEXT,
    "userId" INTEGER,

    CONSTRAINT "SpeechToTexts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TextToSpeech" (
    "id" SERIAL NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "responseTime" TEXT NOT NULL,
    "ipAddress" TEXT NOT NULL,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "userId" INTEGER,

    CONSTRAINT "TextToSpeech_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "OCR" (
    "id" SERIAL NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "responseTime" TEXT NOT NULL,
    "ipAddress" TEXT NOT NULL,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "editOutput" TEXT,
    "userId" INTEGER,

    CONSTRAINT "OCR_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_LikesTranslations" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_LikesSpeechToTexts" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_LikesTextToSpeechs" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_LikesOCRs" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_LikesTranslations_AB_unique" ON "_LikesTranslations"("A", "B");

-- CreateIndex
CREATE INDEX "_LikesTranslations_B_index" ON "_LikesTranslations"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_LikesSpeechToTexts_AB_unique" ON "_LikesSpeechToTexts"("A", "B");

-- CreateIndex
CREATE INDEX "_LikesSpeechToTexts_B_index" ON "_LikesSpeechToTexts"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_LikesTextToSpeechs_AB_unique" ON "_LikesTextToSpeechs"("A", "B");

-- CreateIndex
CREATE INDEX "_LikesTextToSpeechs_B_index" ON "_LikesTextToSpeechs"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_LikesOCRs_AB_unique" ON "_LikesOCRs"("A", "B");

-- CreateIndex
CREATE INDEX "_LikesOCRs_B_index" ON "_LikesOCRs"("B");

-- AddForeignKey
ALTER TABLE "Translation" ADD CONSTRAINT "Translation_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SpeechToTexts" ADD CONSTRAINT "SpeechToTexts_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TextToSpeech" ADD CONSTRAINT "TextToSpeech_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "OCR" ADD CONSTRAINT "OCR_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesTranslations" ADD CONSTRAINT "_LikesTranslations_A_fkey" FOREIGN KEY ("A") REFERENCES "Translation"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesTranslations" ADD CONSTRAINT "_LikesTranslations_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesSpeechToTexts" ADD CONSTRAINT "_LikesSpeechToTexts_A_fkey" FOREIGN KEY ("A") REFERENCES "SpeechToTexts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesSpeechToTexts" ADD CONSTRAINT "_LikesSpeechToTexts_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesTextToSpeechs" ADD CONSTRAINT "_LikesTextToSpeechs_A_fkey" FOREIGN KEY ("A") REFERENCES "TextToSpeech"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesTextToSpeechs" ADD CONSTRAINT "_LikesTextToSpeechs_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesOCRs" ADD CONSTRAINT "_LikesOCRs_A_fkey" FOREIGN KEY ("A") REFERENCES "OCR"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LikesOCRs" ADD CONSTRAINT "_LikesOCRs_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
