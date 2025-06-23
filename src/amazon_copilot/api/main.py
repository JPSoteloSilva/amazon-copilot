from fastapi import FastAPI

from amazon_copilot.api.routers import ai, categories, products, recommendations

app = FastAPI(title="Amazon Copilot API", description="API for Amazon Copilot")

app.include_router(products.router)
app.include_router(ai.router)
app.include_router(recommendations.router)
app.include_router(categories.router)


@app.get("/", response_model=dict[str, str])
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}
