import logging
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from opentelemetry._logs import set_logger_provider, get_logger_provider
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider, get_tracer_provider


class AzureMonitor:
    """
    Class to configure Azure Moniter telemetry with OpenTelemetry.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize the Application Insights configurator.
        
        Args:
            connection_string (str): The connection string for Application Insights resource.
        """
        self.connection_string = connection_string
        self.logger = logging.getLogger(__name__)
        self.resource = Resource.create({ResourceAttributes.SERVICE_NAME: "mypetparlor_ai_assistant_chainlit_app"})
        self.logger.info("ApplicationInsightsConfigurator initialized")
    
    def set_up_logging(self):
        """Set up logging with Azure Monitor."""
        self.logger.info("Setting up logging")
        exporter = AzureMonitorLogExporter(connection_string=self.connection_string)

        # Create and set a global logger provider for the application.
        logger_provider = get_logger_provider() or LoggerProvider(resource=self.resource)
        # Log processors are initialized with an exporter which is responsible
        # for sending the telemetry data to a particular backend.
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        # Sets the global default logger provider
        set_logger_provider(logger_provider)

        # Create a logging handler to write logging records, in OTLP format, to the exporter.
        handler = LoggingHandler()
        # Add filters to the handler to only process records from semantic_kernel.
        handler.addFilter(logging.Filter("semantic_kernel"))
        # Attach the handler to the root logger. `getLogger()` with no arguments returns the root logger.
        # Events from all child loggers will be processed by this handler.
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def set_up_tracing(self):
        """Set up tracing with Azure Monitor."""
        self.logger.info("Setting up tracing")
        exporter = AzureMonitorTraceExporter(connection_string=self.connection_string)

        # Initialize a trace provider for the application. This is a factory for creating tracers.
        tracer_provider = get_tracer_provider() or TracerProvider(resource=self.resource)
        # Span processors are initialized with an exporter which is responsible
        # for sending the telemetry data to a particular backend.
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        # Sets the global default tracer provider
        set_tracer_provider(tracer_provider)

    def set_up_metrics(self):
        """Set up metrics with Azure Monitor."""
        self.logger.info("Setting up metrics")
        exporter = AzureMonitorMetricExporter(connection_string=self.connection_string)

        # Initialize a metric provider for the application. This is a factory for creating meters.
        meter_provider = get_meter_provider() or MeterProvider(
            metric_readers=[PeriodicExportingMetricReader(exporter, export_interval_millis=5000)],
            resource=self.resource,
            views=[
                # Dropping all instrument names except for those starting with "semantic_kernel"
                View(instrument_name="*", aggregation=DropAggregation()),
                View(instrument_name="semantic_kernel*"),
            ],
        )
        # Sets the global default meter provider
        set_meter_provider(meter_provider)

    def configure(self):
        """
        Configure Application Insights by setting up logging, tracing, and metrics.
        """
        self.logger.info("Configuring Application Insights")
        self.set_up_logging()
        self.set_up_tracing()
        self.set_up_metrics()
        self.logger.info("Application Insights configuration complete")


def configure_application_insights(connection_string: str):
    """
    Configure Application Insights by setting up logging, tracing, and metrics.

    Args:
        connection_string (str): The connection string for Application Insights resource.
    """
    configurator = AzureMonitor(connection_string)
    configurator.configure()
