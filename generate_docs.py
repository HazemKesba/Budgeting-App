import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BudgetingApp.settings")
django.setup()

import pdoc
pdoc.pdoc("users", "transactions", output_directory=Path("docs/api"))