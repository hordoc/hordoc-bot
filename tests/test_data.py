from datetime import datetime

from hordoc.data import dt_to_ms


def test_dt_to_ms():
    dt = datetime.fromtimestamp(1679838538.123)
    assert dt_to_ms(dt) == 1679838538123
