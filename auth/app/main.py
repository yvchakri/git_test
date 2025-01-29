from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import logging
from passlib.hash import bcrypt
from .database import get_user_by_email, update_user_password, get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GenAI Team Portal")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # Change this to a secure secret key
    session_cookie="user_session"
)

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=303, detail="Not authenticated")
    return user

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
async def login_page(request: Request, message: str = None):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": message}
    )

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    redirect_url: str = Form(None)
):
    try:
        user = get_user_by_email(email)

        if not user or not bcrypt.verify(password, user['password_hash']):
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Incorrect email or password"
                }
            )

        # Set session data
        request.session["user"] = {
            "email": email,
            "username": email.split('@')[0],
            "group": user['user_group']
        }

        # Redirect to provided URL or default dashboard
        return RedirectResponse(
            url=redirect_url or "/dashboard",
            status_code=303
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "An error occurred during login"
            }
        )

@app.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": user["username"],
            "email": user["email"],
            "group": user["group"]
        }
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        if not email.endswith('@capgemini.com'):
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Please use your Capgemini email address"}
            )

        # Check if user exists in database
        existing_user = get_user_by_email(email)
        if existing_user:
            print(existing_user)
            # If user exists but has no password, update it
            if existing_user["password_hash"] in ("", None):
                hashed_password = bcrypt.hash(password)
                if update_user_password(email, hashed_password):
                    logger.info(f"Updated password for existing user: {email}")
                    return RedirectResponse(
                        url="/login?message=Registration successful. Please login.",
                        status_code=303
                    )
                else:
                    return templates.TemplateResponse(
                        "register.html",
                        {"request": request, "error": "Failed to update user password"}
                    )
            else:
                # User exists with password already set
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Email already registered"}
                )

        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "User is not allowed to register"}
        )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"Registration error: {str(e)}"}
        )

@app.get("/forgot-password")
async def forgot_password_page(request: Request, message: str = None):
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request, "message": message}
    )

@app.post("/forgot-password")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        if not email.endswith('@capgemini.com'):
            return templates.TemplateResponse(
                "forgot_password.html",
                {"request": request, "error": "Please use your Capgemini email address"}
            )

        if new_password != confirm_password:
            return templates.TemplateResponse(
                "forgot_password.html",
                {"request": request, "error": "Passwords do not match"}
            )

        user = get_user_by_email(email)
        if not user:
            return templates.TemplateResponse(
                "forgot_password.html",
                {"request": request, "error": "Email not found"}
            )

        hashed_password = bcrypt.hash(new_password)
        if update_user_password(email, hashed_password):
            logger.info(f"Password reset successful for user: {email}")
            return RedirectResponse(
                url="/login?message=Password reset successful. Please login with your new password.",
                status_code=303
            )
        else:
            return templates.TemplateResponse(
                "forgot_password.html",
                {"request": request, "error": "Failed to reset password"}
            )

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "error": f"An error occurred. Please try again later."}
        )

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        connection = get_db_connection()
        if connection is None:
            logger.error("Database connection failed")
            return {"status": "unhealthy", "database": "Database connection failed"}
        connection.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "unhealthy", "database": f"Health check error: {str(e)}"}

@app.get("/auth/verify")
async def verify_auth(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    return {
        "authenticated": True,
        "user": {
            "email": user["email"],
            "username": user["username"],
            "group": user["group"]
        }
    }
