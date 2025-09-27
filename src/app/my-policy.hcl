# my-policy.hcl
path "secret/data/api/config" {
  capabilities = ["read"]
}

path "secret/data/keycloak" {
  capabilities = ["read"]
}

