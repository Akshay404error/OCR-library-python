"""
Enterprise monitoring and analytics
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

try:
    import prometheus_client as prometheus
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

from .config import EnterpriseConfig, LogLevel


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    operation: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UsageMetric:
    """Usage tracking metric"""
    user_id: str
    operation: str
    resource_type: str
    resource_size: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PerformanceMonitor:
    """Enterprise performance monitoring"""
    
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # In-memory metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics: deque = deque(maxlen=10000)
        self.usage_metrics: deque = deque(maxlen=10000)
        
        # Prometheus metrics (if available)
        self.prometheus_metrics = {}
        self._init_prometheus()
        
        # OpenTelemetry (if available)
        self.tracer = None
        self.meter = None
        self._init_opentelemetry()
        
        # Background thread for metric aggregation
        self._start_background_tasks()
    
    def _init_prometheus(self):
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE or not self.config.monitoring.enable_metrics:
            return
        
        # Create Prometheus metrics
        self.prometheus_metrics = {
            'ocr_requests_total': prometheus.Counter(
                'matocr8d_ocr_requests_total',
                'Total OCR requests',
                ['engine', 'status', 'user_id']
            ),
            'ocr_duration_seconds': prometheus.Histogram(
                'matocr8d_ocr_duration_seconds',
                'OCR processing duration',
                ['engine', 'operation'],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
            ),
            'active_connections': prometheus.Gauge(
                'matocr8d_active_connections',
                'Active API connections'
            ),
            'file_size_bytes': prometheus.Histogram(
                'matocr8d_file_size_bytes',
                'Processed file sizes',
                buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800]
            ),
            'api_errors_total': prometheus.Counter(
                'matocr8d_api_errors_total',
                'Total API errors',
                ['error_type', 'endpoint']
            )
        }
    
    def _init_opentelemetry(self):
        """Initialize OpenTelemetry tracing"""
        if not OPENTELEMETRY_AVAILABLE or not self.config.monitoring.enable_tracing:
            return
        
        # Set up tracing
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        if self.config.monitoring.tracing_backend == "jaeger":
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(__name__)
        
        # Set up metrics
        metrics.set_meter_provider(MeterProvider())
        self.meter = metrics.get_meter(__name__)
    
    def _start_background_tasks(self):
        """Start background metric collection tasks"""
        if not self.config.monitoring.enable_metrics:
            return
        
        def aggregate_metrics():
            """Background task to aggregate metrics"""
            while True:
                try:
                    self._aggregate_performance_metrics()
                    self._cleanup_old_metrics()
                    time.sleep(60)  # Run every minute
                except Exception as e:
                    self.logger.error(f"Error in metric aggregation: {e}")
        
        thread = threading.Thread(target=aggregate_metrics, daemon=True)
        thread.start()
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric"""
        if labels is None:
            labels = {}
        
        metric = Metric(name=name, value=value, labels=labels)
        self.metrics[name].append(metric)
        
        # Update Prometheus if available
        if name in self.prometheus_metrics:
            prom_metric = self.prometheus_metrics[name]
            if isinstance(prom_metric, prometheus.Counter):
                prom_metric.inc()
            elif isinstance(prom_metric, prometheus.Gauge):
                prom_metric.set(value)
            elif isinstance(prom_metric, prometheus.Histogram):
                prom_metric.observe(value)
    
    def record_performance(self, operation: str, duration_ms: float, 
                          success: bool = True, error_message: str = None,
                          user_id: str = None, api_key: str = None):
        """Record performance metric"""
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            user_id=user_id,
            api_key=api_key
        )
        self.performance_metrics.append(metric)
        
        # Update Prometheus
        if 'ocr_duration_seconds' in self.prometheus_metrics:
            self.prometheus_metrics['ocr_duration_seconds'].observe(
                duration_ms / 1000.0, labels={'operation': operation}
            )
        
        # Update request counter
        if 'ocr_requests_total' in self.prometheus_metrics:
            status = 'success' if success else 'error'
            self.prometheus_metrics['ocr_requests_total'].inc(
                labels={'engine': operation, 'status': status, 'user_id': user_id or 'anonymous'}
            )
    
    def record_usage(self, user_id: str, operation: str, 
                    resource_type: str, resource_size: int):
        """Record usage metric"""
        metric = UsageMetric(
            user_id=user_id,
            operation=operation,
            resource_type=resource_type,
            resource_size=resource_size
        )
        self.usage_metrics.append(metric)
        
        # Update Prometheus
        if 'file_size_bytes' in self.prometheus_metrics:
            self.prometheus_metrics['file_size_bytes'].observe(resource_size)
    
    def record_error(self, error_type: str, endpoint: str, error_message: str = None):
        """Record API error"""
        if 'api_errors_total' in self.prometheus_metrics:
            self.prometheus_metrics['api_errors_total'].inc(
                labels={'error_type': error_type, 'endpoint': endpoint}
            )
        
        self.logger.error(f"API Error [{error_type}] at {endpoint}: {error_message}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_performance = [
            m for m in self.performance_metrics 
            if m.timestamp > cutoff_time
        ]
        recent_usage = [
            m for m in self.usage_metrics 
            if m.timestamp > cutoff_time
        ]
        
        # Calculate aggregates
        total_requests = len(recent_performance)
        successful_requests = len([m for m in recent_performance if m.success])
        error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 0
        
        avg_duration = 0
        if recent_performance:
            total_duration = sum(m.duration_ms for m in recent_performance)
            avg_duration = total_duration / len(recent_performance)
        
        # Usage by user
        usage_by_user = defaultdict(int)
        for usage in recent_usage:
            usage_by_user[usage.user_id] += usage.resource_size
        
        return {
            'timeframe_hours': hours,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'error_rate': error_rate,
            'average_duration_ms': avg_duration,
            'unique_users': len(usage_by_user),
            'total_data_processed_mb': sum(usage_by_user.values()) / (1024 * 1024),
            'top_users': dict(sorted(usage_by_user.items(), 
                                   key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _aggregate_performance_metrics(self):
        """Aggregate performance metrics"""
        # This would typically store aggregated metrics in a time-series database
        pass
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.monitoring.retention_days)
        
        # Clean performance metrics
        self.performance_metrics = deque(
            [m for m in self.performance_metrics if m.timestamp > cutoff_date],
            maxlen=10000
        )
        
        # Clean usage metrics
        self.usage_metrics = deque(
            [m for m in self.usage_metrics if m.timestamp > cutoff_date],
            maxlen=10000
        )
    
    def create_span(self, operation_name: str) -> Optional[Any]:
        """Create OpenTelemetry span"""
        if self.tracer:
            return self.tracer.start_as_current_span(operation_name)
        return None
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics for scraping"""
        if PROMETHEUS_AVAILABLE:
            return prometheus.generate_latest()
        return ""


class UsageTracker:
    """Enterprise usage tracking and billing"""
    
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Usage storage (replace with database in production)
        self.usage_records: Dict[str, List[UsageMetric]] = defaultdict(list)
        self.quota_limits: Dict[str, Dict[str, int]] = {}
        self.current_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def set_quota_limit(self, user_id: str, resource_type: str, limit: int):
        """Set quota limit for user"""
        if user_id not in self.quota_limits:
            self.quota_limits[user_id] = {}
        self.quota_limits[user_id][resource_type] = limit
    
    def check_quota(self, user_id: str, resource_type: str, amount: int = 1) -> bool:
        """Check if user has quota remaining"""
        if user_id not in self.quota_limits:
            return True  # No quota set
        
        if resource_type not in self.quota_limits[user_id]:
            return True  # No quota for this resource type
        
        limit = self.quota_limits[user_id][resource_type]
        current = self.current_usage[user_id][resource_type]
        
        return (current + amount) <= limit
    
    def record_usage(self, user_id: str, operation: str, 
                    resource_type: str, resource_size: int):
        """Record usage against quota"""
        metric = UsageMetric(
            user_id=user_id,
            operation=operation,
            resource_type=resource_type,
            resource_size=resource_size
        )
        
        self.usage_records[user_id].append(metric)
        self.current_usage[user_id][resource_type] += resource_size
    
    def get_usage_report(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage report for user"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        user_metrics = [
            m for m in self.usage_records[user_id] 
            if m.timestamp > cutoff_date
        ]
        
        # Aggregate by operation and resource type
        usage_by_operation = defaultdict(int)
        usage_by_resource = defaultdict(int)
        total_data = 0
        
        for metric in user_metrics:
            usage_by_operation[metric.operation] += 1
            usage_by_resource[metric.resource_type] += metric.resource_size
            total_data += metric.resource_size
        
        # Get quota information
        quota_info = self.quota_limits.get(user_id, {})
        current_quota = self.current_usage.get(user_id, {})
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_operations': len(user_metrics),
            'total_data_processed_mb': total_data / (1024 * 1024),
            'usage_by_operation': dict(usage_by_operation),
            'usage_by_resource_type': {
                k: v / (1024 * 1024) for k, v in usage_by_resource.items()
            },
            'quota_limits': quota_info,
            'current_usage': {
                k: v / (1024 * 1024) for k, v in current_quota.items()
            }
        }
    
    def reset_usage_period(self, user_id: str = None):
        """Reset usage for user or all users"""
        if user_id:
            self.current_usage[user_id].clear()
        else:
            self.current_usage.clear()
