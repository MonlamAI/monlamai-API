-- CreateTable
CREATE TABLE "OldSpeechToTexts" (
    "id" TEXT NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "responseTime" TEXT,
    "ipAddress" TEXT,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "editOutput" TEXT,
    "userId" INTEGER,
    "liked_count" INTEGER NOT NULL DEFAULT 0,
    "disliked_count" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "OldSpeechToTexts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "OldTextToSpeech" (
    "id" TEXT NOT NULL,
    "input" TEXT NOT NULL,
    "output" TEXT NOT NULL,
    "responseTime" TEXT,
    "ipAddress" TEXT,
    "version" TEXT,
    "sourceApp" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "country" TEXT,
    "userId" INTEGER,
    "liked_count" INTEGER NOT NULL DEFAULT 0,
    "disliked_count" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "OldTextToSpeech_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "OldSpeechToTexts" ADD CONSTRAINT "OldSpeechToTexts_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "OldTextToSpeech" ADD CONSTRAINT "OldTextToSpeech_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
