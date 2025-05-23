import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")
EIA_BASE_URL = "https://api.eia.gov/v2"

app = FastAPI(title="EIA APIv2 MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class MetadataRequest(BaseModel):
    route: str  # e.g., "petroleum/pri/gnd"

class FacetRequest(BaseModel):
    route: str
    facet: str

class DataRequest(BaseModel):
    route: str
    start: str        # e.g. "2020-01"
    end: str          # e.g. "2020-12"
    frequency: str    # e.g. "monthly"
    facets: Optional[Dict[str, List[str]]] = None  # optional facet filters

def fetch_eia_metadata(route: str) -> dict:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="EIA_API_KEY not set")
    url = f"{EIA_BASE_URL}/{route}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_eia_facet_values(route: str, facet: str) -> dict:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="EIA_API_KEY not set")
    url = f"{EIA_BASE_URL}/{route}/facet/{facet}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

@app.get("/")
async def serve_index():
    """Serve the main HTML interface."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/metadata")
async def get_metadata(request: MetadataRequest):
    """
    Fetch metadata for an EIA APIv2 route.
    """
    try:
        metadata = fetch_eia_metadata(request.route)
        return metadata
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/facets")
async def get_facet_values(request: FacetRequest):
    """
    Fetch available values for a specific facet in an EIA route.
    """
    try:
        facet_values = fetch_eia_facet_values(request.route, request.facet)
        return facet_values
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data")
async def get_data(req: DataRequest):
    """
    Fetch time series data from an EIA APIv2 route.
    """
    try:
        url = f"{EIA_BASE_URL}/{req.route}/data"
        params = {
            "api_key": API_KEY,
            "start": req.start,
            "end": req.end,
            "frequency": req.frequency
        }
        # include any facet filters
        if req.facets:
            for facet_name, values in req.facets.items():
                # EIA API expects comma-separated values for facets
                params[f"facets[{facet_name}]"] = ",".join(values)
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)