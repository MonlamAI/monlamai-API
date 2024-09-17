-- CreateTable
CREATE TABLE "_DislikesTranslations" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_DislikesSpeechToTexts" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_DislikesTextToSpeechs" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_DislikesOCR" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_DislikesTranslations_AB_unique" ON "_DislikesTranslations"("A", "B");

-- CreateIndex
CREATE INDEX "_DislikesTranslations_B_index" ON "_DislikesTranslations"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_DislikesSpeechToTexts_AB_unique" ON "_DislikesSpeechToTexts"("A", "B");

-- CreateIndex
CREATE INDEX "_DislikesSpeechToTexts_B_index" ON "_DislikesSpeechToTexts"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_DislikesTextToSpeechs_AB_unique" ON "_DislikesTextToSpeechs"("A", "B");

-- CreateIndex
CREATE INDEX "_DislikesTextToSpeechs_B_index" ON "_DislikesTextToSpeechs"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_DislikesOCR_AB_unique" ON "_DislikesOCR"("A", "B");

-- CreateIndex
CREATE INDEX "_DislikesOCR_B_index" ON "_DislikesOCR"("B");

-- AddForeignKey
ALTER TABLE "_DislikesTranslations" ADD CONSTRAINT "_DislikesTranslations_A_fkey" FOREIGN KEY ("A") REFERENCES "Translation"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesTranslations" ADD CONSTRAINT "_DislikesTranslations_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesSpeechToTexts" ADD CONSTRAINT "_DislikesSpeechToTexts_A_fkey" FOREIGN KEY ("A") REFERENCES "SpeechToTexts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesSpeechToTexts" ADD CONSTRAINT "_DislikesSpeechToTexts_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesTextToSpeechs" ADD CONSTRAINT "_DislikesTextToSpeechs_A_fkey" FOREIGN KEY ("A") REFERENCES "TextToSpeech"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesTextToSpeechs" ADD CONSTRAINT "_DislikesTextToSpeechs_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesOCR" ADD CONSTRAINT "_DislikesOCR_A_fkey" FOREIGN KEY ("A") REFERENCES "OCR"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DislikesOCR" ADD CONSTRAINT "_DislikesOCR_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
