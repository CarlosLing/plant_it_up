from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Reading, ReadingBase, ReadingsPublic, Sensor

router = APIRouter()


@router.post("/{sensor_id}", response_model=Reading)
def save_reading(
    session: SessionDep, current_user: CurrentUser, sensor_id: int, reading: ReadingBase
) -> Any:
    """
    Saves a reading for a sensor. Given the id
    """
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    reading = Reading.model_validate(reading, update={"sensor_id": sensor_id})
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


@router.get("/{sensor_id}", response_model=ReadingsPublic)
def get_sensor_readings(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Collect all readings from a sensor
    """

    # Validate the sensor
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get the Readings
    count_statement = (
        select(func.count()).select_from(Reading).where(Reading.sensor_id == sensor_id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Reading).where(Reading.sensor_id == sensor_id).offset(skip).limit(limit)
    )
    readings = session.exec(statement).all()

    return ReadingsPublic(data=readings, count=count)


# TODO: Add get route for max reading


@router.get("/{sensor_id}/max", response_model=Reading)
def get_max_reading(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    start: datetime,
    end: datetime,
) -> Any:
    """
    Collect the maximum value reading for a given sensor
    """

    # Validate the sensor
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    statement = (
        select(Reading)
        .where(
            Reading.sensor_id == sensor_id,
            Reading.timestamp >= start,
            Reading.timestamp <= end,
        )
        .order_by(Reading.value.desc())
        .limit(1)
    )
    reading = session.exec(statement).one_or_none()

    if reading is None:
        raise HTTPException(
            status_code=404, detail="No readings found in the specified range"
        )

    return reading


# TODO: Add get route for min reading


@router.get("/{sensor_id}/min", response_model=Reading)
def get_min_reading(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    start: datetime,
    end: datetime,
) -> Any:
    """
    Collect the maximum value reading for a given sensor
    """

    # Validate the sensor
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    statement = (
        select(Reading)
        .where(
            Reading.sensor_id == sensor_id,
            Reading.timestamp >= start,
            Reading.timestamp <= end,
        )
        .order_by(Reading.value.asc())
        .limit(1)
    )
    reading = session.exec(statement).one_or_none()

    if reading is None:
        raise HTTPException(
            status_code=404, detail="No readings found in the specified range"
        )

    return reading


# TODO: Add get route for average reading


@router.get("/{sensor_id}/avg", response_model=float)
def get_avg_reading(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    start: datetime,
    end: datetime,
) -> Any:
    """
    Collect the maximum value reading for a given sensor
    """

    # Validate the sensor
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    statement = select(func.avg(Reading.value)).where(
        Reading.sensor_id == sensor_id,
        Reading.timestamp >= start,
        Reading.timestamp <= end,
    )
    reading = session.exec(statement).one_or_none()

    print(reading)

    if reading is None:
        raise HTTPException(
            status_code=404, detail="No readings found in the specified range"
        )

    return reading


# TODO: Create new model with statistics per day


@router.get("/{sensor_id}/avg", response_model=float)
def get_avg_reading_2(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    start: datetime,
    end: datetime,
) -> Any:
    """
    Collect the maximum value reading for a given sensor
    """

    # Validate the sensor
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    statement = select(func.avg(Reading.value)).where(
        Reading.sensor_id == sensor_id,
        Reading.timestamp >= start,
        Reading.timestamp <= end,
    )
    reading = session.exec(statement).one_or_none()

    print(reading)

    if reading is None:
        raise HTTPException(
            status_code=404, detail="No readings found in the specified range"
        )

    return reading
    statement = (
        select(
            func.date(Reading.timestamp).label("date"),
            func.avg(Reading.value).label("average"),
        )
        .where(
            Reading.sensor_id == sensor_id,
            Reading.timestamp >= start,
            Reading.timestamp <= end,
        )
        .group_by(func.date(Reading.timestamp))
        .order_by(func.date(Reading.timestamp))
    )
    results = session.exec(statement).all()

    if not results:
        raise HTTPException(
            status_code=404, detail="No readings found in the specified range"
        )

    daily_averages = [
        DailyAverage(date=result.date, average=result.average) for result in results
    ]
