from tempfile import template

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pyexpat.errors import messages
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from .db import init_db, get_session, AsyncSession
from .schemas import UserCreate, UserOut, NoteCreate, NoteOut, UserPublic
from .models import User
from . import crud
from .auth import hash_password


# Создаём экземпляр приложения FastAPI
app = FastAPI(title="Notes Service — Step 3: API + HTML Frontend")

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")



# Хук запуска: при старте приложения создаём таблицы (если их нет)
@app.on_event("startup")
async def on_startup() -> None:
    await init_db()

# -------------------
#   API эндпоинты
# -------------------

# Эндпоинт: создать пользователя
@app.post("/users", summary="Создание пользователя", response_model=UserOut, status_code=201, tags=["api"])
async def create_user_endpoint(
    payload: UserCreate, # тело запроса (JSON) → UserCreate
    session: AsyncSession = Depends(get_session) # берём сессию из зависимости
):
    try:
        user = await crud.create_user(session, username=payload.username)
    except IntegrityError:
# 409 — конфликт (например, нарушена уникальность username)
        raise HTTPException(status_code=409, detail="Пользователь уже существует")
    return user #{"success": True, "message": "Успешное создание пользователя"}


# Эндпоинт: создать заметку для существующего пользователя
@app.post("/notes", summary="Создание заметки", response_model=NoteOut, status_code=201, tags=["api"])
async def create_note_endpoint(
    payload: NoteCreate,
    session: AsyncSession = Depends(get_session)
):
# Проверяем, что владелец существует (иначе 404)
    result = await session.execute(select(User).where(User.id == payload.owner_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Выбранный пользователь не найден")


    note = await crud.create_note(
        session, owner_id=payload.owner_id, title=payload.title, content=payload.content
    )
    return note #{"success": True, "message": "Заметка создана"}


@app.post("/register", response_model=UserPublic)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли такой пользователь
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Создаём нового пользователя
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user



# Эндпоинт: получить все заметки пользователя
@app.get("/users/{user_id}/notes",summary="Получение всех заметок пользователя", response_model=list[NoteOut], tags=["api"])
async def list_user_notes(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Можно вернуть пустой список, но покажем 404, если пользователя нет
    result = await session.execute(select(User).where(User.id == user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    notes = await crud.get_user_notes(session, owner_id=user_id)
    return notes

# -------------------
#   HTML интерфейс
# -------------------

# Главная страница

@app.get("/", response_class=HTMLResponse, tags=["front"])
async def home (request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


#Регистрация

@app.get("/register-form", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Создание пользователя

@app.get("/users", response_class=HTMLResponse, tags=["front"])
async def user_page(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.post("users/create", tags=["front"])
async def create_user_from(
        username: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    try:
        await crud.create_user(session, username=username)
    except IntegrityError:
        return HTMLResponse("Пользователь уже существует", status_code=400)
    return RedirectResponse(url="/user",status_code=303)


# Заметки пользователя

@app.get("/users/{user_id}/notes_page", response_class=HTMLResponse, tags=["front"])
async def notes_page(user_id: int, request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    notes = await crud.get_user_notes(session, owner_id=user_id)
    return templates.TemplateResponse("notes.html", {"request": request, "user": user, "notes": notes})

# Создание заметки

@app.post("/users/{user_id}/notes/create", tags=["front"])
async def create_note_from(
        user_id: int,
        title: str = Form(...),
        content: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    await crud.create_note(session, owner_id=user_id, title=title, content=content)
    return RedirectResponse(url=f"/users/{user_id}/notes_page", status_code=303)
