from typing import Callable

from fastapi import Depends, FastAPI, HTTPException

from src.bus_data import Arrival, SourceUnavailable, unavailable_arrivals

app = FastAPI()
STOP_NUMBER = "38563"
STOP_DIRECTION = "경제자유구역청·국제업무지구역5번출구"


def get_arrivals() -> Callable[[], list[Arrival]]:
    return unavailable_arrivals


@app.get("/arrivals")
def arrivals(
    stop: str,
    direction: str,
    fetch: Callable[[], list[Arrival]] = Depends(get_arrivals),
):
    if stop != STOP_NUMBER or direction != STOP_DIRECTION:
        raise HTTPException(status_code=400, detail="지원하지 않는 정류소 또는 방향입니다.")
    try:
        results = fetch()
    except SourceUnavailable:
        raise HTTPException(status_code=503, detail="공공 API 연동 준비 중입니다.")
    return {
        "stop": STOP_NUMBER,
        "direction": STOP_DIRECTION,
        "arrivals": [
            {"route_id": item.route_id, "eta_seconds": item.eta_seconds}
            for item in results
        ],
    }
