import warnings
# Ignorer uniquement le warning de dépréciation de JaegerExporter
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="Call to deprecated method __init__.*Jaeger supports OTLP natively.*"
)

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "simple-banking-api"})
    )
)

tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    collector_endpoint="http://192.168.240.143:14268/api/traces",
    username="",
    password="",
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

