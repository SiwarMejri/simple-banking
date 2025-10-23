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
jaeger_endpoint = os.getenv('JAEGER_COLLECTOR_ENDPOINT')

if not jaeger_endpoint:
    print("⚠️  JAEGER_COLLECTOR_ENDPOINT non défini - Jaeger tracing désactivé")
    jaeger_exporter = None
else:
    print(f"✅ Configuration Jaeger: {jaeger_endpoint}")
    
    # ---------------- Exporter Jaeger sécurisé ----------------
    jaeger_exporter = JaegerExporter(
        collector_endpoint=jaeger_endpoint,
        username=os.getenv('JAEGER_USER', ''),
        password=os.getenv('JAEGER_PASSWORD', ''),
    )

    # ---------------- Span Processor ----------------
    if jaeger_exporter:
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        print("✅ Jaeger tracer setup complete")
