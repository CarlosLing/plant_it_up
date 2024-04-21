from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Sensor,
    SensorCreate,
    SensorPublic,
    SensorsPublic,
    SensorUpdate,
    Message,
)

router = APIRouter()


@router.get("/", response_model=SensorsPublic)
def read_sensors(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve sensors.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Sensor)
        count = session.exec(count_statement).one()
        statement = select(Sensor).offset(skip).limit(limit)
        sensors = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Sensor)
            .where(Sensor.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Sensor)
            .where(Sensor.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        sensors = session.exec(statement).all()

    return SensorsPublic(data=sensors, count=count)


@router.get("/{id}", response_model=SensorPublic)
def read_sensor(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get sensor by ID.
    """
    sensor = session.get(Sensor, id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return sensor


@router.post("/", response_model=SensorPublic)
def create_sensor(
    *, session: SessionDep, current_user: CurrentUser, sensor_in: SensorCreate
) -> Any:
    """
    Create new sensor.
    """
    sensor = Sensor.model_validate(sensor_in, update={"owner_id": current_user.id})
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor


@router.put("/{id}", response_model=SensorPublic)
def update_sensor(
    *, session: SessionDep, current_user: CurrentUser, id: int, sensor_in: SensorUpdate
) -> Any:
    """
    Update an sensor.
    """
    sensor = session.get(Sensor, id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = sensor_in.model_dump(exclude_unset=True)
    sensor.sqlmodel_update(update_dict)
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor


@router.delete("/{id}")
def delete_sensor(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an sensor.
    """
    sensor = session.get(Sensor, id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if not current_user.is_superuser and (sensor.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(sensor)
    session.commit()
    return Message(message="Sensor deleted successfully")
