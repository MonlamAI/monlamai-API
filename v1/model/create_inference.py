from fastapi import Depends
from prisma.models import Translation, SpeechToTexts, TextToSpeech, OCR
from v1.Config.Connection import db,prisma_connection


async def create_translation( translation_data: dict) -> Translation:
   
    data = {
        'input': translation_data['input'],
        'output': translation_data['output'],
        'inputLang': translation_data['input_lang'],
        'outputLang': translation_data['output_lang'],
        'responseTime': str(round(translation_data['response_time'])),
        'ipAddress': translation_data.get('ip_address'),
        'version': translation_data.get('version'),
        'sourceApp': translation_data.get('source_app'),
        'userId': translation_data.get('user_id'),
        'city': translation_data.get('city'),
        'country': translation_data.get('country'),
    }
    if 'id' in translation_data:
        data['id'] = translation_data['id']
    translation = await db.translation.create(data=data)
    return translation

async def create_speech_to_text( speech_data: dict) -> SpeechToTexts:
    data={
            'input': speech_data['input'],
            'output': speech_data['output'],
            'responseTime': str(round(speech_data['response_time'])),
            'ipAddress': speech_data.get('ip_address'),
            'version': speech_data.get('version'),
            'sourceApp': speech_data.get('source_app'),
            'userId': speech_data.get('user_id'),
            'city': speech_data.get('city'),
            'country': speech_data.get('country'),
        }
    if 'id' in speech_data:
        data['id'] = speech_data['id']
    speech_to_text = await db.speechtotexts.create(
        data=data
    )
    return speech_to_text

async def create_text_to_speech( tts_data: dict) -> TextToSpeech:
    data={
            'input': tts_data['input'],
            'output': tts_data['output'],
            'responseTime': str(round(tts_data['response_time'])),
            'ipAddress': tts_data.get('ip_address'),
            'version': tts_data.get('version'),
            'sourceApp': tts_data.get('source_app'),
            'userId': tts_data.get('user_id'),
            'city': tts_data.get('city'),
            'country': tts_data.get('country'),
        }
    if 'id' in tts_data:
        data['id'] = tts_data['id']
    text_to_speech = await db.texttospeech.create(
        data=data
    )
    return text_to_speech

async def create_ocr(ocr_data: dict) -> OCR:
    data={
            'input': ocr_data['input'],
            'output': ocr_data['output'],
            'responseTime': str(round(ocr_data['response_time'])),
            'ipAddress': ocr_data.get('ip_address'),
            'version': ocr_data.get('version'),
            'sourceApp': ocr_data.get('source_app'),
            'userId': ocr_data.get('user_id'),
            'city': ocr_data.get('city'),
            'country': ocr_data.get('country'),
        }
    if 'id' in ocr_data:
        data['id'] = ocr_data['id']
    return await db.ocr.create(
        data=data
    )