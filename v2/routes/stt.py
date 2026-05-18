from __future__ import annotations

import os
from typing import Any, AsyncIterator, Dict, Optional

import httpx
from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse


router = APIRouter()


def _stt_base_url() -> str:
    base = (os.getenv("STT_BACKEND_URL_V2") or "").strip()
    if not base:
        raise HTTPException(status_code=500, detail="Missing STT_BACKEND_URL_V2 in environment")
    return base.rstrip("/")
def _model_auth() -> str:
    model_auth = os.getenv("MODEL_AUTH_V2")
    if not model_auth:
        raise HTTPException(status_code=500, detail="Missing MODEL_AUTH_V2 in environment")
    return model_auth

def _timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=10.0, read=300.0, write=60.0, pool=30.0)


@router.post("/transcribe")
async def transcribe_v2(
    request: Request,
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    JSON proxy endpoint (expects the same shapes STT backend supports).
    If you need multipart upload, use /transcribe/file.
    """
    url = f"{_stt_base_url()}/v2/stt/transcribe"
    headers: Dict[str, str] = {"X-Org-Id": x_org_id,"Authorization": f"Bearer {_model_auth()}"}
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e}") from e

    async with httpx.AsyncClient(timeout=_timeout()) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"STT backend error: {e}") from e

    if resp.status_code >= 400:
        detail: Any
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    passthrough: Dict[str, str] = {}
    for h in ["X-Request-Id", "X-Org-Id", "X-Model", "X-Batch-Size"]:
        if h in resp.headers:
            passthrough[h] = resp.headers[h]
    return JSONResponse(resp.json(), headers=passthrough)


@router.post("/transcribe/file")
async def transcribe_file_v2(
    file: UploadFile = File(...),
    language: str = Form("bo"),
    task: str = Form("transcribe"),
    return_timestamps: bool = Form(False),
    num_beams: int = Form(1),
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    Multipart proxy endpoint.
    """
    url = f"{_stt_base_url()}/transcribe"
    headers: Dict[str, str] = {"X-Org-Id": x_org_id,"Authorization": f"Bearer {_model_auth()}"}
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    audio_bytes = await file.read()
    files = {"file": (file.filename or "audio", audio_bytes, file.content_type or "application/octet-stream")}
    data = {
        "language": language,
        "task": task,
        "return_timestamps": "true" if return_timestamps else "false",
        "num_beams": str(int(num_beams)),
    }

    async with httpx.AsyncClient(timeout=_timeout()) as client:
        try:
            resp = await client.post(url, files=files, data=data, headers=headers)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"STT backend error: {e}") from e

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    passthrough: Dict[str, str] = {}
    for h in ["X-Request-Id", "X-Org-Id", "X-Model", "X-Batch-Size"]:
        if h in resp.headers:
            passthrough[h] = resp.headers[h]
    return JSONResponse(resp.json(), headers=passthrough)


@router.post("/transcribe.stream")
async def transcribe_stream_v2(
    request: Request,
    x_org_id: str = Header(..., alias="X-Org-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    Streaming NDJSON proxy (JSON input). For multipart streaming, add a separate endpoint if needed.
    """
    url = f"{_stt_base_url()}/transcribe.stream"
    headers: Dict[str, str] = {"X-Org-Id": x_org_id,"Authorization": f"Bearer {_model_auth()}"}
    if x_request_id:
        headers["X-Request-Id"] = x_request_id

    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e}") from e

    client = httpx.AsyncClient(timeout=_timeout())
    stream_ctx = client.stream("POST", url, json=payload, headers=headers)
    try:
        resp = await stream_ctx.__aenter__()
    except httpx.HTTPError as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"STT backend error: {e}") from e

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
    for h in ["X-Request-Id", "X-Org-Id", "X-Model", "X-Batch-Size"]:
        if h in resp.headers:
            out_headers[h] = resp.headers[h]
    out_headers["Cache-Control"] = "no-store"
    return StreamingResponse(gen(), media_type=resp.headers.get("content-type", "application/x-ndjson"), headers=out_headers)

