from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from class_valuation_calculus import valuation_calculus as valuation
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="Option Valuation Web")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

new_valuation_type = valuation()

array_type_option = [
    "Call Europea",
    "Put Europea",
    "Call Americana",
    "Put Americana",
    "Call BlackScholes",
    "Put BlackScholes",
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response


@app.get("/process")
async def process():
    return {"option_type": array_type_option}


@app.post("/option_calculation")
async def option_calculation(request: Request):
    data_received = await request.json()
    logging.debug(data_received)
    valuation_option = {}
    for type_option_received in data_received[0].split(","):
        new_valuation_type.construct_info_need_valuate(type_option_received, data_received)
        if int(type_option_received) < 5:
            valuation_option[type_option_received] = new_valuation_type.definition_binomial_tree_calculation()
        else:
            valuation_option[type_option_received] = new_valuation_type.blackSholes_Modeling(type_option_received)
    logging.debug(valuation_option)
    return {"finalValue": valuation_option}
