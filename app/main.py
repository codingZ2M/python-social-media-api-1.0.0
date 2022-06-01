

from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post (BaseModel):
    title: str
    content: str
    published: bool = True  # By default 'True'


while True:
    try:
        connection = psycopg2.connect(host='localhost', database='socialmediaapi', user='postgres',
                                      password='root', cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connecting to database failed!")
        print("Error: ", error)
        time.sleep(3)


@app.get("/")  # Decorator is used to use the path and HTTP method
async def root():
    return {"message": "Social Media API!"}


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):  # Referencing our 'Post' model(schema) for validation
    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s,%s) RETURNING * ",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    connection.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):  # Validating user value
    cursor.execute("SELECT * FROM posts WHERE id= %s", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found!")

    return({"Post Details": post})


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id= %s RETURNING * ", (str(id),))
    post_deleted = cursor.fetchone()
    connection.commit()

    if post_deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} doesn't exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("UPDATE posts SET title= %s, content=%s, published=%s  WHERE id = %s RETURNING *",
                   (post.title, post.content, post.published, str(id),))
    post_updated = cursor.fetchone()
    connection.commit()

    if post_updated == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} doesn't exist")

    return {"data": post_updated}
