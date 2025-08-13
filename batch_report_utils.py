import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class BatchStatus(Enum):
    """Enum per gli stati dei batch"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class BatchResult:
    """Classe per rappresentare un risultato di batch"""
    name: str
    status: BatchStatus
    start_time: datetime
    end_time: datetime
    duration: timedelta
    success_count: int = 0
    failed_count: int = 0
    partial_count: int = 0
    total_count: int = 0
    success_items: List[Dict[str, Any]] = None
    failed_items: List[Dict[str, Any]] = None
    partial_items: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    error_messages: List[str] = None
    
    def __post_init__(self):
        if self.success_items is None:
            self.success_items = []
        if self.failed_items is None:
            self.failed_items = []
        if self.partial_items is None:
            self.partial_items = []
        if self.metadata is None:
            self.metadata = {}
        if self.error_messages is None:
            self.error_messages = []
        
        # Calcola i totali se non specificati
        if self.total_count == 0:
            self.total_count = len(self.success_items) + len(self.failed_items) + len(self.partial_items)
        if self.success_count == 0:
            self.success_count = len(self.success_items)
        if self.failed_count == 0:
            self.failed_count = len(self.failed_items)
        if self.partial_count == 0:
            self.partial_count = len(self.partial_items)

class BatchReportGenerator:
    """Generatore di report per batch con supporto per success, failed e partial success"""
    
    def __init__(self, output_dir: str = "batch_reports"):
        """
        Inizializza il generatore di report
        
        Args:
            output_dir: Directory dove salvare i report
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_batch_result(self, 
                          name: str,
                          start_time: datetime,
                          end_time: datetime,
                          success_items: List[Dict[str, Any]] = None,
                          failed_items: List[Dict[str, Any]] = None,
                          partial_items: List[Dict[str, Any]] = None,
                          metadata: Dict[str, Any] = None,
                          error_messages: List[str] = None) -> BatchResult:
        """
        Crea un risultato di batch
        
        Args:
            name: Nome del batch
            start_time: Ora di inizio
            end_time: Ora di fine
            success_items: Lista degli elementi processati con successo
            failed_items: Lista degli elementi falliti
            partial_items: Lista degli elementi con successo parziale
            metadata: Metadati aggiuntivi
            error_messages: Messaggi di errore
            
        Returns:
            BatchResult: Risultato del batch
        """
        duration = end_time - start_time
        
        # Determina lo status del batch
        if failed_items and len(failed_items) > 0:
            if success_items and len(success_items) > 0:
                status = BatchStatus.PARTIAL
            else:
                status = BatchStatus.FAILED
        else:
            status = BatchStatus.SUCCESS
        
        return BatchResult(
            name=name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success_items=success_items or [],
            failed_items=failed_items or [],
            partial_items=partial_items or [],
            metadata=metadata or {},
            error_messages=error_messages or []
        )
    
    def generate_text_report(self, batch_result: BatchResult, include_details: bool = True) -> str:
        """
        Genera un report testuale del batch
        
        Args:
            batch_result: Risultato del batch
            include_details: Se includere i dettagli degli elementi
            
        Returns:
            str: Report testuale
        """
        report_lines = []
        
        # Header
        report_lines.append(f"REPORT BATCH: {batch_result.name.upper()}")
        report_lines.append("=" * 60)
        report_lines.append(f"Data/Ora: {batch_result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Stato: {batch_result.status.value.upper()}")
        report_lines.append(f"Durata: {self._format_duration(batch_result.duration)}")
        report_lines.append(f"Ora inizio: {batch_result.start_time.strftime('%H:%M:%S')}")
        report_lines.append(f"Ora fine: {batch_result.end_time.strftime('%H:%M:%S')}")
        
        # Statistiche
        report_lines.append("")
        report_lines.append("STATISTICHE:")
        report_lines.append("-" * 20)
        report_lines.append(f"Totale elementi: {batch_result.total_count}")
        report_lines.append(f"Successi: {batch_result.success_count}")
        report_lines.append(f"Fallimenti: {batch_result.failed_count}")
        report_lines.append(f"Parziali: {batch_result.partial_count}")
        
        if batch_result.total_count > 0:
            success_rate = (batch_result.success_count / batch_result.total_count) * 100
            report_lines.append(f"Tasso di successo: {success_rate:.1f}%")
        
        # Metadati
        if batch_result.metadata:
            report_lines.append("")
            report_lines.append("METADATI:")
            report_lines.append("-" * 20)
            for key, value in batch_result.metadata.items():
                report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # Errori
        if batch_result.error_messages:
            report_lines.append("")
            report_lines.append("ERRORI:")
            report_lines.append("-" * 20)
            for error in batch_result.error_messages:
                report_lines.append(f"- {error}")
        
        # Dettagli per categoria
        if include_details:
            self._add_category_details(report_lines, "SUCCESSI", batch_result.success_items)
            self._add_category_details(report_lines, "FALLIMENTI", batch_result.failed_items)
            self._add_category_details(report_lines, "PARZIALI", batch_result.partial_items)
        
        return "\n".join(report_lines)
    
    def _add_category_details(self, report_lines: List[str], category_name: str, items: List[Dict[str, Any]]):
        """Aggiunge i dettagli di una categoria al report"""
        if not items:
            return
            
        report_lines.append("")
        report_lines.append(f"DETTAGLI {category_name} ({len(items)} elementi):")
        report_lines.append("-" * 40)
        
        for i, item in enumerate(items[:10], 1):  # Primi 10 elementi
            if isinstance(item, dict):
                # Cerca campi comuni per la visualizzazione
                display_text = self._get_item_display_text(item)
                report_lines.append(f"{i}. {display_text}")
            else:
                report_lines.append(f"{i}. {str(item)}")
        
        if len(items) > 10:
            report_lines.append(f"... e altri {len(items) - 10} elementi")
    
    def _get_item_display_text(self, item: Dict[str, Any]) -> str:
        """Estrae un testo di visualizzazione da un elemento"""
        # Cerca campi comuni per la visualizzazione
        for field in ['title', 'name', 'file', 'id', 'message']:
            if field in item:
                return str(item[field])
        
        # Se non trova campi comuni, usa i primi valori
        if item:
            first_key = list(item.keys())[0]
            return f"{first_key}: {item[first_key]}"
        
        return str(item)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Formatta una durata in modo leggibile"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def save_report(self, batch_result: BatchResult, 
                   save_text: bool = True, 
                   save_json: bool = True,
                   include_details: bool = True) -> Dict[str, str]:
        """
        Salva il report del batch
        
        Args:
            batch_result: Risultato del batch
            save_text: Se salvare il report testuale
            save_json: Se salvare il report JSON
            include_details: Se includere i dettagli nel report testuale
            
        Returns:
            Dict[str, str]: Percorsi dei file salvati
        """
        timestamp = batch_result.end_time.strftime("%Y%m%d_%H%M%S")
        base_filename = f"{batch_result.name}_{timestamp}"
        saved_files = {}
        
        # Report testuale
        if save_text:
            text_filename = f"{base_filename}_report.txt"
            text_path = os.path.join(self.output_dir, text_filename)
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_text_report(batch_result, include_details))
            
            saved_files['text'] = text_path
            self.logger.info(f"Report testuale salvato: {text_path}")
        
        # Report JSON
        if save_json:
            json_filename = f"{base_filename}_detailed.json"
            json_path = os.path.join(self.output_dir, json_filename)
            
            # Converti il BatchResult in dizionario
            report_data = {
                'batch_info': {
                    'name': batch_result.name,
                    'status': batch_result.status.value,
                    'start_time': batch_result.start_time.isoformat(),
                    'end_time': batch_result.end_time.isoformat(),
                    'duration_seconds': batch_result.duration.total_seconds(),
                    'duration_formatted': self._format_duration(batch_result.duration)
                },
                'statistics': {
                    'total_count': batch_result.total_count,
                    'success_count': batch_result.success_count,
                    'failed_count': batch_result.failed_count,
                    'partial_count': batch_result.partial_count,
                    'success_rate': (batch_result.success_count / batch_result.total_count * 100) if batch_result.total_count > 0 else 0
                },
                'metadata': batch_result.metadata,
                'error_messages': batch_result.error_messages,
                'results': {
                    'success_items': batch_result.success_items,
                    'failed_items': batch_result.failed_items,
                    'partial_items': batch_result.partial_items
                }
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            saved_files['json'] = json_path
            self.logger.info(f"Report JSON salvato: {json_path}")
        
        return saved_files
    
    def print_summary(self, batch_result: BatchResult):
        """Stampa un riassunto del batch sulla console"""
        print("\n" + "=" * 60)
        print(f"BATCH COMPLETATO: {batch_result.name.upper()}")
        print("=" * 60)
        print(f"Stato: {batch_result.status.value.upper()}")
        print(f"Durata: {self._format_duration(batch_result.duration)}")
        print(f"Totale: {batch_result.total_count} | Successi: {batch_result.success_count} | Fallimenti: {batch_result.failed_count} | Parziali: {batch_result.partial_count}")
        
        if batch_result.total_count > 0:
            success_rate = (batch_result.success_count / batch_result.total_count) * 100
            print(f"Tasso di successo: {success_rate:.1f}%")
        
        if batch_result.error_messages:
            print(f"Errori: {len(batch_result.error_messages)}")
        
        print("=" * 60)

# Funzioni di utilità per facilitare l'uso
def create_batch_context(name: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Crea un contesto per un batch
    
    Args:
        name: Nome del batch
        metadata: Metadati aggiuntivi
        
    Returns:
        Dict con il contesto del batch
    """
    return {
        'name': name,
        'start_time': datetime.now(),
        'metadata': metadata or {},
        'success_items': [],
        'failed_items': [],
        'partial_items': [],
        'error_messages': []
    }

def add_success_item(context: Dict[str, Any], item: Dict[str, Any]):
    """Aggiunge un elemento di successo al contesto del batch"""
    context['success_items'].append(item)

def add_failed_item(context: Dict[str, Any], item: Dict[str, Any], error_message: str = None):
    """Aggiunge un elemento fallito al contesto del batch"""
    if error_message:
        item['error'] = error_message
    context['failed_items'].append(item)
    if error_message:
        context['error_messages'].append(error_message)

def add_partial_item(context: Dict[str, Any], item: Dict[str, Any], partial_reason: str = None):
    """Aggiunge un elemento con successo parziale al contesto del batch"""
    if partial_reason:
        item['partial_reason'] = partial_reason
    context['partial_items'].append(item)

def finalize_batch(context: Dict[str, Any], 
                  output_dir: str = "batch_reports",
                  save_text: bool = True,
                  save_json: bool = True,
                  print_summary: bool = True) -> BatchResult:
    """
    Finalizza un batch e genera il report
    
    Args:
        context: Contesto del batch
        output_dir: Directory per i report
        save_text: Se salvare il report testuale
        save_json: Se salvare il report JSON
        print_summary: Se stampare il riassunto
        
    Returns:
        BatchResult: Risultato del batch
    """
    end_time = datetime.now()
    
    generator = BatchReportGenerator(output_dir)
    batch_result = generator.create_batch_result(
        name=context['name'],
        start_time=context['start_time'],
        end_time=end_time,
        success_items=context['success_items'],
        failed_items=context['failed_items'],
        partial_items=context['partial_items'],
        metadata=context['metadata'],
        error_messages=context['error_messages']
    )
    
    # Salva i report
    generator.save_report(batch_result, save_text, save_json)
    
    # Stampa il riassunto
    if print_summary:
        generator.print_summary(batch_result)
    
    return batch_result 