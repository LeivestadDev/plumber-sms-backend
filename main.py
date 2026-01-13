@app.get("/")
def health():
    return {"status": "ok"}
