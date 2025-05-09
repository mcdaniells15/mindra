import asyncio
import aiohttp
from typing import Dict, Any
from ..config import Config
import google.generativeai as genai
from ..core.rate_limiter import rate_limit
from ..exceptions import APIError, RateLimitError, ValidationError

class APIClient:
    """Client for handling API communication."""
    
    def __init__(self):
        if not Config.API_KEY:
            raise ValidationError(
                "API key not configured",
                field="API_KEY",
                details={"config_source": "Config.API_KEY"}
            )
        
        self.api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.API_MODEL}:generateContent?key={Config.API_KEY}"
        self.headers = {
            "Content-Type": "application/json"
        }
        self._session = None
        
        # Configure Gemini API
        genai.configure(api_key=Config.API_KEY)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the current session or create a new one."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                connector=aiohttp.TCPConnector(
                    force_close=True,  # Force close connections
                    enable_cleanup_closed=True
                )
            )
        return self._session

    async def close(self):
        """Close the session properly."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with session cleanup."""
        await self.close()

    @rate_limit(
        key="global",
        max_requests=Config.RATE_LIMIT_SETTINGS["global"]["limit"],
        time_window=Config.RATE_LIMIT_SETTINGS["global"]["window"],
        namespace=Config.RATE_LIMIT_SETTINGS["global"]["namespace"]
    )
    async def make_api_call(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """Make API call using aiohttp with rate limiting and retry logic."""
        if not prompt:
            raise ValidationError(
                "Empty prompt provided",
                field="prompt",
                value=prompt
            )

        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                # Prepare request payload
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }]
                }
                
                async with self.session.post(
                    self.api_endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200 and "candidates" in result:
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                        return {"success": True, "content": text}
                    elif response.status == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitError(
                            "API rate limit exceeded",
                            retry_after=retry_after,
                            limit_type="api",
                            details={"response": result}
                        )
                    else:
                        error_details = result.get("error", {})
                        raise APIError(
                            error_details.get("message", f"API call failed with status {response.status}"),
                            status_code=response.status,
                            endpoint=self.api_endpoint,
                            details={"response": result}
                        )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                retries += 1
                last_error = APIError(
                    f"Connection error (attempt {retries}/{max_retries})",
                    details={
                        "attempt": retries,
                        "max_retries": max_retries,
                        "original_error": str(e)
                    }
                )
                
                if retries == max_retries:
                    await self.close()  # Close session on max retries
                    raise last_error
                
                # Close current session and create new one on next iteration
                await self.close()
                
                # Wait before retrying with exponential backoff
                await asyncio.sleep(2 ** retries)
                continue
                
            except RateLimitError:
                # Don't retry on rate limit errors, just propagate
                raise
            except (APIError, ValidationError):
                raise
            except Exception as e:
                await self.close()  # Close session on unexpected errors
                raise APIError(
                    "Unexpected API error",
                    details={"original_error": str(e)}
                )
            
            # If we get here, the request was successful
            break 