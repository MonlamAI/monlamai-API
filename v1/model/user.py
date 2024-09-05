from db import get_db
from models import Users
from sqlalchemy.orm import Session

def get_user_by_email(db:Session,email: str):
    # Manually retrieve the session object
        user = db.query(Users).filter(Users.email == email).first()
        return user
   

def create_user(db:Session,user_data: dict):
        user = get_user_by_email(db,user_data['email'])
        if not user:
            db_user = Users(
                email=user_data['email'],
                username=user_data['name'],
                picture=user_data['picture'],
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user.id
        return user.id
