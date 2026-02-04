import requests
from core_v2.domain.interfaces.communication_service import ICommunicationService

class HassCommunicationAdapter(ICommunicationService):
    def __init__(self, hass_url: str, token: str, media_player: str):
        self.url = hass_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.media_player = media_player

    def speak(self, text: str, language: str = "es") -> bool:
        """Utiliza el servicio TTS de Home Assistant para verbalizar texto."""
        
        # Check if we are targeting a satellite directly
        if self.media_player.startswith("assist_satellite."):
            endpoint = f"{self.url}/api/services/assist_satellite/announce"
            payload = {
                "entity_id": self.media_player,
                "message": text
            }
        else:
            # Standard Media Player TTS
            endpoint = f"{self.url}/api/services/tts/speak"
            payload = {
                "engine_id": "tts.piper",
                "media_player_entity_id": self.media_player,
                "message": text,
                "language": language
            }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"HASS TTS Success: {text}")
                return True
            else:
                print(f"HASS TTS Error ({response.status_code}): {response.text}")
                # Fallback to google_translate if piper fails or isn't first choice
                if not self.media_player.startswith("assist_satellite."):
                     return self._fallback_speak(text, language)
                return False
        except Exception as e:
            print(f"HASS Connection Exception: {e}")
            return False

    def _fallback_speak(self, text, language):
        endpoint = f"{self.url}/api/services/tts/google_translate_say"
        payload = {
            "entity_id": self.media_player,
            "message": text,
            "language": language
        }
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

    def notify(self, message: str) -> bool:
        """Envía una notificación al sistema persistente de HASS."""
        endpoint = f"{self.url}/api/services/persistent_notification/create"
        payload = {
            "title": "Anticitera Flux",
            "message": message
        }
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"HASS Notification Error: {e}")
            return False
