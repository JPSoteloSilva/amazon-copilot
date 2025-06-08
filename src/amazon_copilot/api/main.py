from fastapi import FastAPI

from amazon_copilot.api.routers import products

app = FastAPI(title="Amazon Copilot API", description="API for Amazon Copilot")

app.include_router(products.router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
