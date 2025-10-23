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
# Utiliser une variable unique pour l'endpoint complet
jaeger_endpoint = os.getenv('JAEGER_COLLECTOR_ENDPOINT', 'https://192.168.240.143:14268/api/traces')

# ---------------- Exporter Jaeger sécurisé ----------------
jaeger_exporter = JaegerExporter(
    # Utiliser les variables d'environnement pour éviter les IPs hardcodées
    collector_endpoint=jaeger_endpoint,
    username=os.getenv('JAEGER_USER', ''),        # Chaîne vide si pas d'authentification
    password=os.getenv('JAEGER_PASSWORD', ''),    # Chaîne vide si pas d'authentification
)

# ---------------- Span Processor ----------------
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

print(f"✅ Jaeger tracer setup complete - Endpoint: {jaeger_endpoint}")
