import os
import shutil
from pathlib import Path

from PIL import Image

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from xai_service import analyze_image
from agent import run_agent



app = FastAPI(
    title="Explainable Crop Disease AI",
    description="CNN + Grad-CAM + Integrated Gradients + AI Agent + Guardrails",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR = OUTPUT_DIR / "uploads"

OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)


@app.get("/", response_class=HTMLResponse)
async def home():

    return """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Explainable Crop Disease AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f4f8f5;
    color: #17251c;
}

.header {
    background: linear-gradient(135deg, #0b6b3a, #159447);
    color: white;
    padding: 28px 20px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    margin: 8px 0 0;
    opacity: 0.9;
}

.container {
    width: 92%;
    max-width: 1100px;
    margin: 30px auto;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 22px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

.upload-area {
    border: 2px dashed #39a96b;
    border-radius: 15px;
    padding: 35px;
    text-align: center;
    background: #f5fff8;
}

input[type="file"] {
    margin: 15px 0;
}

textarea {
    width: 100%;
    min-height: 100px;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #ccd8d0;
    resize: vertical;
    font-size: 15px;
}

button {
    width: 100%;
    margin-top: 18px;
    padding: 15px;
    border: none;
    border-radius: 10px;
    background: #087f45;
    color: white;
    font-size: 17px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #056936;
}

button:disabled {
    background: #999;
    cursor: not-allowed;
}

#loading {
    display: none;
    text-align: center;
    padding: 20px;
    color: #087f45;
    font-weight: bold;
}

#error {
    display: none;
    background: #ffecec;
    color: #b00020;
    padding: 15px;
    border-radius: 10px;
    margin-top: 15px;
}

#results {
    display: none;
}

.prediction {
    background: #ecfff3;
    border-left: 6px solid #087f45;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.prediction h2 {
    margin-top: 0;
    color: #087f45;
}

.confidence {
    font-size: 24px;
    font-weight: bold;
}

.xai-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.xai-box {
    border: 1px solid #d9e5dd;
    border-radius: 12px;
    padding: 15px;
    background: #fafdfb;
}

.xai-box h3 {
    color: #087f45;
}

.xai-box img {
    width: 100%;
    border-radius: 10px;
    margin-top: 10px;
}

.advisory {
    background: #f5f8ff;
    border-left: 6px solid #3b6fd8;
    padding: 20px;
    border-radius: 10px;
    white-space: pre-wrap;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    background: #d9f7e5;
    color: #087f45;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    padding: 25px;
    color: #68756d;
}

</style>

</head>

<body>

<div class="header">

    <h1>🌱 Explainable Crop Disease AI</h1>

    <p>
        CNN Disease Detection • Grad-CAM • Integrated Gradients
        • AI Agricultural Advisory • Guardrails
    </p>

</div>


<div class="container">

    <div class="card">

        <h2>🔬 Analyze Crop Leaf</h2>

        <div class="upload-area">

            <p>
                Upload a crop leaf image for disease detection
                and explainable AI analysis.
            </p>

            <input
                type="file"
                id="image"
                accept="image/*"
            >

        </div>

        <br>

        <label>
            <strong>💬 Ask the Agricultural AI</strong>
        </label>

        <textarea
            id="question"
            placeholder="Example: What should I do about this result?"
        >What should I do about this result?</textarea>

        <button
            id="analyzeButton"
            onclick="analyzeLeaf()"
        >
            🔍 Analyze Leaf
        </button>

        <div id="loading">
            ⏳ Analyzing image... Please wait.
            <br>
            CNN → XAI → Agent → Guardrails
        </div>

        <div id="error"></div>

    </div>


    <div id="results">

        <div class="card">

            <span class="badge">
                CNN PREDICTION
            </span>

            <div class="prediction">

                <h2 id="disease">-</h2>

                <p>Confidence:</p>

                <div
                    class="confidence"
                    id="confidence"
                >
                    -
                </div>

            </div>

        </div>


        <div class="card">

            <span class="badge">
                EXPLAINABLE AI
            </span>

            <h2>🧠 Why did the model make this prediction?</h2>

            <p id="explanation">-</p>

            <div class="xai-grid">

                <div class="xai-box">

                    <h3>🔴 Grad-CAM</h3>

                    <p>
                        Shows the regions of the leaf
                        that the CNN focused on.
                    </p>

                    <img
                        id="gradcam"
                        src=""
                        alt="Grad-CAM visualization"
                    >

                </div>


                <div class="xai-box">

                    <h3>🟢 Integrated Gradients</h3>

                    <p>
                        Shows which input regions
                        contributed to the prediction.
                    </p>

                    <img
                        id="integratedGradients"
                        src=""
                        alt="Integrated Gradients visualization"
                    >

                </div>

            </div>

        </div>


        <div class="card">

            <span class="badge">
                AI AGRICULTURAL ADVISORY
            </span>

            <h2>🤖 Agent Response</h2>

            <div
                class="advisory"
                id="advisory"
            >
                -
            </div>

        </div>

    </div>

</div>


<div class="footer">

    Explainable Crop Disease Detection & Safe Agricultural Advisory Agent

</div>


<script>

async function analyzeLeaf() {

    const imageInput =
        document.getElementById("image");

    const question =
        document.getElementById("question").value;

    const button =
        document.getElementById("analyzeButton");

    const loading =
        document.getElementById("loading");

    const errorBox =
        document.getElementById("error");

    const results =
        document.getElementById("results");


    if (!imageInput.files.length) {

        alert("Please upload a crop leaf image.");

        return;
    }


    button.disabled = true;

    loading.style.display = "block";

    errorBox.style.display = "none";

    results.style.display = "none";


    const formData = new FormData();

    formData.append(
        "image",
        imageInput.files[0]
    );

    formData.append(
        "question",
        question ||
        "What should I do about this result?"
    );


    try {

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Analysis failed."
            );

        }


        document.getElementById(
            "disease"
        ).innerText =
            data.disease || "Unknown";


        let confidence =
            Number(data.confidence || 0);


        if (confidence <= 1) {

            confidence *= 100;

        }


        document.getElementById(
            "confidence"
        ).innerText =
            confidence.toFixed(2) + "%";


        document.getElementById(
            "explanation"
        ).innerText =
            data.explanation ||
            "XAI explanation generated successfully.";


        if (data.gradcam) {

            document.getElementById(
                "gradcam"
            ).src =
                data.gradcam +
                "?t=" +
                Date.now();

        }


        if (data.integrated_gradients) {

            document.getElementById(
                "integratedGradients"
            ).src =
                data.integrated_gradients +
                "?t=" +
                Date.now();

        }


        let advisory =
            data.advisory;


        if (typeof advisory === "object") {

            advisory =
                advisory.guidance ||
                advisory.response ||
                advisory.answer ||
                advisory.message ||
                JSON.stringify(
                    advisory,
                    null,
                    2
                );

        }


        document.getElementById(
            "advisory"
        ).innerText =
            advisory ||
            "No advisory response generated.";


        results.style.display = "block";

        results.scrollIntoView({
            behavior: "smooth"
        });

    }

    catch (error) {

        console.error(error);

        errorBox.innerText =
            "❌ " + error.message;

        errorBox.style.display =
            "block";

    }

    finally {

        button.disabled = false;

        loading.style.display =
            "none";

    }

}

</script>

</body>

</html>
"""


