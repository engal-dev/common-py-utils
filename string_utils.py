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
    clean_str1, clean_step1_changes, _ = clean_string_extended(str1)
    clean_str2, clean_step2_changes, _ = clean_string_extended(str2)
    #clean_str1 = clean_string(str1)
    #clean_str2 = clean_string(str2)
    
    # Calcola una penalità basata sul numero di modifiche effettive.
    # 0.01 per ogni modifica.
    penality = (0.01 * sum(clean_step1_changes.values())) + (0.01 * sum(clean_step2_changes.values()))
    #penality=0.0

    # Se dopo la pulizia sono identiche, abbiamo un match
    if clean_str1 == clean_str2:
        return True, max(0, 1.0 - penality)
    
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

    final_score = combined_score - penality
    
    return final_score >= threshold, max(0, final_score)

def clean_string_extended(text, ignore_debug_steps=None, debug_steps=None):
    """
    Come clean_string, ma tiene traccia di ogni modifica e restituisce:
    - la stringa pulita
    - un report dettagliato dei passaggi (nome, cambiamento, prima, dopo)
    - un dizionario di booleani per i passaggi configurabili
    debug_steps: lista opzionale di nomi di step per cui vuoi il booleano di modifica
    """
    report = []
    step_changes = {}
    if debug_steps is None:
        debug_steps = []
    if ignore_debug_steps is None:
        ignore_debug_steps = ["replace specifics char", "strip", "lower", "normalize unicode", "remove multiple spaces"]
    
    def track(step_name, func):
        nonlocal text
        before = text
        text = func(text)
        changed = before != text
        report.append({
            'step': step_name,
            'changed': changed,
            'before': before,
            'after': text
        })
        if step_name in debug_steps:
            step_changes[step_name] = changed
        elif step_name not in ignore_debug_steps:
            step_changes[step_name] = changed
        
        return changed

    # 1. Replace specifics char
    track("replace specifics char", lambda t: t.replace("’", "'")
                                         .replace("×", "x")
                                         .replace("·", "")
                                         .replace("‐", "-")
                                         .replace("…", "...")
                                         .replace(" / ", "/")
                                         .replace("A'", "à")
                                         .replace("E'", "è")
                                         .replace("I'", "ì")
                                         .replace("O'", "ò")
                                         .replace("U'", "ù")
                                         .replace("Sansiro", "San siro")
                                         .replace(" - ", "-")
                                         .replace("I RIO", "Rio"))

    # 2. Strip e lower
    track("strip", lambda t: t.strip())
    track("lower", lambda t: t.lower())

    # 3. Rimuovi parole non significative
    words_to_remove = [
        "remastered", "remaster", "version", "extended", "special", "edition", 
        "deluxe", "feat", "featuring", "ft", "radio edit", "remix", "mix", 
        "original", "bonus track", "live", "acoustic", "instrumental", 
        "explicit", "clean", "album version", "single", "official", "bonus",
        "full", "super", "box", "stereo", "album", "anniversary", "expanded",
        "edit", "vrs", "192 khz", "mono", "ep", "e.p."
    ]
    pattern = r'\b(?:' + '|'.join(words_to_remove) + r')\b'
    track("remove words_to_remove", lambda t: re.sub(pattern, '', t))

    # 4. Rimuovi testo in parentesi o bracket
    #track("remove round brackets", lambda t: re.sub(r'\([^)]*\)', '', t))
    #track("remove square brackets", lambda t: re.sub(r'\[[^\]]*\]', '', t))

    # 4.5. Rimuovi solo le parentesi (opzionale - alternativa ai passaggi 4)
    track("remove brackets only", lambda t: re.sub(r'[\(\)\[\]]', '', t))

    # 5. Rimuovi anni a 4 cifre
    track("remove years", lambda t: re.sub(r'\b(19|20)\d{2}\b', '', t))

    # 6. Normalizza caratteri unicode
    track("normalize unicode", lambda t: unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('utf-8'))

    # 7. Rimuovi punteggiatura e caratteri speciali
    track("remove punctuation", lambda t: re.sub(r'[^\w\s]', '', t))

    # 8. Rimuovi spazi multipli
    track("remove multiple spaces", lambda t: re.sub(r'\s+', ' ', t).strip())

    return text, step_changes, report
