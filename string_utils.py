import re
import unicodedata
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import logging

logger = logging.getLogger(__name__)

def clean_string(text):
    """
    Preprocessa una stringa musicale rimuovendo parole non significative e normalizzando
    """
    
    # Remove specifics char
    text = text.replace("’", "'")
    text = text.replace("×", "x")
    text = text.replace("·", "")
    text = text.replace("‐", "-")
    text = text.replace("…", "...")
    text = text.replace(" / ", "/")
    text = text.replace("A'", "à")
    text = text.replace("E'", "è")
    text = text.replace("I'", "ì")
    text = text.replace("O'", "ò")
    text = text.replace("U'", "ù")
    text = text.replace("Sansiro", "San siro")
    text = text.replace(" - ", "-")
    text = text.replace("I RIO", "Rio")
    
    text = text.strip().lower()

    # Converti a minuscolo
    text = text.lower()
    
    # Rimuovi parole non significative comuni nelle tracce musicali
    words_to_remove = [
        "remastered", "remaster", "version", "extended", "special", "edition", 
        "deluxe", "feat", "featuring", "ft", "radio edit", "remix", "mix", 
        "original", "bonus track", "live", "acoustic", "instrumental", 
        "explicit", "clean", "album version", "single", "official", "bonus"
        "full", "super", "box", "stereo", "album", "anniversary", "expanded"
        "edit", "vrs", "192 khz", "mono", "ep", "e.p."
    ]
    
    pattern = r'\b(?:' + '|'.join(words_to_remove) + r')\b'
    text = re.sub(pattern, '', text)
    
    # Rimuovi testo in parentesi o bracket (spesso contiene info aggiuntive)
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    
    # Rimuovi anni a 4 cifre (come 1999, 2021, ecc.)
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)

    # Normalizza caratteri unicode (rimuovi accenti)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Rimuovi punteggiatura e caratteri speciali
    text = re.sub(r'[^\w\s]', '', text)
    
    # Rimuovi spazi multipli
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def are_strings_similar(str1, str2, threshold=0.85):
    """
    Determina se due stringhe sono simili usando vari metodi di confronto
    """
    if str1 == str2:
        return True, 1.0
    
    # Preprocess entrambe le stringhe
    clean_str1 = clean_string(str1)
    clean_str2 = clean_string(str2)
    
    # Se dopo la pulizia sono identiche, abbiamo un match
    if clean_str1 == clean_str2:
        return True, 1.0
    
    # Controlla la similarità con più algoritmi
    
    # 1. Sequence Matcher (algoritmo di difflib)
    sequence_ratio = SequenceMatcher(None, clean_str1, clean_str2).ratio()
    #logger.debug(f"sequence_ratio={sequence_ratio}")
    
    # 2. Rapporto di token (parole) - FuzzyWuzzy
    # Installa con: pip install fuzzywuzzy[speedup]
    token_ratio = fuzz.token_sort_ratio(clean_str1, clean_str2) / 100
    #logger.debug(f"token_ratio={token_ratio}")

    # 3. Partial Ratio - utile per quando una stringa è contenuta nell'altra
    partial_ratio = fuzz.partial_ratio(clean_str1, clean_str2) / 100
    #logger.debug(f"partial_ratio={partial_ratio}")
    
    # Calcola un punteggio combinato
    combined_score = (sequence_ratio + token_ratio + partial_ratio) / 3
    
    return combined_score >= threshold, combined_score
