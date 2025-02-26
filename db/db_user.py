from sqlalchemy.orm.session import Session
from db.hash import Hash
from schemas import UserBase
from db.models import DbUser


def create_user(db: Session, request: UserBase):
    new_user = DbUser(
        username = request.username,
        email = request.email,
        full_name = request.full_name,
        password = Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Temporary
def get_all_users(db: Session):
    return db.query(DbUser).all()

def get_user(db: Session, id:int):
    #handle any exception
    return db.query(DbUser).filter(DbUser.id == id).first()

def update_user(db: Session, id: int, request: UserBase):
    user = db.query(DbUser).filter(DbUser.id == id)   # first()'e gerek duymadi!! cunku update(), bir Query nesnesi üzerinde çalışabilir.
    #handle any exception 
    user.update({
        DbUser.username: request.username,
        DbUser.email: request.email,
        DbUser.full_name: request.full_name,
        DbUser.password: Hash.bcrypt(request.password)
    })
    db.commit()
    return "User updated!"

def delete_user(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()  #  first() gerekli, delete() bir model nesnesi gerektirir
    #handle any exception
    db.delete(user)
    db.commit()
    return "User deleted!"
