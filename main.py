import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import FileResponse
from pydantic import BaseModel

from database.database import AuthDatabase

app = FastAPI(title="UData")

db = AuthDatabase()  # Create an instance of the Database class


# Model for user registration
class UserCreate(BaseModel):
    username: str
    password: str


# Security
security = HTTPBasic()


# Dependency to get the current user
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    db = AuthDatabase()
    user = db.fetch_data('users', f"username = '{credentials.username}' AND password = '{credentials.password}'")
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user[0][0]


# Define the path to the "static" folder
STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)


# Route to register a new user
@app.post("/register",  tags=['AUTH'])
async def register(user_create: UserCreate):
    username = user_create.username
    password = user_create.password
    table = 'users'
    table_columns = ['username TEXT', 'password TEXT']
    db.create_table('users', table_columns)
    user = db.fetch_data(table, f"username = '{username}'")
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    db.insert_data(table, (username, password))
    return {"message": "User registered successfully"}


# Route to perform login
@app.post("/login", tags=['AUTH'])
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_current_user(credentials)
    return {"message": f"Welcome, {user}"}


# Route to upload a file
@app.post("/upload", tags=['Storage'])
async def upload_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    # Use UUID to generate a secure filename
    print(current_user)
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(STATIC_FOLDER, current_user)
    os.makedirs(file_path, exist_ok=True)
    file_path = os.path.join(file_path, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"message": "File uploaded successfully"}


# Route to list all uploaded files
@app.get("/files", tags=['Storage'])
async def list_files(current_user: str = Depends(get_current_user)):
    file_path = os.path.join(STATIC_FOLDER, current_user)
    files = os.listdir(file_path)
    return {"files": files}


# Route to download a file
@app.get("/download/{file_name}", tags=['Storage'])
async def download_file(file_name: str, response: Response, current_user: str = Depends(get_current_user)):
    file_path = os.path.join(STATIC_FOLDER, current_user)
    file_path = os.path.join(file_path, file_name)
    if os.path.exists(file_path):
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={file_name}"})
    raise HTTPException(status_code=404, detail="File not found")


# Route to delete a file
@app.delete("/delete/{file_name}", tags=['Storage'])
async def delete_file(file_name: str, current_user: str = Depends(get_current_user)):
    file_path = os.path.join(STATIC_FOLDER, current_user)
    file_path = os.path.join(file_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")


# if __name__ == '__main__':
#     import uvicorn
#
#     uvicorn.run(app, host="127.0.0.1", port=8000)
