from __future__ import annotations

import os
from typing import Any, AsyncIterator, Dict, Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel


router = APIRouter()


class TTSV2Request(BaseModel):
    inputs: str
    speaker: Optional[str] = "Vivian"
    language: Optional[str] = "Auto"
    tibetan_speaker: Optional[str] = None
    tibetan_voice: Optional[str] = None
    hhdl_speaker: Optional[str] = None
    hhdl_voice: Optional[str] = None
    auto_voice: bool = False

    num_step: int = 32
    guidance_scale: float = 2.0
    denoise: bool = True
    preprocess_prompt: bool = True
    postprocess_output: bool = True
    speed: Optional[float] = None
    duration: Optional[float] = None

    chunk_tibetan: bool = False
    chunk_max_chars: int = 200
    chunk_gap_ms: float = 80.0
    stream_normalize_numbers: bool = True


def _tts_base_url() -> str:
    base = (os.getenv("TTS_BACKEND_URL_V2") or "").strip()
    if not base:
        raise HTTPException(status_code=500, detail="Missing TTS_BACKEND_URL_V2 in environment")
    return base.rstrip("/")

def _model_auth() -> str:
    model_auth = os.getenv("MODEL_AUTH_V2")
    if not model_auth:
        raise HTTPException(status_code=500, detail="Missing MODEL_AUTH_V2 in environment")
    return model_auth

def _timeout() -> httpx.Timeout:
    # Long enough for cold starts + long synthesis; streaming uses separate semantics.
    return httpx.Timeout(connect=10.0, read=300.0, write=30.0, pool=30.0)


@router.post("/")
async def tts_v2(
    body: TTSV2Request,
    client_request: Request,
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    url = f"{_tts_base_url()}/v2/tts"
    headers = {
        "X-Org-Id": x_org_id,
        "Authorization": f"Bearer {_model_auth()}"
    }
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    async with httpx.AsyncClient(timeout=_timeout()) as client:
        try:
            resp = await client.post(url, json=body.model_dump(), headers=headers)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"TTS backend error: {e}") from e

    # bubble backend errors
    if resp.status_code >= 400:
        detail: Any
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    # pass through useful metadata headers
    passthrough = {}
    for h in ["X-Request-Id", "X-Org-Id", "X-Sample-Rate", "X-Model", "X-Model-Role", "X-Voice-Mode"]:
        if h in resp.headers:
            passthrough[h] = resp.headers[h]
    return JSONResponse(resp.json(), headers=passthrough)


@router.post("/stream")
async def tts_stream_v2(
    body: TTSV2Request,
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    url = f"{_tts_base_url()}/v2/tts/stream"
    headers = {"X-Org-Id": x_org_id,"Authorization": f"Bearer {_model_auth()}"}
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    client = httpx.AsyncClient(timeout=_timeout())
    stream_ctx = client.stream("POST", url, json=body.model_dump(), headers=headers)
    try:
        resp = await stream_ctx.__aenter__()
    except httpx.HTTPError as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"TTS backend error: {e}") from e

    if resp.status_code >= 400:
        try:
            detail = await resp.aread()
        finally:
            await stream_ctx.__aexit__(None, None, None)
            await client.aclose()
        raise HTTPException(status_code=resp.status_code, detail=detail.decode("utf-8", errors="replace"))

    async def gen() -> AsyncIterator[bytes]:
        try:
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk
        finally:
            await stream_ctx.__aexit__(None, None, None)
            await client.aclose()

    out_headers: Dict[str, str] = {}
    for h in ["X-Request-Id", "X-Org-Id", "X-Sample-Rate", "X-Model", "X-Model-Role", "X-Voice-Mode"]:
        if h in resp.headers:
            out_headers[h] = resp.headers[h]
    out_headers["Cache-Control"] = "no-store"
    return StreamingResponse(gen(), media_type=resp.headers.get("content-type", "audio/wav"), headers=out_headers)


@router.post("/stream.raw")
async def tts_stream_raw_v2(
    body: TTSV2Request,
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    url = f"{_tts_base_url()}/v2/tts/stream.raw"
    headers = {"X-Org-Id": x_org_id,"Authorization": f"Bearer {_model_auth()}"}
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    client = httpx.AsyncClient(timeout=_timeout())
    stream_ctx = client.stream("POST", url, json=body.model_dump(), headers=headers)
    try:
        resp = await stream_ctx.__aenter__()
    except httpx.HTTPError as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"TTS backend error: {e}") from e

    if resp.status_code >= 400:
        try:
            detail = await resp.aread()
        finally:
            await stream_ctx.__aexit__(None, None, None)
            await client.aclose()
        raise HTTPException(status_code=resp.status_code, detail=detail.decode("utf-8", errors="replace"))

    async def gen() -> AsyncIterator[bytes]:
        try:
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk
        finally:
            await stream_ctx.__aexit__(None, None, None)
            await client.aclose()

    out_headers: Dict[str, str] = {}
    for h in ["X-Request-Id", "X-Org-Id", "X-Sample-Rate", "X-Model", "X-Model-Role", "X-Voice-Mode"]:
        if h in resp.headers:
            out_headers[h] = resp.headers[h]
    out_headers["Cache-Control"] = "no-store"
    return StreamingResponse(gen(), media_type="application/octet-stream", headers=out_headers)

