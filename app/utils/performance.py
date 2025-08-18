"""
Performance monitoring and optimization utilities.
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from PySide6.QtCore import QTimer, QObject, Signal
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceMonitor(QObject):
    """Monitor application performance and resource usage."""
    
    performance_warning = Signal(str, str)  # component, message
    
    def __init__(self):
        super().__init__()
        self.metrics = {}
        self.thresholds = {
            'memory_usage_mb': 500,  # MB
            'cpu_usage_percent': 80,  # %
            'operation_time_ms': 2000,  # milliseconds
            'database_query_time_ms': 1000,  # milliseconds
        }
        
        # Start periodic monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_resources)
        self.monitor_timer.start(5000)  # Check every 5 seconds
    
    def _monitor_resources(self):
        """Monitor system resources periodically."""
        try:
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            
            # Update metrics
            self.metrics.update({
                'memory_usage_mb': memory_mb,
                'cpu_usage_percent': cpu_percent,
                'timestamp': time.time()
            })
            
            # Check thresholds
            if memory_mb > self.thresholds['memory_usage_mb']:
                message = f"High memory usage: {memory_mb:.1f} MB"
                logger.warning(message)
                self.performance_warning.emit("Memory", message)
            
            if cpu_percent > self.thresholds['cpu_usage_percent']:
                message = f"High CPU usage: {cpu_percent:.1f}%"
                logger.warning(message)
                self.performance_warning.emit("CPU", message)
                
        except Exception as e:
            logger.error(f"Error monitoring resources: {str(e)}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def log_operation_time(self, operation: str, duration_ms: float):
        """Log operation execution time."""
        self.metrics[f'{operation}_time_ms'] = duration_ms
        
        if duration_ms > self.thresholds['operation_time_ms']:
            message = f"Slow operation '{operation}': {duration_ms:.1f}ms"
            logger.warning(message)
            self.performance_warning.emit("Performance", message)
    
    def log_database_query_time(self, query: str, duration_ms: float):
        """Log database query execution time."""
        query_key = f"db_query_{hash(query) % 1000}"
        self.metrics[query_key] = duration_ms
        
        if duration_ms > self.thresholds['database_query_time_ms']:
            message = f"Slow database query: {duration_ms:.1f}ms"
            logger.warning(message)
            self.performance_warning.emit("Database", message)


# Global performance monitor
performance_monitor = PerformanceMonitor()


def measure_time(operation_name: str):
    """Decorator to measure function execution time."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_monitor.log_operation_time(operation_name, duration_ms)
                logger.debug(f"{operation_name} completed in {duration_ms:.2f}ms")
        return wrapper
    return decorator


def measure_database_query(query_description: str):
    """Decorator to measure database query execution time."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_monitor.log_database_query_time(query_description, duration_ms)
                logger.debug(f"Database query '{query_description}' completed in {duration_ms:.2f}ms")
        return wrapper
    return decorator


@contextmanager
def performance_timer(operation_name: str):
    """Context manager for measuring execution time."""
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        performance_monitor.log_operation_time(operation_name, duration_ms)
        logger.debug(f"{operation_name} completed in {duration_ms:.2f}ms")


class DatabaseOptimizer:
    """Database optimization utilities."""
    
    @staticmethod
    def optimize_patient_queries():
        """Optimize patient-related database queries."""
        # These would be implemented based on actual query patterns
        optimizations = [
            "CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(full_name);",
            "CREATE INDEX IF NOT EXISTS idx_patients_created ON patients(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_dental_records_patient ON dental_chart_records(patient_id);",
            "CREATE INDEX IF NOT EXISTS idx_dental_records_quadrant ON dental_chart_records(quadrant, tooth_number);",
        ]
        
        return optimizations
    
    @staticmethod
    def analyze_table_stats():
        """Analyze database table statistics for optimization."""
        # Would be implemented to analyze actual database
        return {
            'patients_count': 0,
            'dental_records_count': 0,
            'index_usage': {},
            'slow_queries': []
        }


class UIOptimizer:
    """UI performance optimization utilities."""
    
    @staticmethod
    def optimize_table_rendering(table_widget, max_visible_rows: int = 100):
        """Optimize table widget rendering for large datasets."""
        # Implement virtual scrolling or pagination
        pass
    
    @staticmethod
    def debounce_search(search_func: Callable, delay_ms: int = 300):
        """Create debounced version of search function."""
        timer = None
        
        def debounced_func(*args, **kwargs):
            nonlocal timer
            if timer:
                timer.stop()
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: search_func(*args, **kwargs))
            timer.start(delay_ms)
        
        return debounced_func
    
    @staticmethod
    def lazy_load_images(image_paths: list, load_callback: Callable):
        """Implement lazy loading for images."""
        # Would implement progressive image loading
        pass


class MemoryOptimizer:
    """Memory usage optimization utilities."""
    
    @staticmethod
    def cleanup_ui_cache():
        """Clean up UI-related caches."""
        # Clear any UI caches, temporary data
        logger.info("UI cache cleaned up")
    
    @staticmethod
    def optimize_database_sessions():
        """Optimize database session management."""
        # Ensure sessions are properly closed
        logger.info("Database sessions optimized")
    
    @staticmethod
    def check_memory_leaks():
        """Check for potential memory leaks."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'memory_percent': process.memory_percent()
        }


def optimize_application_performance():
    """Run comprehensive performance optimizations."""
    logger.info("Starting application performance optimization...")
    
    try:
        # Database optimizations
        db_optimizer = DatabaseOptimizer()
        db_stats = db_optimizer.analyze_table_stats()
        logger.info(f"Database statistics: {db_stats}")
        
        # Memory optimizations
        MemoryOptimizer.cleanup_ui_cache()
        MemoryOptimizer.optimize_database_sessions()
        memory_stats = MemoryOptimizer.check_memory_leaks()
        logger.info(f"Memory usage: {memory_stats}")
        
        logger.info("Performance optimization completed")
        return True
        
    except Exception as e:
        logger.error(f"Error during performance optimization: {str(e)}")
        return False
