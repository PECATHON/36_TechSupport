from fastapi import FastAPI, File, UploadFile
app = FastAPI()

@app.post("/upload")
async def parse_files(file: UploadFile = File(...)):
    return {"mesg": "helo"}