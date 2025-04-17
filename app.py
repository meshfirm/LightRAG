# app.py
from lightrag.api.lightrag_server import get_application
from lightrag_multitenant.main_integration import integrate_with_server

# Get the base LightRAG application
app = get_application()

# Integrate multi-tenant functionality
app = integrate_with_server(app)

# This is important for Google Cloud Run to find the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 9621)))