#!/bin/bash

# === CONFIGURATION ===
KEYCLOAK_URL="http://192.168.240.143:8080"
REALM="simple-banking-realm"
CLIENT_ID="api-rest-client"
CLIENT_SECRET="${KEYCLOAK_CLIENT_SECRET}"   # récupéré depuis Vault ou exporté dans l'env
SCOPE="api-access"
API_URL="http://0.0.0.0:8000/protected"

# === Vérification des prérequis ===
if [ -z "$CLIENT_SECRET" ]; then
  echo "❌ La variable d'environnement KEYCLOAK_CLIENT_SECRET n'est pas définie."
  echo "   Utilise : export KEYCLOAK_CLIENT_SECRET='ton_secret' avant d'exécuter ce script."
  exit 1
fi

echo "🔑 Récupération du token auprès de Keycloak..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/$REALM/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "scope=$SCOPE" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Impossible d'obtenir le token ! Vérifie Keycloak, client_id ou client_secret."
  exit 1
fi

echo "✅ Token obtenu avec succès."
echo "🚀 Test de l'endpoint protégé..."

RESPONSE=$(curl -s -X GET "$API_URL" \
  -H "Authorization: Bearer $TOKEN")

echo "📡 Réponse de l'API :"
echo "$RESPONSE"

