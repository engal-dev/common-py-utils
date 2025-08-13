# Sistema di Report per Batch

Questo modulo fornisce un sistema generico e flessibile per generare report sui batch di elaborazione, con supporto per tre categorie di risultati: **success**, **failed** e **partial success**.

## Caratteristiche Principali

- ✅ **Gestione automatica degli stati**: Determina automaticamente se il batch è success, failed o partial
- 📊 **Statistiche complete**: Conteggi, tassi di successo, durata
- 📝 **Report multipli**: Testuale e JSON
- 🕒 **Timing automatico**: Traccia ora inizio, fine e durata
- 🔧 **Flessibilità**: Supporta qualsiasi struttura dati per gli elementi
- 📁 **Organizzazione**: Salva i report in directory timestampate

## Struttura dei Dati

### Categorie di Risultati

1. **SUCCESS**: Elementi processati completamente con successo
2. **FAILED**: Elementi che hanno fallito completamente
3. **PARTIAL**: Elementi con successo parziale (alcuni dati mancanti, warning, ecc.)

### Formato degli Elementi

Gli elementi possono essere **dizionari Python** con qualsiasi struttura. Il sistema è flessibile e si adatta ai tuoi dati:

```python
# Esempio di elemento success
{
    "file": "song.mp3",
    "artist": "Artist Name",
    "album": "Album Name",
    "status": "processed",
    "output_path": "/output/song.mp3"
}

# Esempio di elemento failed
{
    "file": "corrupted.mp3",
    "error_type": "file_corrupted",
    "error_code": "E001"
}

# Esempio di elemento partial
{
    "file": "song.mp3",
    "artist": "Artist Name",
    "missing_metadata": ["genre", "year"],
    "partial_reason": "Metadati incompleti"
}
```

## Utilizzo Base

### Metodo 1: Utilizzo con Contesto (Raccomandato)

```python
from batch_report_utils import (
    create_batch_context, 
    add_success_item, 
    add_failed_item, 
    add_partial_item, 
    finalize_batch
)

# 1. Crea il contesto del batch
batch_context = create_batch_context(
    name="elaborazione_musica",
    metadata={
        "directory_input": "/path/to/files",
        "formato_output": "mp3"
    }
)

# 2. Durante l'elaborazione, aggiungi elementi
for item in items_to_process:
    try:
        result = process_item(item)
        if result.is_complete():
            add_success_item(batch_context, {
                "file": item.name,
                "status": "processed",
                "output": result.output_path
            })
        elif result.is_partial():
            add_partial_item(batch_context, {
                "file": item.name,
                "missing_data": result.missing_fields
            }, "Dati incompleti")
        else:
            add_failed_item(batch_context, {
                "file": item.name,
                "error": result.error
            }, f"Errore: {result.error}")
    except Exception as e:
        add_failed_item(batch_context, {
            "file": item.name,
            "exception": str(e)
        }, f"Eccezione: {e}")

# 3. Finalizza e genera il report
batch_result = finalize_batch(
    context=batch_context,
    output_dir="reports",
    save_text=True,
    save_json=True,
    print_summary=True
)
```

### Metodo 2: Utilizzo Diretto

```python
from batch_report_utils import BatchReportGenerator
from datetime import datetime

# Crea il generatore
generator = BatchReportGenerator("reports")

# Crea il risultato direttamente
batch_result = generator.create_batch_result(
    name="test_batch",
    start_time=datetime.now(),
    end_time=datetime.now(),
    success_items=[{"id": 1, "name": "Item1"}],
    failed_items=[{"id": 2, "name": "Item2", "error": "Not found"}],
    partial_items=[{"id": 3, "name": "Item3", "partial_reason": "Missing data"}],
    metadata={"version": "1.0"},
    error_messages=["Item2 not found"]
)

# Salva i report
saved_files = generator.save_report(batch_result)
```

## Output dei Report

### Report Testuale

