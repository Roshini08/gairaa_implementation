from pathlib import Path


from predictor import (
    get_predictor
)


from gradcam import (
    generate_gradcam,
    save_gradcam
)


from integrated_gradients import (
    generate_integrated_gradients,
    save_integrated_gradients
)


OUTPUT_DIRECTORY = Path(
    "outputs"
)


OUTPUT_DIRECTORY.mkdir(
    exist_ok=True
)


def analyze_image(
    image
):

    predictor = (
        get_predictor()
    )


    prediction = (
        predictor.predict(
            image
        )
    )


    inputs = (
        prediction["inputs"]
    )


    class_index = (
        prediction["class_index"]
    )


    model = (
        predictor.model
    )


 

    gradcam_map = (
        generate_gradcam(
            model,
            inputs,
            class_index
        )
    )


    gradcam_path = (
        OUTPUT_DIRECTORY /
        "gradcam.png"
    )


    save_gradcam(
        image,
        gradcam_map,
        gradcam_path
    )


 

    integrated_gradients_map = (
        generate_integrated_gradients(
            model,
            inputs,
            class_index
        )
    )


    integrated_gradients_path = (
        OUTPUT_DIRECTORY /
        "integrated_gradients.png"
    )


    save_integrated_gradients(
        image,
        integrated_gradients_map,
        integrated_gradients_path
    )


    return {

        "disease":
            prediction["label"],

        "confidence":
            prediction["confidence"],

        "confidence_percent":
            prediction[
                "confidence_percent"
            ],

        "class_index":
            class_index,

        "gradcam_path":
            str(
                gradcam_path
            ),

        "integrated_gradients_path":
            str(
                integrated_gradients_path
            )
    }
    
    
    
    
    
    