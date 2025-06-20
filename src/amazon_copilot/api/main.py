from fastapi import FastAPI

from amazon_copilot.api.routers import products, recommendations

app = FastAPI(title="Amazon Copilot API", description="API for Amazon Copilot")

app.include_router(products.router)
app.include_router(recommendations.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}
