# Guía de Configuración: Gmail OAuth2 para n8n

Para enviar correos desde n8n como **elswork@gmail.com**, necesitas crear una "App" en Google Cloud. Sigue estos pasos exactos:

## 1. Crear Proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Arriba a la izquierda, haz clic en el selector de proyectos y selecciona **"New Project"**.
3. Nombre: `Anticitera-Diplomacy`.
4. Haz clic en **Create**.

## 2. Activar la API de Gmail
1. En el menú de la izquierda, ve a **APIs & Services > Library**.
2. Busca `Gmail API`.
3. Haz clic en el resultado y luego en **Enable**.

## 3. Configurar Pantalla de Consentimiento
1. Ve a **APIs & Services > OAuth consent screen**.
2. Selecciona **External** y haz clic en **Create**.
3. Rellena lo básico:
   - **App name:** `Anticitera Dispatch`
   - **User support email:** Selecciona tu correo (`elswork@gmail.com`).
   - **Developer contact information:** `elswork@gmail.com`.
4. Haz clic en **Save and Continue** hasta llegar a la sección **Test Users**.
5. Haz clic en **Add Users** y pon tu propio correo: `elswork@gmail.com`. (Esto es vital para que funcione sin verificar la app).
6. Termina el asistente.

## 4. Obtener Credenciales (Los Valores que buscas)
1. Ve a **APIs & Services > Credentials**.
2. Haz clic en **+ CREATE CREDENTIALS** > **OAuth client ID**.
3. **Application type:** Selecciona `Web application`.
4. **Name:** `n8n Node`.
5. **Authorized redirect URIs:** (¡IMPORTANTE!)
   - Haz clic en **ADD URI**.
   - Pega EXACTAMENTE la URL que te muestra n8n en tu pantalla (Redirect URL). 
   - Según tu captura parece ser: `http://192.168.1.75:5678/rest/oauth2-credential/callback`
   - *Nota: Asegúrate de que esa IP (192.168.1.75) es accesible desde donde estás configurando esto.*
6. Haz clic en **Create**.

## 5. Resultado
Google te mostrará una ventana con:
- **Client ID**
- **Client Secret**

Copia estos dos valores y pégalos en los campos correspondientes de n8n. Finalmente, en n8n haz clic en el botón circular de "Sign in with Google" para conectar la cuenta.
