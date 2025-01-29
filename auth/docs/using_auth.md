# Integrating with AFEAF Auth Service

This guide explains how to integrate your service with the AFEAF Auth Service for authentication.

## Overview

The Auth Service provides a centralized authentication system that other services can use. Instead of implementing their own auth, services can redirect users to the auth service for login and verify authentication status through an API endpoint.

## Network Setup

All services should be on the same Docker network. Add this to your `docker-compose.yml`:

```yaml
services:
  your-service:
    # ... your service config ...
    networks:
      - afeaf-network

networks:
  afeaf-network:
    external: true
```

## Integration Steps

### 1. Redirect Unauthenticated Users to Auth Service

When a user tries to access your protected routes, redirect them to the auth service login:

```python
# Example redirect URL
AUTH_SERVICE_URL = "http://auth-service:8000/login"

@app.get("/protected-route")
async def protected_route():
    # Add your service's return URL as a parameter
    return RedirectResponse(
        f"{AUTH_SERVICE_URL}?redirect_url=http://your-service:port/your-return-path"
    )
```

### 2. Verify Authentication Status

Before allowing access to protected routes, verify the user's authentication status:

```python
import httpx

async def verify_auth():
    async with httpx.AsyncClient() as client:
        try:
            # Call auth service verify endpoint
            response = await client.get(
                "http://auth-service:8000/auth/verify",
                cookies=request.cookies  # Forward the session cookie
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

@app.get("/protected-route")
async def protected_route():
    auth_status = await verify_auth()
    if not auth_status:
        return RedirectResponse(f"{AUTH_SERVICE_URL}?redirect_url=...")

    # User is authenticated, proceed with your logic
    user_info = auth_status["user"]
    return {"message": f"Welcome {user_info['username']}"}
```

### 3. Required Dependencies

Add these to your `requirements.txt`:

```
httpx==0.24.1  # For making HTTP requests to auth service
```

## Authentication Flow

1. User attempts to access your service's protected route
2. Your service checks authentication status with auth service
3. If not authenticated, redirect to auth service login
4. User logs in at auth service
5. Auth service redirects back to your service's return URL
6. Your service verifies authentication and proceeds

## Security Considerations

1. Always verify authentication status before allowing access to protected routes
2. Use HTTPS in production
3. Keep the auth service internal to your network
4. Don't expose the verify endpoint publicly

## Example Implementation

Here's a minimal FastAPI service example:

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import httpx

app = FastAPI()

AUTH_SERVICE_URL = "http://auth-service:8000"
SERVICE_URL = "http://your-service:port"

async def verify_auth(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                cookies=request.cookies
            )
            return response.status_code == 200
        except Exception:
            return False

@app.get("/protected")
async def protected_route(request: Request):
    is_authenticated = await verify_auth(request)
    if not is_authenticated:
        return RedirectResponse(
            f"{AUTH_SERVICE_URL}/login?redirect_url={SERVICE_URL}/protected"
        )
    return {"message": "You have access to protected route"}
```

## Troubleshooting

1. Ensure your service is on the same Docker network as the auth service
2. Check that cookies are being properly forwarded
3. Verify the auth service is accessible from your service
4. Check logs for any connection errors

## Need Help?

Contact the AFEAF team for support or to report issues.