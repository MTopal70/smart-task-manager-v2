import os
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Depends
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.oauth_config import oauth
from app.database import get_db
from app.models.user import User

# Kein Prefix, damit die URLs kurz bleiben (/login statt /auth/login)
router = APIRouter()

@router.get("/register")
async def register(request: Request):
    """Leitet den User direkt zum Auth0 Registrierungs-Formular."""
    redirect_uri = request.url_for('auth_callback')

    # Der Parameter screen_hint='signup' sagt Auth0: "Zeig sofort das Registrier-Feld!"
    return await oauth.auth0.authorize_redirect(
        request,
        redirect_uri,
        screen_hint='signup'
    )
@router.get("/login")
async def login(request: Request):
    """Leitet den User zur Auth0-Anmeldeseite weiter."""
    # Wir bauen die URL für den Rückweg (Callback)
    redirect_uri = request.url_for('auth_callback')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):  # <--- DB injected
    try:
        # 1. Daten von Auth0 holen
        token = await oauth.auth0.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            print("❌ Auth0 hat keine User-Info zurückgegeben.")
            return RedirectResponse(url="/")

        # In Session speichern (für den Browser)
        request.session['user'] = dict(user_info)

        # 2. WICHTIG: User in die Datenbank synchronisieren 💾
        email = user_info.get('email')

        # User suchen
        db_user = db.query(User).filter(User.email == email).first()

        if not db_user:
            print(f"🆕 Lege neuen User an: {email}")

            # Username generieren: Falls Nickname fehlt, nimm den Teil vor dem @ der Email
            fallback_name = email.split("@")[0]
            nickname = user_info.get('nickname', fallback_name)

            new_user = User(
                email=email,
                username=nickname,
                # Da Login via Auth0 läuft, setzen wir ein Dummy-Passwort
                hashed_password="AUTH0_EXTERNAL_LOGIN"
            )

            try:
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                print(f"✅ User {email} erfolgreich in DB gespeichert (ID: {new_user.id})")
            except Exception as db_err:
                print(f"❌ Datenbank-Fehler beim Anlegen: {db_err}")
                db.rollback()
                # Wir lassen den User trotzdem rein (Session ist ja da),
                # aber er hat dann keine DB-ID für Tasks.
        else:
            print(f"👋 Willkommen zurück, {email} (ID: {db_user.id})")

        # 3. Weiter zum Dashboard
        return RedirectResponse(url="/")

    except Exception as e:
        print(f"❌ Schwerer Fehler im Callback: {e}")
        # Bei Fehler zurück zum Login oder Home
        return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    """Loggt den User aus."""
    # 1. clear session
    request.session.clear()

    # 2. Auth0 Logout URL bauen
    # Wir brauchen die Domain und Client ID aus den Umgebungsvariablen
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")

    # Wohin soll Auth0 uns nach dem Logout schicken?
    return_to = "http://localhost:8000"  # Muss im Dashboard bei "Allowed Logout URLs" stehen!

    # URL Parameter zusammenbauen
    params = {
        "returnTo": return_to,
        "client_id": client_id
    }

    # Die Logout-URL sieht dann so aus: https://dev-xyz.../v2/logout?client_id=...&returnTo=...
    logout_url = f"https://{domain}/v2/logout?{urlencode(params)}"

    # 3. Den User zu Auth0 schicken
    return RedirectResponse(url=logout_url, status_code=303)

