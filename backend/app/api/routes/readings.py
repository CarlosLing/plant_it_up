from datetime import datetime, date
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Reading, ReadingBase, ReadingsPublic, Sensor, SensorStatisticsList
from datetime import timedelta
router = APIRouter()

def check_sensor_permission(session, current_user, sensor_id):
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")


@router.post("/{sensor_id}", response_model=Reading)
def save_reading(
    session: SessionDep, current_user: CurrentUser, sensor_id: int, reading: ReadingBase
) -> Any:
    """
    Saves a reading for a sensor. Given the id
    """
    # Validate the sensor
    check_sensor_permission(session, current_user, sensor_id)
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
    check_sensor_permission(session, current_user, sensor_id)

    # Get the Readings
    count_statement = (
        select(func.count()).select_from(Reading).where(Reading.sensor_id == sensor_id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Reading).where(Reading.sensor_id == sensor_id)
        .order_by(Reading.timestamp.desc()).offset(skip).limit(limit)
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
    check_sensor_permission(session, current_user, sensor_id)

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
    check_sensor_permission(session, current_user, sensor_id)

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
    check_sensor_permission(session, current_user, sensor_id)

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


@router.get("/{sensor_id}/stats", response_model=SensorStatisticsList)
def get_statistics(
    session: SessionDep,
    current_user: CurrentUser,
    sensor_id: int,
    start: date,
    end: date,
) -> Any:
    """
    Given a date range returns a Statistics List with all the statistics per day 
    """
    # Validate the sensor
    check_sensor_permission(session, current_user, sensor_id)
    # Calculate the number of days between start and end dates
    num_days = (end - start).days

    # Create a list to store the statistics per day
    statistics_list = []

    # Iterate over each day in the date range
    for i in range(num_days + 1):
        # Calculate the current date
        current_date = start + timedelta(days=i)

        # Calculate the start and end timestamps for the current day
        current_day_start = datetime.combine(current_date, datetime.min.time())
        current_day_end = datetime.combine(current_date, datetime.max.time())

        # Query the database for the statistics for the current day
        statement = (
            select(
                func.max(Reading.value).label("max_value"),
                func.min(Reading.value).label("min_value"),
                func.avg(Reading.value).label("avg_value"),
            )
            .where(
                Reading.sensor_id == sensor_id,
                Reading.timestamp >= current_day_start,
                Reading.timestamp <= current_day_end,
            )
            .group_by(func.date(Reading.timestamp))
        )
        statistics = session.exec(statement).one_or_none()

        # If no statistics found for the current day, skip it
        if statistics is None:
            continue

        # Add the statistics to the list
        statistics_list.append(
            {
                "date": current_date,
                "max_value": statistics.max_value,
                "min_value": statistics.min_value,
                "avg_value": statistics.avg_value,
            }
        )

    # Create the SensorStatisticsList object with the collected statistics
    sensor_statistics_list = SensorStatisticsList(data=statistics_list)

    return sensor_statistics_list
