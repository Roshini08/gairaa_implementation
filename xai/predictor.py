import torch

from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification
)

from config import MODEL_ID


class PlantDiseasePredictor:

    def __init__(self):

        print(
            "Loading Plant Disease CNN..."
        )

        self.processor = (
            AutoImageProcessor.from_pretrained(
                MODEL_ID
            )
        )

        self.model = (
            AutoModelForImageClassification
            .from_pretrained(
                MODEL_ID
            )
        )

        self.model.eval()

        self.device = torch.device(
            "cpu"
        )

        self.model.to(
            self.device
        )

        print(
            "CNN model loaded successfully."
        )


    def preprocess(
        self,
        image
    ):

        image = image.convert(
            "RGB"
        )

        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(
                self.device
            )
            for key, value in inputs.items()
        }

        return inputs


    def predict(
        self,
        image
    ):

        inputs = self.preprocess(
            image
        )

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )

        confidence, class_index = (
            torch.max(
                probabilities,
                dim=-1
            )
        )

        index = int(
            class_index.item()
        )

        confidence_value = float(
            confidence.item()
        )

        label = (
            self.model.config
            .id2label[index]
        )

        return {

            "label": label,

            "confidence":
                confidence_value,

            "confidence_percent":
                round(
                    confidence_value * 100,
                    2
                ),

            "class_index":
                index,

            "inputs":
                inputs
        }


_predictor = None


def get_predictor():

    global _predictor

    if _predictor is None:

        _predictor = (
            PlantDiseasePredictor()
        )

    return _predictor



