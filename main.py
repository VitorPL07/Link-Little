from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


from fastapi.middleware.cors import CORSMiddleware
import pymysql
import random
from string import ascii_letters

import requests

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="views")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def init_connection():
    db = pymysql.connect(
        host='HOST',
        user='USERNAME',
        password='PASSWORD',
        database='DATABASE',
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = db.cursor()

    return db, cursor


def generateToken(number):
    lista = []
    for _ in range(number):
        lista.append(random.choice(list(ascii_letters)))

    return "".join(lista)


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        }
    )


@app.get("/l/{uri}")
def send_user(uri: str, request: Request):
    conn, cursor = init_connection()

    query = f"select * from url where url_final = '{uri}';"
    cursor.execute(query)

    result = cursor.fetchone()

    conn.close()

    if result:
        return RedirectResponse(result["url_main"])
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request
            }
        )


@app.get("/user/create")
def user_create():

    conn, cursor = init_connection()
    while True:
        token = generateToken(10)
        query = f"select * from users where token = '{token}';"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            break

    query = f"insert into users (token) values ('{token}');"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return {
        "status": 200,
        "message": "Usuário cadastrado com sucesso!",
        "token": token
    }


@app.post("/user/get/{token}")
def get_url_by_token(token: str):
    conn, cursor = init_connection()

    query = f"select * from users where token = '{token}';"

    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        idUser = result["idusers"]

        query = f"select * from url where id_father = '{idUser}';"

        cursor.execute(query)

        result = cursor.fetchall()

        conn.close()

        if result:
            return {
                "status": 200,
                "content": result
            }
        else:
            return {
                "status": 202,
                "message": "Nenhum link foi cadastrado com esse token"
            }
    else:
        return {
            "status": 500,
            "message": "Esse token não está cadastrado"
        }


@app.post("/url/set/{token}")
def set_url(token: str, url: str):

    conn, cursor = init_connection()

    try:
        if requests.get(url).status_code != 200:
            return {
                "status": 400,
                "message": "A URL passada é inválida!"
            }
    except requests.exceptions.MissingSchema:
        url = "https://" + url

        try:
            if requests.get(url).status_code != 200:
                return {
                    "status": 400,
                    "message": "A URL passada é inválida!"
                }
        except requests.exceptions.MissingSchema:
            return {
                "status": 400,
                "message": "A URL passada é inválida!"
            }

    query = f"select * from users where token = '{token}';"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        uri = generateToken(4)
        query = f"insert into url (url_main, url_final, id_father) values ('{url}', '{uri}', {result['idusers']});"
        cursor.execute(query)
        conn.commit()
        conn.close()

        return {
            "status": 200,
            "message": "A Url foi cadastrada com sucesso!",
            "uri": uri
        }
    else:
        return {
            "status": 400,
            "message": "O Token passado é inválido!"
        }