```
REPORT BATCH: ELABORAZIONE_MUSICA
============================================================
Data/Ora: 2025-01-15 14:30:25
Stato: PARTIAL
Durata: 2m 15s
Ora inizio: 14:28:10
Ora fine: 14:30:25

STATISTICHE:
--------------------
Totale elementi: 100
Successi: 85
Fallimenti: 10
Parziali: 5
Tasso di successo: 85.0%

METADATI:
--------------------
Directory Input: /path/to/files
Formato Output: mp3

ERRORI:
--------------------
- Errore: File non trovato
- Errore: Permessi insufficienti

DETTAGLI SUCCESSI (85 elementi):
----------------------------------------
1. song1.mp3
2. song2.mp3
3. song3.mp3
... e altri 82 elementi

DETTAGLI FALLIMENTI (10 elementi):
----------------------------------------
1. corrupted.mp3: File corrotto
2. missing.mp3: File non trovato
... e altri 8 elementi

DETTAGLI PARZIALI (5 elementi):
----------------------------------------
1. incomplete.mp3: Metadati mancanti
... e altri 4 elementi
```

### Report JSON

```json
{
  "batch_info": {
    "name": "elaborazione_musica",
    "status": "partial",
    "start_time": "2025-01-15T14:28:10.123456",
    "end_time": "2025-01-15T14:30:25.654321",
    "duration_seconds": 135.530865,
    "duration_formatted": "2m 15s"
  },
  "statistics": {
    "total_count": 100,
    "success_count": 85,
    "failed_count": 10,
    "partial_count": 5,
    "success_rate": 85.0
  },
  "metadata": {
    "directory_input": "/path/to/files",
    "formato_output": "mp3"
  },
  "error_messages": [
    "Errore: File non trovato",
    "Errore: Permessi insufficienti"
  ],
  "results": {
    "success_items": [...],
    "failed_items": [...],
    "partial_items": [...]
  }
}
```

## Integrazione con i Tuoi Batch Esistenti

### Esempio: Adattamento di un Batch Spotify

```python
# Prima (senza sistema di report)
def sync_spotify_library():
    stats = {"processed": 0, "errors": 0}
    for file in music_files:
        try:
            sync_file(file)
            stats["processed"] += 1
        except Exception as e:
            stats["errors"] += 1
            print(f"Errore: {e}")
    
    print(f"Completato: {stats['processed']} file, {stats['errors']} errori")

# Dopo (con sistema di report)
def sync_spotify_library():
    batch_context = create_batch_context(
        name="spotify_sync",
        metadata={"library_path": "/music", "write_tags": True}
    )
    
    for file in music_files:
        try:
            result = sync_file(file)
            if result.is_complete():
                add_success_item(batch_context, {
                    "file": file,
                    "spotify_id": result.spotify_id,
                    "metadata_updated": result.metadata_updated
                })
            elif result.is_partial():
                add_partial_item(batch_context, {
                    "file": file,
                    "partial_match": result.partial_match,
                    "missing_fields": result.missing_fields
                }, "Match parziale")
        except Exception as e:
            add_failed_item(batch_context, {
                "file": file,
                "error_type": type(e).__name__
            }, str(e))
    
    finalize_batch(batch_context, "spotify_reports")
```

## Vantaggi del Sistema

1. **Standardizzazione**: Tutti i batch avranno lo stesso formato di report
2. **Tracciabilità**: Facile vedere cosa è successo in ogni batch
3. **Debugging**: I dettagli degli errori sono sempre disponibili
4. **Analisi**: I report JSON permettono analisi automatiche
5. **Flessibilità**: Si adatta a qualsiasi tipo di batch
6. **Manutenibilità**: Codice più pulito e organizzato

## File di Output

Il sistema crea automaticamente:

- `{batch_name}_{timestamp}_report.txt` - Report testuale leggibile
- `{batch_name}_{timestamp}_detailed.json` - Report JSON completo
- Directory organizzate per tipo di batch

## Esempi Pratici

Vedi il file `example_batch_usage.py` per esempi completi di utilizzo con diversi scenari. 