# Configuración Manual Infalible (3 Nodos)

Si la importación falla, vamos a crear los 3 nodos a mano. Tardarás 2 minutos.

## 1. Nodo Trigger: "Schedule"
1. Pulsa el **+ (Más)** arriba a la derecha.
2. Busca **"Schedule"**.
3. Configuración:
   - **Trigger Interval:** `Days`
   - **Time:** `09:00` (o la hora que quieras).
   - *Opcional: Añade otra hora para las 21:00.*

## 2. Nodo Acción: "HTTP Request"
1. Pulsa el **+** del nodo Schedule para encadenar el siguiente.
2. Busca **"HTTP Request"**.
3. Configuración:
   - **Method:** `GET`
   - **URL:** `http://192.168.1.XX:5050/generate-mep`  <-- **¡Pon la IP de tu PC aquí!**
   - **Authentication:** `None`

## 3. Nodo Acción: "Email" (Send Email)
*Nota: Busca "Send Email" o "Email", selecciona el que tiene el icono de un sobre genérico (SMTP).*

1. Pulsa el **+** del nodo HTTP Request.
2. Busca **"Send Email"**.
3. **Credentials:**
   - Selecciona "Create New".
   - **User:** `elswork@gmail.com`
   - **Password:** (Tu contraseña de aplicación de Google de 16 letras)
   - **Host:** `smtp.gmail.com`
   - **Port:** `465`
   - **SSL/TLS:** `Active` (On)
4. **Parameters:**
   - **From Email:** `elswork@gmail.com`
   - **To Email:** `elswork@gmail.com`
   - **Subject:** (Copia esto dentro, haz clic en el engranaje "Expression"):
     `{{ $json.email_draft.split('\n')[0] }}`
   - **Text:** (Expression):
     `{{ $json.email_draft }}`

## 4. Prueba Final
1. Dale al botón **"Execute Node"** en el Schedule o **"Execute Workflow"** abajo.
2. Deberías ver cómo pasa la bolita verde y te llega el correo.
