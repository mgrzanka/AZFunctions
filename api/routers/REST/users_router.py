from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, text
from typing import Annotated
import logging

from api.models.user_model import UserPublic, UserBase, User, UserUpdate
from api.database import get_session
from api.dependencies import validate_internal_secret
from api.config.BlobHolderService import BlobHolderService
from api.config.envs import QUERY_BLOB_NAME


SessionDep = Annotated[Session, Depends(get_session)]

blob_holder_service = BlobHolderService()

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/custom-query",
            response_model=list[UserPublic] | UserPublic,
            dependencies=[Depends(validate_internal_secret)])
def perform_custom_query_from_storage(db_session: SessionDep):
    query_content = blob_holder_service.get_blob_content(QUERY_BLOB_NAME)
    print(f"Reading QUERY: {query_content}")

    query = text(query_content)

    try:
        query_result = db_session.connection().execute(query).fetchall()
    except Exception as e:
        logging.error(f"There was issue while executing your query: {e}")
        raise e

    return query_result


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
    users = db_session.exec(select(User).offset(offset).limit(limit)).all()
    return users


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
