from tracer_setup import tracer
import time

def main():
    print("Création d'un span de test vers Jaeger...")
    with tracer.start_as_current_span("test_span"):
        print("Span 'test_span' en cours...")
        time.sleep(2)  # simule une opération
    print("Span terminé ✅")

if __name__ == "__main__":
    main()
