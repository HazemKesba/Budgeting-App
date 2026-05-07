import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BudgetingApp.settings")
django.setup()

import pdoc
pdoc.pdoc("users", "dashboard", "transactions", "budgets", "saving_goals", "users_profile", output_directory=Path("docs/api"))