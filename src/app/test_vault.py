import os
import hvac

vault_addr = os.getenv("VAULT_ADDR")
role_id = os.getenv("VAULT_ROLE_ID")
secret_id = os.getenv("VAULT_SECRET_ID")

print(f"Connexion à Vault sur {vault_addr} ...")
client = hvac.Client(url=vault_addr)

# ✅ Authentification via AppRole (syntaxe correcte)
resp = client.auth.approle.login(role_id=role_id, secret_id=secret_id)
client.token = resp['auth']['client_token']
print("✅ Authentification réussie !")

# Lire un secret de test
secret = client.secrets.kv.v2.read_secret_version(path="api/config")
print("Secret :", secret["data"]["data"])

