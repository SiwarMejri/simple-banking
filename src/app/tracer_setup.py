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

# ---------------- Exporter Jaeger sécurisé ----------------
jaeger_exporter = JaegerExporter(
    # Utiliser HTTPS pour chiffrer le trafic
    collector_endpoint="https://192.168.240.143:14268/api/traces",
    username="",       # mettre vos credentials ici
    password="",
)

# ---------------- Span Processor ----------------
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

print("✅ Jaeger tracer setup with HTTPS complete")
