import os
import warnings
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# ⚠️ Ignorer uniquement le warning de dépréciation de JaegerExporter
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="Call to deprecated method __init__.*Jaeger supports OTLP natively.*"
)

# ---------------- Tracer Provider ----------------
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "simple-banking-api"})
    )
)

tracer = trace.get_tracer(__name__)

# ---------------- Configuration via variables d'environnement ----------------
jaeger_host = os.getenv('JAEGER_HOST', 'localhost')
jaeger_port = os.getenv('JAEGER_PORT', '14268')
jaeger_protocol = os.getenv('JAEGER_PROTOCOL', 'http')
jaeger_username = os.getenv('JAEGER_USERNAME', '')
jaeger_password = os.getenv('JAEGER_PASSWORD', '')

# ---------------- Exporter Jaeger sécurisé ----------------
jaeger_exporter = JaegerExporter(
    # Utiliser les variables d'environnement pour éviter les IPs hardcodées
    collector_endpoint=f"{jaeger_protocol}://{jaeger_host}:{jaeger_port}/api/traces",
    username=jaeger_username,
    password=jaeger_password,
)

# ---------------- Span Processor ----------------
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

print(f"✅ Jaeger tracer setup complete - Endpoint: {jaeger_protocol}://{jaeger_host}:{jaeger_port}")
