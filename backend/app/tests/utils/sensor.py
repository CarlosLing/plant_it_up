from sqlmodel import Session

from app import crud
from app.models import Sensor, SensorCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_sensor(db: Session) -> Sensor:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    name = random_lower_string()
    measurement = random_lower_string()
    location = random_lower_string()
    description = random_lower_string()
    sensor_in = SensorCreate(name=name, measurement=measurement, location=location, description=description)
    return crud.create_sensor(session=db, sensor_in=sensor_in, owner_id=owner_id)
