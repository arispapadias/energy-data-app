from fastapi import FastAPI, HTTPException, Query
from utils import download_xlsx_file, parse_and_aggregate_data

app = FastAPI()

@app.get("/get_energy_data/")
async def get_energy_data(target_date: str = Query(..., description="Target date in YYYYMMDD format")):
    try:
        file_path = download_xlsx_file(target_date)
        
        data = parse_and_aggregate_data(file_path)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
