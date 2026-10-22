from decimal import Decimal

ZERO = Decimal("0.00")


def calc_percentage(part: Decimal, total: Decimal) -> float:
    """Вычисляет процент part от total."""
    if not total:
        return 0.0
    return float(round(part / total * 100, 1))
