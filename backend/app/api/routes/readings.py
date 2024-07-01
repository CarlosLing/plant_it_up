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

# TODO: Add get route for min reading

# TODO: Add get route for average reading
