import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from src.schemas.analytics import CategoryNode, PreviousPeriodType

ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


@dataclass(frozen=True)
class CategoryInfo:
    """Минимальные данные о категории, нужные для построения дерева."""
    category_id: int
    name: str
    parent_id: int | None
    icon: str | None = None


def money(value: Decimal | int | float | None) -> Decimal:
    """Привести сумму к двум знакам после запятой."""
    return Decimal(value or 0).quantize(_CENT)


def period_days(date_from: date, date_to: date) -> int:
    """Длина периода в днях, обе границы включительно."""
    return (date_to - date_from).days + 1


def _last_day_of_month(day: date) -> date:
    return date(day.year, day.month, calendar.monthrange(day.year, day.month)[1])


def _previous_month_start(day: date) -> date:
    last_of_previous = day.replace(day=1) - timedelta(days=1)
    return last_of_previous.replace(day=1)


def resolve_previous_period(date_from: date, date_to: date) -> tuple[date, date, PreviousPeriodType]:
    """Выбрать предыдущий период для сравнения.

    1. Полный календарный месяц -> предыдущий календарный месяц.
    2. С 1-го числа до середины того же месяца -> те же дни предыдущего месяца
       (но не дальше его последнего дня).
    3. Любой другой период -> период такой же длины, заканчивающийся за день до начала.
    """
    same_month = (date_from.year, date_from.month) == (date_to.year, date_to.month)

    if date_from.day == 1 and same_month:
        prev_start = _previous_month_start(date_from)
        prev_last = _last_day_of_month(prev_start)
        if date_to == _last_day_of_month(date_from):
            return prev_start, prev_last, PreviousPeriodType.calendar_month
        prev_end = min(prev_start + timedelta(days=period_days(date_from, date_to) - 1), prev_last)
        return prev_start, prev_end, PreviousPeriodType.same_days_previous_month

    days = period_days(date_from, date_to)
    prev_end = date_from - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return prev_start, prev_end, PreviousPeriodType.same_length


def calc_percentage(part: Decimal, total: Decimal) -> float:
    """Доля part от total в процентах (один знак), 0.0 при нулевом total."""
    if not total:
        return 0.0
    return float(round(part / total * 100, 1))


def calc_change_pct(current: Decimal, previous: Decimal) -> float | None:
    """Изменение в % к предыдущему значению; None, если предыдущее значение равно нулю."""
    if not previous:
        return None
    return float(round((current - previous) / previous * 100, 1))


def calc_savings_rate(income: Decimal, expense: Decimal) -> float | None:
    """Норма сбережений в % от доходов; None, если доходов нет. Может быть отрицательной."""
    if income <= 0:
        return None
    return float(round((income - expense) / income * 100, 1))


def build_category_tree(
        own_totals: dict[int, Decimal],
        categories: list[CategoryInfo],
        grand_total: Decimal,
) -> list[CategoryNode]:
    """Построить дерево категорий.

    own_totals - суммы транзакций, привязанных прямо к категории.
    Сумма узла включает собственные транзакции и все вложенные категории.
    Проценты считаются от grand_total для всех уровней.
    """
    by_id = {c.category_id: c for c in categories}
    rolled: dict[int, Decimal] = {}

    for category_id, amount in own_totals.items():
        if category_id not in by_id:
            continue
        seen: set[int] = set()
        current: int | None = category_id
        while current is not None and current in by_id and current not in seen:
            seen.add(current)
            rolled[current] = rolled.get(current, ZERO) + amount
            current = by_id[current].parent_id

    nodes = {
        category_id: CategoryNode(
            category_id=category_id,
            name=by_id[category_id].name,
            icon=by_id[category_id].icon,
            total=money(total),
            percentage=calc_percentage(total, grand_total),
            children=[],
        )
        for category_id, total in rolled.items()
    }

    roots: list[CategoryNode] = []
    for category_id, node in nodes.items():
        parent_id = by_id[category_id].parent_id
        if parent_id in nodes:
            nodes[parent_id].children.append(node)
        else:
            roots.append(node)

    _sort_nodes(roots)
    return roots


def _sort_nodes(nodes: list[CategoryNode]) -> None:
    nodes.sort(key=lambda n: (-n.total, n.name))
    for node in nodes:
        _sort_nodes(node.children)
