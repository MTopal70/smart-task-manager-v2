from app.database import engine
# WICHTIG: Base holen wir direkt aus models.base, nicht aus database
from app.models.base import Base
from app.models.project import Project
from app.models.task import Task

print("🧹 DB-Reset (Profi-Version)...")

try:
    # Erst Tasks (Kind), dann Projekte (Eltern) löschen
    Task.__table__.drop(engine)
    print("✅ Tasks gelöscht.")
    Project.__table__.drop(engine)
    print("✅ Projekte gelöscht.")
except Exception as e:
    print(f"Info (Löschen): {e}")

print("✨ Erstelle Tabellen neu...")
# Das erstellt alle Tabellen basierend auf den importierten Models
Base.metadata.create_all(bind=engine)
print("Fertig! 🚀")
