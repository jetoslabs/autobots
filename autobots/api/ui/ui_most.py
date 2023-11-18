import gotrue
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from gotrue import UserResponse, AuthResponse
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from autobots.api.deps import get_user_from_cookie
from autobots.auth.auth import get_auth
from autobots.core.logging.log import Log
from autobots.core.settings import SettingsProvider

router = APIRouter()

templates = Jinja2Templates(directory="autobots/ui/templates")

@router.post("/cookie")
async def cookie(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    settings = SettingsProvider.sget()
    try:
        auth_res: AuthResponse = await get_auth().sign_in_with_password(form_data.username, form_data.password)
        user: gotrue.User | None = auth_res.user
        session: gotrue.Session | None = auth_res.session
        if not user or not session:
            raise HTTPException(status_code=401, detail="User Session not found")

        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        if settings.COOKIE_DOMAIN.find(request.base_url.hostname) >= 0:
            response.set_cookie(
                "Authorization",
                value=f"Bearer {auth_res.session.access_token}",
                domain=request.base_url.hostname,
                httponly=True,
                max_age=1800,
                expires=1800,
            )
        else:
            Log.error(f"Cookie domain codes not contain request base url: {request.base_url.hostname}")
        return response
    except Exception as e:
        Log.exception(str(e))
        return templates.TemplateResponse("index.html", {"request": request})


@router.get("/cookie/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain=request.base_url.hostname)
    await get_auth().sign_out()
    return response


@router.post("/signup")
async def signup(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    settings = SettingsProvider.sget()
    try:
        # Only allow meetkiwi emails to register
        if not form_data.username.endswith("@meetkiwi.co"):
            raise HTTPException(status_code=401, detail="User not a Meetkiwi email")

        auth_res: AuthResponse = await get_auth().sign_up_with_password(
            form_data.username, form_data.password, str(request.base_url)
        )
        user: gotrue.User | None = auth_res.user
        session: gotrue.Session | None = auth_res.session
        if not user or not session:
            raise HTTPException(status_code=401, detail="User Session not found")

        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        if settings.COOKIE_DOMAIN.find(request.base_url.hostname) >= 0:
            response.set_cookie(
                "Authorization",
                value=f"Bearer {auth_res.session.access_token}",
                domain=request.base_url.hostname,
                httponly=True,
                max_age=1800,
                expires=1800,
            )
        else:
            Log.error(f"Cookie domain codes not contain request base url: {request.base_url.hostname}")
        return response
    except HTTPException as e:
        Log.exception(str(e))
    except Exception as e:
        Log.exception(str(e))
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/")
async def page_index(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("home.html",
                                          {"request": request, "user": user.user, "version": settings.VERSION})
    else:
        return templates.TemplateResponse("index.html", {"request": request})


@router.get("/signup")
async def page_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login")
async def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/docs")
async def page_api_docs(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("docs.html",
                                          {"request": request, "user": user, "version": settings.VERSION})
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response


@router.get("/redoc")
async def page_api_docs(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("redoc.html",
                                          {"request": request, "user": user, "version": settings.VERSION})
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response


@router.get("/logs")
async def page_logs(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("logs.html",
                                          {"request": request, "user": user, "version": settings.VERSION})
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response


@router.get("/user")
async def page_user(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("user.html",
                                          {"request": request, "user": user, "version": settings.VERSION})
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response
