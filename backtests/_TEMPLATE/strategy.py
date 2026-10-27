"""<Strategy name> — <creator>, <video url>

Rules (as stated in the video, see source.md for assumptions):
  Entry:
  Exit:
  Stop / target:
"""
import pandas as pd

PARAMS = {}


def signals(df: pd.DataFrame, p: dict) -> pd.DataFrame:
    """Decide on bar close; the engine fills on the next bar's open.

    Return any of: entry_long, exit_long, entry_short, exit_short (bool),
    and optionally sl / target (absolute prices for a trade entered off this bar).
    Never use future data: no shift(-1), no centred rolling windows.
    """
    out = pd.DataFrame(index=df.index)
    return out
