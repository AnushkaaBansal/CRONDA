from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import service_account
from typing import Optional
import os
import json

class AuthService:
    def __init__(self):
        self.credentials = None
        self.dev_mode = os.getenv('DEV_MODE', 'true').lower() == 'true'
        if not self.dev_mode:
            self.setup_credentials()

    def setup_credentials(self):
        """Setup Google Cloud credentials"""
        if self.dev_mode:
            return  # Skip credential setup in dev mode
            
        try:
            # Try to get credentials from environment variable first
            creds_json = os.getenv('GOOGLE_CREDENTIALS')
            if creds_json:
                creds_dict = json.loads(creds_json)
            else:
                # Fall back to credentials file
                creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'cronda-key.json')
                if not os.path.exists(creds_file):
                    raise FileNotFoundError(f"Credentials file not found: {creds_file}")
                with open(creds_file, 'r') as f:
                    creds_dict = json.load(f)

            self.credentials = service_account.Credentials.from_service_account_info(creds_dict)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to setup credentials: {str(e)}"
            )

    async def verify_token(self, token: str) -> bool:
        """Verify the authentication token"""
        if self.dev_mode:
            return True  # Always authenticate in dev mode
        try:
            return self.credentials and not self.credentials.expired
        except Exception:
            return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
auth_service = AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency for protected routes"""
    if auth_service.dev_mode:
        return "dev_user"  # Return a mock user in dev mode
        
    if not token or not await auth_service.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token