from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from app.oauth_config import oauth

# Kein Prefix, damit die URLs kurz bleiben (/login statt /auth/login)
router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """Leitet den User zur Auth0-Anmeldeseite weiter."""
    # Wir bauen die URL für den Rückweg (Callback)
    redirect_uri = request.url_for('auth_callback')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    """Hier landet der User, wenn er sich bei Auth0 eingeloggt hat."""
    try:
        # 1. Den Token von Auth0 holen
        token = await oauth.auth0.authorize_access_token(request)

        # 2. Die User-Infos aus dem Token lesen
        user_info = token.get('userinfo')

        # 3. Den User in der Browser-Session (Cookie) speichern
        request.session['user'] = user_info

        # Für den Moment geben wir einfach die Infos zurück, damit wir sehen, ob es klappt
        return {"status": "Login erfolgreich!", "user": user_info}
    except Exception as e:
        return {"error": f"Login fehlgeschlagen: {str(e)}"}


@router.get("/logout")
async def logout(request: Request):
    """Loggt den User aus."""
    request.session.pop('user', None)
    return {"message": "Erfolgreich ausgeloggt"}