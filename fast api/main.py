from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from auth import (
    users,
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
    ADMIN_REGISTRATION_KEY
)

from llm import analyze_document


app = FastAPI(
    title="AI Document Intelligence API",
    description=(
        "Secure LLM-powered document analysis "
        "using FastAPI, JWT and Ollama"
    ),
    version="1.0.0"
)



class RegisterRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=30
    )

    password: str = Field(
        min_length=6,
        max_length=72
    )

    role: str = "user"

    admin_key: str | None = None



@app.get("/")
def home():

    return {
        "message": "AI Document Intelligence API is running"
    }


@app.post("/register")
def register(
    request: RegisterRequest
):

    username = request.username.strip().lower()

    if username in users:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    role = request.role.lower()

    if role == "user":

        assigned_role = "user"

    
    elif role == "admin":

        if not ADMIN_REGISTRATION_KEY:

            raise HTTPException(
                status_code=500,
                detail="Admin registration is not configured"
            )

        if request.admin_key != ADMIN_REGISTRATION_KEY:

            raise HTTPException(
                status_code=403,
                detail="Invalid admin registration key"
            )

        assigned_role = "admin"

    else:

        raise HTTPException(
            status_code=400,
            detail="Role must be user or admin"
        )

    users[username] = {
        "username": username,
        "password": hash_password(
            request.password
        ),
        "role": assigned_role
    }

    return {
        "message": "User registered successfully",
        "username": username,
        "role": assigned_role
    }



@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    username = form_data.username.strip().lower()

    user = authenticate_user(
        username,
        form_data.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        username=user["username"],
        role=user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }



@app.get("/profile")
def profile(
    current_user=Depends(get_current_user)
):

    return {
        "username": current_user["username"],
        "role": current_user["role"]
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),

    instruction: str = Form(
        "Summarize this document and list the key points."
    ),

    current_user=Depends(get_current_user)
):

  
    content = await file.read()

    try:

        document_text = content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail=(
                "For this version, please upload "
                "a UTF-8 text file."
            )
        )

    if not document_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Document is empty"
        )


    answer = analyze_document(
        document_text,
        instruction
    )

    return {
        "username": current_user["username"],
        "filename": file.filename,
        "analysis": answer
    }



@app.get("/admin")
def admin_endpoint(
    current_user=Depends(require_admin)
):

    return {
        "message": "Admin authorization successful",
        "username": current_user["username"],
        "role": current_user["role"]
    }
    
    
    
    
    
    
    
    