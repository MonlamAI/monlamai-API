from sqlalchemy.orm import Session
from models import  Translations, SpeechToTexts, TextToSpeech, OCR

def create_translation(db: Session, translation_data: dict) -> Translations:
    translation = Translations(
        input=translation_data['input'],
        output=translation_data['output'],
        input_lang=translation_data['input_lang'],
        output_lang=translation_data['output_lang'],
        response_time=translation_data['response_time'],
        ip_address=translation_data.get('ip_address'),
        version=translation_data.get('version'),
        source_app=translation_data.get('source_app'),
        user_id=translation_data.get('user_id'),
    )
    db.add(translation)
    db.commit()
    db.refresh(translation)
    return translation

def create_speech_to_text(db: Session, speech_data: dict) -> SpeechToTexts:
    speech_to_text = SpeechToTexts(
        input=speech_data['input'],
        output=speech_data['output'],
        response_time=speech_data['response_time'],
        ip_address=speech_data.get('ip_address'),
        version=speech_data.get('version'),
        source_app=speech_data.get('source_app'),
        user_id=speech_data.get('user_id'),
    )
    db.add(speech_to_text)
    db.commit()
    db.refresh(speech_to_text)
    return speech_to_text

def create_text_to_speech(db: Session, tts_data: dict) -> TextToSpeech:
    text_to_speech = TextToSpeech(
        input=tts_data['input'],
        output=tts_data['output'],
        response_time=tts_data['response_time'],
        ip_address=tts_data.get('ip_address'),
        version=tts_data.get('version'),
        source_app=tts_data.get('source_app'),
        user_id=tts_data.get('user_id'),
    )
    db.add(text_to_speech)
    db.commit()
    db.refresh(text_to_speech)
    return text_to_speech

def create_ocr(db: Session, ocr_data: dict) -> OCR:
    ocr = OCR(
        input=ocr_data['input'],
        output=ocr_data['output'],
        response_time=ocr_data['response_time'],
        ip_address=ocr_data.get('ip_address'),
        version=ocr_data.get('version'),
        source_app=ocr_data.get('source_app'),
        user_id=ocr_data.get('user_id'),
    )
    db.add(ocr)
    db.commit()
    db.refresh(ocr)
    return ocr