@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    question: str = Form(
        "What should I do about this result?"
    )
):

    try:
        if not image.filename:

            raise HTTPException(
                status_code=400,
                detail="No image was uploaded."
            )


        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/jpg",
            "image/webp"
        }


        if image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail="Please upload JPG, PNG or WEBP."
            )



        extension = Path(
            image.filename
        ).suffix.lower()


        if extension not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }:

            extension = ".png"


        image_path = (
            UPLOAD_DIR / ("uploaded_leaf" + extension)
        )


        with open(image_path, "wb") as buffer:

            shutil.copyfileobj(
                image.file,
                buffer
            )


        print("\n====================================")
        print("IMAGE RECEIVED")
        print("====================================")


        pil_image = Image.open(
            image_path
        ).convert("RGB")


        print("Running CNN + XAI...")


        analysis = analyze_image(
            pil_image
        )


        print("CNN + XAI completed.")

        print("Analysis:", analysis)



        if isinstance(analysis, dict):

            disease = (
                analysis.get("disease")
                or analysis.get("prediction")
                or analysis.get("predicted_class")
                or analysis.get("label")
                or "Unknown"
            )

        else:

            disease = str(analysis)

        if isinstance(analysis, dict):

            confidence = (
                analysis.get("confidence")
                or analysis.get("score")
                or analysis.get("probability")
                or 0.0
            )

        else:

            confidence = 0.0


        try:

            confidence = float(
                confidence
            )

        except (TypeError, ValueError):

            confidence = 0.0


        if confidence > 1:

            confidence /= 100.0



        if isinstance(analysis, dict):

            explanation = (
                analysis.get("explanation")
                or analysis.get("xai_explanation")
                or
                "The prediction was explained using "
                "Grad-CAM and Integrated Gradients."
            )

        else:

            explanation = (
                "The prediction was explained using "
                "Grad-CAM and Integrated Gradients."
            )


        gradcam_path = None

        integrated_gradients_path = None


        if isinstance(analysis, dict):

            gradcam_path = (
                analysis.get("gradcam")
                or analysis.get("gradcam_path")
            )

            integrated_gradients_path = (
                analysis.get("integrated_gradients")
                or analysis.get("integrated_gradients_path")
                or analysis.get("ig")
            )


        def convert_to_url(path):

            if not path:

                return None


            path_string = str(path)


            if path_string.startswith("http://"):

                return path_string


            if path_string.startswith("https://"):

                return path_string


            normalized = path_string.replace(
                "\\",
                "/"
            )


            if "outputs/" in normalized:

                index = normalized.index(
                    "outputs/"
                )

                relative = normalized[
                    index + len("outputs/"):
                ]

                return "/outputs/" + relative


            try:

                resolved = Path(
                    path_string
                ).resolve()


                output_root = OUTPUT_DIR.resolve()


                relative = resolved.relative_to(
                    output_root
                )


                return (
                    "/outputs/"
                    + str(relative).replace(
                        "\\",
                        "/"
                    )
                )

            except Exception:

                return None


        gradcam_url = convert_to_url(
            gradcam_path
        )


        integrated_gradients_url = (
            convert_to_url(
                integrated_gradients_path
            )
        )


        print("Running agricultural AI agent...")


        agent_result = run_agent(
            disease=disease,
            confidence=confidence,
            explanation=explanation,
            question=question
        )


        print("Agent completed.")



        return JSONResponse(

            content={

                "success": True,

                "disease": str(
                    disease
                ),

                "confidence": confidence,

                "explanation": str(
                    explanation
                ),

                "gradcam": gradcam_url,

                "integrated_gradients":
                    integrated_gradients_url,

                "advisory": agent_result

            }

        )


    except HTTPException:

        raise


    except Exception as e:

        print("\n====================================")
        print("ANALYSIS ERROR")
        print("====================================")
        print(repr(e))
        print("====================================\n")


        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "Explainable Crop Disease AI"
    }
    
    
    
