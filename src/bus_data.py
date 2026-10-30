from dataclasses import dataclass


@dataclass(frozen=True)
class Arrival:
    route_id: str
    eta_seconds: int


class SourceUnavailable(Exception):
    pass


def unavailable_arrivals() -> list[Arrival]:
    raise SourceUnavailable("공공 API 연동이 아직 준비되지 않았습니다.")
