import json
from backend.app.db.init_db import get_db_session
from training.build_dataset import build_label_studio_tasks

db = get_db_session()
try:
    tasks = build_label_studio_tasks(db)

    with open("label_studio_tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    print("Exported tasks for Label Studio")
finally:
    db.close()

