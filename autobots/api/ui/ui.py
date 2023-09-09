import gotrue
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from gotrue import UserResponse, AuthResponse, SignInWithEmailAndPasswordCredentials
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from autobots.auth.security import get_user_from_access_token
from autobots.conn.supabase.supabase import get_supabase
from autobots.core.settings import get_settings

router = APIRouter()


templates = Jinja2Templates(directory="autobots/ui/templates")


async def get_user_from_cookie(request: Request) -> UserResponse | None:
    token = request.cookies.get("Authorization")
    if not token:
        return None
    user = get_user_from_access_token(api_key_query=None, api_key_header=None, api_key_cookie=token)
    if not user:
        return None
    return user


@router.post("/cookie")
async def cookie(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    auth_res: AuthResponse = get_supabase().client.auth.sign_in_with_password(
        credentials=SignInWithEmailAndPasswordCredentials(
            email=form_data.username, password=form_data.password
        )
    )
    user: gotrue.User | None = auth_res.user
    session: gotrue.Session | None = auth_res.session
    if not user or not session:
        raise HTTPException(status_code=401, detail="User Session not found")

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {auth_res.session.access_token}",
        domain=get_settings().COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@router.get("/cookie/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain=get_settings().COOKIE_DOMAIN)
    return response


@router.get("/")
async def index(request: Request):
    user: UserResponse | None = await get_user_from_cookie(request)
    if user:
        return templates.TemplateResponse("home.html", {"request": request, "user": user.user})
    else:
        return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/docs")
async def api_docs(request: Request):
    user: UserResponse | None = await get_user_from_cookie(request)
    if user:
        return templates.TemplateResponse("docs.html", {"request": request, "user": user})
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response


# @router.get("/platform_summary")
# async def api_docs(request: Request):
#     user: UserResponse | None = await get_user_from_cookie(request)
#     if user:
#         return templates.TemplateResponse("platform_summary.html", {"request": request, "user": user})
#     else:
#         response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
#         return response
