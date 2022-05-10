from googletrans import Translator


def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text
