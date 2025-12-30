from authlib.integrations.starlette_client import OAuth
from app.config import settings

# Wir erstellen ein OAuth-Objekt
oauth = OAuth()

# Wir registrieren Auth0 als unseren Anbieter
oauth.register(
    name='auth0',
    client_id=settings.auth0_client_id,
    client_secret=settings.auth0_client_secret,
    # Diese URL ist wichtig: Hier holt sich die App alle Infos von Auth0 automatisch
    server_metadata_url=f'https://{settings.auth0_domain}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email'
    }
)