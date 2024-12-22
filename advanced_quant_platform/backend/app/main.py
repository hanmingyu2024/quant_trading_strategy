from fastapi import FastAPI

app = FastAPI(title="Advanced Quant Platform")

@app.get("/")
async def root():
    return {"message": "Advanced Quant Platform API"}
