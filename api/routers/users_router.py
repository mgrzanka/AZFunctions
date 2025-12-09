from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Annotated

from api.models.user_model import UserPublic, UserBase, User, UserUpdate
from api.database import get_session


SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get("/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: str, db_session: SessionDep):
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserPublic])
def get_all_users(db_session: SessionDep,
                  offset: int = 0,
                  limit: Annotated[int, Query(le=100)] = 100):
    heroes = db_session.exec(select(User).offset(offset).limit(limit)).all()
    return heroes


@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserBase, db_session: SessionDep):
    db_user = User.model_validate(user_data)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, new_user_data: UserUpdate, db_session: SessionDep):
    user_db = db_session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Hero not found")

    user_data = new_user_data.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)

    db_session.add(user_db)
    db_session.commit()
    db_session.refresh(user_db)

    return user_db


@router.delete("/{user_id}")
def delete_user(user_id: int, db_session: SessionDep):
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USer not found")
    db_session.delete(user)
    db_session.commit()
    return {"ok": True}
