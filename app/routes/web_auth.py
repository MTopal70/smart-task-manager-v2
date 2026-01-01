from fastapi import APIRouter, Request, Depends
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.oauth_config import oauth
from app.database import get_db
from app.models.user import User

# Kein Prefix, damit die URLs kurz bleiben (/login statt /auth/login)
router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """Leitet den User zur Auth0-Anmeldeseite weiter."""
    # Wir bauen die URL für den Rückweg (Callback)
    redirect_uri = request.url_for('auth_callback')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

# Callback Route aktualisiert:
@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):  # <--- DB injected
    try:
        # 1. Daten von Auth0 holen
        token = await oauth.auth0.authorize_access_token(request)
        user_info = token.get('userinfo')

        # In Session speichern (für den Browser)
        request.session['user'] = user_info

        # 2. WICHTIG: User in die Datenbank synchronisieren 💾
        email = user_info.get('email')
        db_user = db.query(User).filter(User.email == email).first()

        if not db_user:
            # User existiert noch nicht -> neu anlegen!
            print(f"Lege neuen User an: {email}")
            new_user = User(
                email=email,
                # Wir nehmen den Nickname von Auth0 als Username
                username=user_info.get('nickname', 'NewUser'),
                # Da Login via Auth0 läuft, setzen wir ein Dummy-Passwort
                hashed_password="AUTH0_EXTERNAL_LOGIN"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        # 3. Weiter zum Dashboard
        return RedirectResponse(url="/")

    except Exception as e:
        return {"error": f"Login fehlgeschlagen: {str(e)}"}

@router.get("/logout")
async def logout(request: Request):
    """Loggt den User aus."""
    request.session.pop('user', None)
    return {"message": "Erfolgreich ausgeloggt"}