import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

mysql_config = {
    'user': 'root',
    'password': 'htsDFxPbLSCjASyZeFIdXKlsmsynwLOo',
    'host': 'viaduct.proxy.rlwy.net',
    'database': 'railway',
    'auth_plugin': 'mysql_native_password'
}

def get_connection():
    return mysql.connector.connect(**mysql_config)

class UserApi(BaseModel):
    Nombre: str
    Apellido: str  
    PhoneNumber: int
    Email: str
    Password: str
    Brd: str

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://alegod125.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def usuario_existe(email):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result > 0

@app.get('/getUser')
async def get_User():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users"
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los usuarios {e}")
    finally:
        cursor.close()
        conn.close()

@app.post('/createUser')
async def create_user(user: UserApi):
    if usuario_existe(user.Email):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    if len(user.Password) <= 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener más de 6 caracteres")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO users (nombre, apellido, PhoneNumber, email, password, Brd) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (user.Nombre, user.Apellido, user.PhoneNumber, user.Email, user.Password, user.Brd)
        cursor.execute(query, values)
        conn.commit()
        user_id = cursor.lastrowid
        return {'message': 'Usuario registrado exitosamente', 'user_id': user_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al registrar el usuario ({err})")
    finally:
        cursor.close()
        conn.close()

@app.post('/login')
async def login_user(email: str, password: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE Email = %s AND Password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        if user:
            return {'message': 'Usuario Iniciado exitosamente'}
        else:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al iniciar el usuario ({err})")
    finally:
        cursor.close()
        conn.close()

@app.get('/getID')
async def get_ID(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT UserID FROM users WHERE Email = %s AND Password = %s"
    try:
        cursor.execute(query, (email, password))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los usuarios {e}")
    finally:
        cursor.close()
        conn.close()

@app.get('/getUserInfo')
async def get_UserInfo(id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE UserID = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los usuarios {e}")
    finally:
        cursor.close()
        conn.close()

@app.delete('/deleteUser')
async def delete_user(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE UserID = %s"
    try:
        cursor.execute(query, (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el usuario {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
