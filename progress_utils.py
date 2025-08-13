"""
Progress Utilities - Sistema avanzato per progress bar riutilizzabili

Questo modulo fornisce classi per gestire progress bar avanzate con:
- ETA dinamico
- Velocità di elaborazione
- Statistiche in tempo reale
- Integrazione con logging
- Supporto per operazioni batch
"""

import time
import sys
import threading
from typing import Optional, Callable, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProgressStats:
    """Statistiche del progresso"""
    total: int
    completed: int
    failed: int = 0
    skipped: int = 0
    start_time: datetime = None
    last_update: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.last_update is None:
            self.last_update = datetime.now()
    
    @property
    def remaining(self) -> int:
        """Elementi rimanenti"""
        return self.total - self.completed - self.failed - self.skipped
    
    @property
    def processed(self) -> int:
        """Elementi processati totali"""
        return self.completed + self.failed + self.skipped
    
    @property
    def progress_ratio(self) -> float:
        """Ratio di progresso (0.0 - 1.0)"""
        return self.processed / self.total if self.total > 0 else 0.0
    
    @property
    def progress_percentage(self) -> float:
        """Percentuale di progresso"""
        return self.progress_ratio * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Tempo trascorso"""
        return datetime.now() - self.start_time
    
    @property
    def rate_per_second(self) -> float:
        """Velocità di elaborazione (item/sec)"""
        elapsed = self.elapsed_time.total_seconds()
        return self.processed / elapsed if elapsed > 0 else 0.0
    
    @property
    def eta(self) -> Optional[timedelta]:
        """Tempo stimato al completamento"""
        if self.rate_per_second > 0 and self.remaining > 0:
            seconds_remaining = self.remaining / self.rate_per_second
            return timedelta(seconds=seconds_remaining)
        return None


class ProgressDisplay:
    """Gestisce la visualizzazione della progress bar"""
    
    def __init__(self, 
                 width: int = 50,
                 show_eta: bool = True,
                 show_rate: bool = True,
                 show_stats: bool = True,
                 use_colors: bool = True):
        self.width = width
        self.show_eta = show_eta
        self.show_rate = show_rate
        self.show_stats = show_stats
        self.use_colors = use_colors
        
        # Caratteri per la progress bar
        self.fill_char = '█'
        self.empty_char = '░'
        
        # Colori ANSI (se supportati)
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m', 
            'red': '\033[91m',
            'blue': '\033[94m',
            'reset': '\033[0m'
        } if use_colors else {}
    
    def format_time(self, td: timedelta) -> str:
        """Formatta un timedelta in formato leggibile"""
        if td is None:
            return "N/A"
        
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def format_rate(self, rate: float) -> str:
        """Formatta la velocità di elaborazione"""
        if rate >= 1:
            return f"{rate:.1f}/s"
        elif rate >= 0.1:
            return f"{rate:.2f}/s"
        else:
            return f"{rate:.3f}/s"
    
    def create_bar(self, stats: ProgressStats, description: str = "") -> str:
        """Crea la stringa della progress bar"""
        ratio = stats.progress_ratio
        filled_width = int(self.width * ratio)
        
        # Barra di progresso
        bar = self.fill_char * filled_width + self.empty_char * (self.width - filled_width)
        
        # Aggiungi colori se abilitati
        if self.use_colors:
            if ratio >= 1.0:
                bar = f"{self.colors.get('green', '')}{bar}{self.colors.get('reset', '')}"
            elif ratio >= 0.7:
                bar = f"{self.colors.get('blue', '')}{bar}{self.colors.get('reset', '')}"
            elif stats.failed > 0:
                bar = f"{self.colors.get('yellow', '')}{bar}{self.colors.get('reset', '')}"
        
        # Descrizione
        desc_part = f"{description}: " if description else ""
        
        # Statistiche base
        stats_part = f"{stats.processed}/{stats.total} ({stats.progress_percentage:.1f}%)"
        
        # Statistiche dettagliate
        detail_parts = []
        if self.show_stats and (stats.failed > 0 or stats.skipped > 0):
            detail_parts.append(f"✓{stats.completed}")
            if stats.failed > 0:
                detail_parts.append(f"✗{stats.failed}")
            if stats.skipped > 0:
                detail_parts.append(f"⊘{stats.skipped}")
        
        # Velocità
        rate_part = ""
        if self.show_rate:
            rate_part = f" | {self.format_rate(stats.rate_per_second)}"
        
        # ETA
        eta_part = ""
        if self.show_eta and stats.eta:
            eta_part = f" | ETA: {self.format_time(stats.eta)}"
        
        # Assembla tutto
        detail_str = f" [{', '.join(detail_parts)}]" if detail_parts else ""
        
        return f"{desc_part}{bar} {stats_part}{detail_str}{rate_part}{eta_part}"


class ProgressTracker:
    """Tracker di progresso principale con supporto threading"""
    
    def __init__(self,
                 total: int,
                 description: str = "Processing",
                 update_interval: float = 0.5,
                 auto_display: bool = True,
                 display_config: Optional[Dict[str, Any]] = None):
        """
        Inizializza il tracker di progresso
        
        Args:
            total: Numero totale di elementi da processare
            description: Descrizione dell'operazione
            update_interval: Intervallo di aggiornamento display (secondi)
            auto_display: Se mostrare automaticamente gli aggiornamenti
            display_config: Configurazione per ProgressDisplay
        """
        self.stats = ProgressStats(total=total, completed=0)
        self.description = description
        self.update_interval = update_interval
        self.auto_display = auto_display
        
        # Setup display
        display_config = display_config or {}
        self.display = ProgressDisplay(**display_config)
        
        # Threading per auto-update
        self._stop_event = threading.Event()
        self._display_thread = None
        self._last_display = ""
        
        if auto_display:
            self.start_display()
    
    def start_display(self):
        """Avvia il thread di display automatico"""
        if self._display_thread is None or not self._display_thread.is_alive():
            self._stop_event.clear()
            self._display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self._display_thread.start()
    
    def stop_display(self):
        """Ferma il thread di display automatico"""
        if self._display_thread and self._display_thread.is_alive():
            self._stop_event.set()
            self._display_thread.join(timeout=1)
    
    def _display_loop(self):
        """Loop del thread di display"""
        while not self._stop_event.wait(self.update_interval):
            self._update_display()
    
    def _update_display(self):
        """Aggiorna il display"""
        current_display = self.display.create_bar(self.stats, self.description)
        
        # Solo stampa se cambiato (riduce flickering)
        if current_display != self._last_display:
            # Cancella riga precedente e stampa nuova
            print(f"\r{' ' * len(self._last_display)}\r{current_display}", end='', flush=True)
            self._last_display = current_display
    
    def update(self, 
               completed: int = 0, 
               failed: int = 0, 
               skipped: int = 0,
               force_display: bool = False):
        """
        Aggiorna le statistiche
        
        Args:
            completed: Numero di elementi completati da aggiungere
            failed: Numero di elementi falliti da aggiungere  
            skipped: Numero di elementi saltati da aggiungere
            force_display: Forza aggiornamento display immediato
        """
        self.stats.completed += completed
        self.stats.failed += failed
        self.stats.skipped += skipped
        self.stats.last_update = datetime.now()
        
        if force_display or not self.auto_display:
            self._update_display()
    
    def increment(self, status: str = 'completed'):
        """
        Incrementa un singolo elemento
        
        Args:
            status: 'completed', 'failed', o 'skipped'
        """
        if status == 'completed':
            self.update(completed=1)
        elif status == 'failed':
            self.update(failed=1)
        elif status == 'skipped':
            self.update(skipped=1)
    
    def finish(self, message: Optional[str] = None):
        """
        Completa il tracking e mostra risultato finale
        
        Args:
            message: Messaggio finale opzionale
        """
        self.stop_display()
        
        # Display finale
        final_display = self.display.create_bar(self.stats, self.description)
        print(f"\r{' ' * len(self._last_display)}\r{final_display}")
        
        if message:
            print(f"\n{message}")
        else:
            # Messaggio di default
            elapsed = self.format_elapsed()
            print(f"\nCompletato in {elapsed}")
    
    def format_elapsed(self) -> str:
        """Formatta il tempo trascorso"""
        return self.display.format_time(self.stats.elapsed_time)
    
    def get_summary(self) -> Dict[str, Any]:
        """Ritorna un riassunto delle statistiche"""
        return {
            'total': self.stats.total,
            'completed': self.stats.completed,
            'failed': self.stats.failed,
            'skipped': self.stats.skipped,
            'progress_percentage': self.stats.progress_percentage,
            'elapsed_time': self.stats.elapsed_time.total_seconds(),
            'rate_per_second': self.stats.rate_per_second,
            'eta_seconds': self.stats.eta.total_seconds() if self.stats.eta else None
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.finish()


# Funzioni di convenienza
def create_progress_tracker(total: int, 
                          description: str = "Processing",
                          **kwargs) -> ProgressTracker:
    """Factory function per creare un ProgressTracker"""
    return ProgressTracker(total=total, description=description, **kwargs)


def track_batch_operation(items: list,
                         operation: Callable,
                         description: str = "Processing items",
                         **progress_kwargs) -> Dict[str, Any]:
    """
    Esegue un'operazione batch con tracking automatico
    
    Args:
        items: Lista di elementi da processare
        operation: Funzione che prende un elemento e ritorna ('status', result)
        description: Descrizione dell'operazione
        **progress_kwargs: Parametri per ProgressTracker
    
    Returns:
        Dizionario con risultati e statistiche
    """
    results = {
        'completed': [],
        'failed': [],
        'skipped': []
    }
    
    with create_progress_tracker(len(items), description, **progress_kwargs) as progress:
        for item in items:
            try:
                status, result = operation(item)
                
                if status == 'completed':
                    results['completed'].append(result)
                    progress.increment('completed')
                elif status == 'failed':
                    results['failed'].append(result)
                    progress.increment('failed')
                elif status == 'skipped':
                    results['skipped'].append(result)
                    progress.increment('skipped')
                    
            except Exception as e:
                logger.exception(f"Errore processing item {item}: {e}")
                results['failed'].append({'item': item, 'error': str(e)})
                progress.increment('failed')
    
    # Aggiungi statistiche finali
    results['summary'] = progress.get_summary()
    return results