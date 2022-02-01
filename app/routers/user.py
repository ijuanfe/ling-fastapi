from fastapi import status, HTTPException, Depends, APIRouter
from .. import database, models, schemas, utils
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(new_user: schemas.UserCreate, db: Session = Depends(database.get_db)):

    hashed_password = utils.hash_password(new_user.password)
    new_user.password = hashed_password
    user = models.User(**new_user.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} was not found")
    return user
