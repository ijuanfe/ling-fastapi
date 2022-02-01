from fastapi import status, Response, HTTPException, Depends, APIRouter
from .. import models, schemas, database, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=['Posts'])  # tags allows to group request into categories at http://localhost:8000/docs


@router.get("", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(database.get_db),
                    current_user: models.User = Depends(oauth2.get_current_user),
                    limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    # posts = db.query(models.Post).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).\
        group_by(models.Post.id).filter(models.Post.title.contains(search)).\
        limit(limit).offset(skip).all()
    return posts


@router.get("/{id}", response_model=schemas.PostOut)
# Automatically validate and convert the path parameter to an integer
async def get_post(id: int, db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(oauth2.get_current_user)):

    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).\
        group_by(models.Post.id).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    # if post.user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the request")
    return post


# Change the default returning status code when successfully made
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(database.get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the request")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(database.get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the request")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
# Extract all the fields from the request body
# and convert, store and validate the data based
# on the schema defined in PostCreate object
async def create_post(new_post: schemas.PostCreate, db: Session = Depends(database.get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):

    # "**new_post.dict()" automatically does this: (title=post.title, content=post.content, ...)
    post = models.Post(user_id=current_user.id, **new_post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
