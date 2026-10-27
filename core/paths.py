from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
INSTRUMENTS_CSV = DATA / "kite_instruments.csv"
MODELS = ROOT / "_models"
