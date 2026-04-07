#!/usr/bin/env python3
"""
Gera refresh token OAuth2 com escopos combinados (Google Ads + GA4).
Uso: python3 generate_token.py --client-id XXX --client-secret XXX
"""
import argparse
import json
import ssl
import sys
import urllib.parse
import urllib.request
import urllib.error

# Fix SSL certificate verification on macOS with Python 3.13+
_ssl_ctx = ssl.create_default_context()
try:
    import certifi
    _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/analytics.readonly",
]

REDIRECT_URI = "http://localhost:8844"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    args = parser.parse_args()

    # Step 1: Build auth URL
    params = {
        "client_id": args.client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    print("\n=== Gerar Token OAuth2 (Google Ads + GA4) ===\n")
    print("1. Abre esta URL no navegador:\n")
    print(auth_url)
    print("\n2. Faz login e autoriza.")
    print("3. Cole aqui o CODIGO que aparece na URL de redirect (parametro 'code=...'):\n")

    code = input("Codigo: ").strip()

    # Step 2: Exchange code for tokens
    token_data = urllib.parse.urlencode({
        "code": code,
        "client_id": args.client_id,
        "client_secret": args.client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urllib.request.urlopen(req, context=_ssl_ctx) as resp:
            result = json.loads(resp.read())
        print("\n=== TOKEN GERADO COM SUCESSO ===\n")
        print(f"REFRESH_TOKEN={result['refresh_token']}")
        print(f"\nEscopos: {', '.join(SCOPES)}")
        print("\nAtualize o .env do google-ads-ratos e do ga4-ratos com esse refresh token.")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"\nERRO {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
