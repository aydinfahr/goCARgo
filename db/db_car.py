from sqlalchemy.orm.session import Session
from schemas import CarBase
from db.models import DbCar

def create_car(db: Session, request: CarBase):
    new_car = DbCar(
        owner_id = request.owner_id,
        brand = request.brand,
        model = request.model,
        color = request.color
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car