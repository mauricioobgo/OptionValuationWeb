import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from class_valuation_calculus import ValuationCalculus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Option Valuation Web")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OPTION_TYPES = [
    "Call Europea",
    "Put Europea",
    "Call Americana",
    "Put Americana",
    "Call BlackScholes",
    "Put BlackScholes",
]

BASE_DAYS = 360


class CalculationRequest(BaseModel):
    option_types: list[int]
    spot: float = Field(..., gt=0)
    strike: float = Field(..., gt=0)
    rate: float
    volatility: float = Field(..., ge=0)
    time_days: float = Field(..., gt=0)
    nodes: int = Field(..., gt=0, le=100)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response


@app.get("/process")
async def process():
    return {"option_type": OPTION_TYPES}


@app.post("/option_calculation")
async def option_calculation(body: CalculationRequest):
    calculator = ValuationCalculus(
        spot=body.spot,
        strike=body.strike,
        rate=body.rate,
        volatility=body.volatility,
        time_years=body.time_days / BASE_DAYS,
        nodes=body.nodes,
    )
    results: dict[str, float] = {}
    for opt_type in body.option_types:
        if opt_type < 5:
            results[str(opt_type)] = calculator.price_binomial(opt_type)
        else:
            results[str(opt_type)] = calculator.price_black_scholes(opt_type)
    logger.info("option_calculation results: %s", results)
    return {"finalValue": results}
