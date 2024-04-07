import spacy

def vaidate_spanish_word(text: str) -> bool:
    nlp = spacy.load('es_core_news_md')
    if len(text.split(' ')) > 1:
        return 'OTHER'
    pos = nlp(text)
    if pos[0].pos_ in ('NOUN', 'VERB', 'ADJ'):
        return pos[0].pos_
    return 'OTHER'
