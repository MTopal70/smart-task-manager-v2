# unit test

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Importiere deine Modelle (pass den Punkt . ggf. an, falls nötig)
# Wenn die Datei im selben Ordner liegt, entferne den Punkt vor 'base' in deinen Models temporär
# oder sorge dafür, dass es als Package läuft.
# Für diesen Test gehen wir davon aus, dass alles importierbar ist.
from base import Base
from user import User
from project import Project
from task import Task

# 1. SETUP: Die "Wegwerf-Datenbank" im Arbeitsspeicher
# sqlite:///:memory: bedeutet: Es wird keine Datei auf der Festplatte erstellt!
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=False)  # echo=False macht die Konsole ruhiger

# Tabellen erstellen
Base.metadata.create_all(bind=engine)

# Session erstellen
Session = sessionmaker(bind=engine)
session = Session()


def test_create_full_workflow():
    print("--- Start Test: Full Workflow ---")

    # A. User erstellen
    new_user = User(
        username="TestUser",
        email="test@example.com",
        hashed_password="fakehash123"
    )
    session.add(new_user)
    session.commit()  # Wichtig: Erst jetzt bekommt der User eine ID

    print(f"1. User erstellt: ID={new_user.id}, Name={new_user.username}")

    # B. Projekt erstellen (gehört dem User)
    new_project = Project(
        name="Python Lernen",
        description="Alles über Backend Development",
        owner_id=new_user.id
    )
    session.add(new_project)
    session.commit()

    print(f"2. Projekt erstellt: ID={new_project.id}, OwnerID={new_project.owner_id}")

    # C. Task erstellen (gehört User UND Projekt)
    new_task = Task(
        title="Unit Tests schreiben",
        description="Lerne wie man mit pytest testet",
        priority="High",
        owner_id=new_user.id,
        project_id=new_project.id
    )
    session.add(new_task)
    session.commit()

    print(f"3. Task erstellt: ID={new_task.id}, ProjektID={new_task.project_id}")

    # D. DER GROSSE CHECK (Assertions)
    # Wir laden den User frisch aus der DB und schauen, ob SQLAlchemy die Verknüpfungen kennt
    # refresh lädt die Daten neu
    session.refresh(new_user)

    # Test 1: Hat der User Zugriff auf sein Projekt?
    assert len(new_user.projects) == 1
    assert new_user.projects[0].name == "Python Lernen"
    print("✅ Check bestanden: User kennt sein Projekt.")

    # Test 2: Hat der User Zugriff auf seinen Task?
    assert len(new_user.tasks) == 1
    assert new_user.tasks[0].title == "Unit Tests schreiben"
    print("✅ Check bestanden: User kennt seinen Task.")

    # Test 3: Rückwärts-Check - Kennt der Task sein Projekt?
    task_from_db = session.query(Task).filter_by(title="Unit Tests schreiben").first()
    assert task_from_db.project.name == "Python Lernen"
    print("✅ Check bestanden: Task weiß, zu welchem Projekt er gehört.")

    print("--- Test erfolgreich beendet! 🚀 ---")


# Test ausführen
if __name__ == "__main__":
    try:
        test_create_full_workflow()
    except AssertionError as e:
        print(f"❌ TEST FEHLGESCHLAGEN: {e}")
    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")
    finally:
        session.close()