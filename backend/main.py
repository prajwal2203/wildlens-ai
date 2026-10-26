from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import get_connection
from ai.model import predict_animal
from PIL import Image
app = FastAPI(
    title="WildLens AI",
    description="AI-powered wildlife identification and conservation platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {
        "message": "WildLens AI API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/animals")
def get_animals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            common_name,
            scientific_name,
            description,
            habitat,
            diet,
            lifespan,
            conservation_status,
            geographic_range
        FROM animals
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    animals = []

    for row in rows:
        animals.append({
            "id": row[0],
            "common_name": row[1],
            "scientific_name": row[2],
            "description": row[3],
            "habitat": row[4],
            "diet": row[5],
            "lifespan": row[6],
            "conservation_status": row[7],
            "geographic_range": row[8]
        })

    return {
        "count": len(animals),
        "animals": animals
    }
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file)

        # AI prediction
        predictions = predict_animal(image)
        top_prediction = predictions[0]

        animal_label = top_prediction["label"]
        confidence = top_prediction["score"]

        # Extract scientific name from AI result
        scientific_name = animal_label.split(",")[-1].strip()

        # Connect to PostgreSQL
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                common_name,
                scientific_name,
                description,
                habitat,
                diet,
                lifespan,
                conservation_status,
                geographic_range
            FROM animals
            WHERE scientific_name = %s
            LIMIT 1
        """, (scientific_name,))

        animal = cursor.fetchone()

        cursor.close()
        conn.close()

        # Animal not found in database
        if not animal:
            return {
                "animal": animal_label,
                "confidence": confidence,
                "message": "Animal identified, but details not found in database."
            }

        # Return AI + database information
        return {
            "animal": animal[1],
            "scientific_name": animal[2],
            "confidence": confidence,
            "description": animal[3],
            "habitat": animal[4],
            "diet": animal[5],
            "lifespan": animal[6],
            "conservation_status": animal[7],
            "geographic_range": animal[8]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))