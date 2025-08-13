#!/usr/bin/env python3
"""
Esempio di utilizzo del sistema di report per batch

Questo script mostra come utilizzare il sistema generico di report per batch
con supporto per success, failed e partial success.
"""

import sys
import os
import time
import random
from datetime import datetime

# Aggiungi il path per importare i moduli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_report_utils import (
    create_batch_context, 
    add_success_item, 
    add_failed_item, 
    add_partial_item, 
    finalize_batch,
    BatchReportGenerator,
    BatchResult
)

def simulate_batch_processing():
    """
    Simula un batch di elaborazione con diversi risultati
    """
    print("Avvio simulazione batch...")
    
    # Crea il contesto del batch
    batch_context = create_batch_context(
        name="elaborazione_file_musica",
        metadata={
            "directory_input": "/path/to/music/files",
            "formato_output": "mp3",
            "qualita": "320kbps",
            "modalita": "simulazione"
        }
    )
    
    # Simula l'elaborazione di alcuni file
    files_to_process = [
        {"file": "song1.mp3", "artist": "Artist1", "album": "Album1"},
        {"file": "song2.mp3", "artist": "Artist2", "album": "Album2"},
        {"file": "song3.mp3", "artist": "Artist3", "album": "Album3"},
        {"file": "song4.mp3", "artist": "Artist4", "album": "Album4"},
        {"file": "song5.mp3", "artist": "Artist5", "album": "Album5"},
        {"file": "corrupted.mp3", "artist": "Unknown", "album": "Unknown"},
        {"file": "song6.mp3", "artist": "Artist6", "album": "Album6"},
        {"file": "song7.mp3", "artist": "Artist7", "album": "Album7"},
    ]
    
    for file_info in files_to_process:
        # Simula un po' di elaborazione
        time.sleep(0.1)
        
        # Simula diversi risultati
        result = random.choice(['success', 'failed', 'partial'])
        
        if result == 'success':
            processed_file = {
                "file": file_info["file"],
                "artist": file_info["artist"],
                "album": file_info["album"],
                "status": "processed",
                "output_path": f"/output/{file_info['file']}",
                "processing_time": random.uniform(0.5, 2.0)
            }
            add_success_item(batch_context, processed_file)
            print(f"✓ Processato con successo: {file_info['file']}")
            
        elif result == 'failed':
            failed_file = {
                "file": file_info["file"],
                "artist": file_info["artist"],
                "album": file_info["album"],
                "error_type": "processing_error"
            }
            error_msg = f"Errore durante l'elaborazione di {file_info['file']}"
            add_failed_item(batch_context, failed_file, error_msg)
            print(f"✗ Fallito: {file_info['file']}")
            
        elif result == 'partial':
            partial_file = {
                "file": file_info["file"],
                "artist": file_info["artist"],
                "album": file_info["album"],
                "status": "partially_processed",
                "missing_metadata": ["genre", "year"]
            }
            partial_reason = f"Metadati incompleti per {file_info['file']}"
            add_partial_item(batch_context, partial_file, partial_reason)
            print(f"⚠ Parziale: {file_info['file']}")
    
    # Finalizza il batch e genera il report
    batch_result = finalize_batch(
        context=batch_context,
        output_dir="example_batch_reports",
        save_text=True,
        save_json=True,
        print_summary=True
    )
    
    return batch_result

def example_direct_usage():
    """
    Esempio di utilizzo diretto del BatchReportGenerator
    """
    print("\n" + "="*60)
    print("ESEMPIO UTILIZZO DIRETTO")
    print("="*60)
    
    # Crea il generatore
    generator = BatchReportGenerator("example_direct_reports")
    
    # Crea un risultato di batch direttamente
    start_time = datetime.now()
    time.sleep(1)  # Simula elaborazione
    end_time = datetime.now()
    
    # Dati di esempio
    success_items = [
        {"id": 1, "name": "Item1", "status": "completed"},
        {"id": 2, "name": "Item2", "status": "completed"}
    ]
    
    failed_items = [
        {"id": 3, "name": "Item3", "error": "Connection timeout"}
    ]
    
    partial_items = [
        {"id": 4, "name": "Item4", "partial_reason": "Missing data"}
    ]
    
    # Crea il risultato
    batch_result = generator.create_batch_result(
        name="test_direct_batch",
        start_time=start_time,
        end_time=end_time,
        success_items=success_items,
        failed_items=failed_items,
        partial_items=partial_items,
        metadata={"test_mode": True, "version": "1.0"},
        error_messages=["Connection timeout for Item3"]
    )
    
    # Salva i report
    saved_files = generator.save_report(batch_result)
    print(f"File salvati: {saved_files}")
    
    # Stampa il riassunto
    generator.print_summary(batch_result)

def example_custom_data_structures():
    """
    Esempio con strutture dati personalizzate
    """
    print("\n" + "="*60)
    print("ESEMPIO STRUTTURE DATI PERSONALIZZATE")
    print("="*60)
    
    # Crea il contesto
    batch_context = create_batch_context(
        name="sync_spotify_playlist",
        metadata={
            "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",
            "playlist_name": "Today's Top Hits",
            "sync_mode": "full"
        }
    )
    
    # Aggiungi elementi con strutture dati complesse
    add_success_item(batch_context, {
        "track_id": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
        "track_name": "Blinding Lights",
        "artist": "The Weeknd",
        "album": "After Hours",
        "added_to_playlist": True,
        "spotify_data": {
            "popularity": 95,
            "duration_ms": 200040,
            "explicit": False
        }
    })
    
    add_failed_item(batch_context, {
        "track_id": "spotify:track:invalid_id",
        "track_name": "Unknown Track",
        "error_code": "TRACK_NOT_FOUND",
        "retry_count": 3
    }, "Track non trovato su Spotify")
    
    add_partial_item(batch_context, {
        "track_id": "spotify:track:partial_id",
        "track_name": "Partial Track",
        "artist": "Unknown Artist",
        "missing_data": ["album", "release_date"],
        "partial_match_score": 0.7
    }, "Match parziale - dati incompleti")
    
    # Finalizza
    finalize_batch(batch_context, "custom_data_reports")

if __name__ == "__main__":
    print("ESEMPI UTILIZZO SISTEMA REPORT BATCH")
    print("="*60)
    
    # Esempio 1: Utilizzo con contesto
    batch_result = simulate_batch_processing()
    
    # Esempio 2: Utilizzo diretto
    example_direct_usage()
    
    # Esempio 3: Strutture dati personalizzate
    example_custom_data_structures()
    
    print("\n" + "="*60)
    print("TUTTI GLI ESEMPI COMPLETATI!")
    print("Controlla le cartelle:")
    print("- example_batch_reports/")
    print("- example_direct_reports/")
    print("- custom_data_reports/")
    print("="*60) 