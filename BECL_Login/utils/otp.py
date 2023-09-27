from django.conf  import settings
import os
from dotenv import load_dotenv
import pyotp

class OTP(object): 
    
    load_dotenv()

    totp_validator = pyotp.TOTP(os.getenv('SECRET_KEY_P'), interval=60)

    __instance = None 

    def __new__(cls): 
        if OTP.__instance is None:
            OTP.__instance = object.__new__(cls)
        
        return OTP.__instance

    @classmethod
    def generate_code(self) -> str:
        return self.totp_validator.now()
    @classmethod
    def validate_code(self, code) -> bool:
        return self.totp_validator.verify(code)
    


