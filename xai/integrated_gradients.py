import numpy as np

import torch

from captum.attr import (
    IntegratedGradients
)

from captum.attr import visualization as viz


def generate_integrated_gradients(
    model,
    inputs,
    target_class
):

    pixel_values = (
        inputs["pixel_values"]
    )


    def forward_function(
        x
    ):

        output = model(
            pixel_values=x
        )

        return output.logits


    integrated_gradients = (
        IntegratedGradients(
            forward_function
        )
    )


    baseline = torch.zeros_like(
        pixel_values
    )


    attribution = (
        integrated_gradients.attribute(
            pixel_values,
            baselines=baseline,
            target=target_class,
            n_steps=8
        )
    )


    attribution = (
        attribution
        .squeeze(0)
        .detach()
        .cpu()
        .numpy()
    )


    attribution = np.transpose(
        attribution,
        (1, 2, 0)
    )


    attribution = np.abs(
        attribution
    )


    attribution = attribution.mean(
        axis=2
    )


    if attribution.max() > 0:

        attribution = (
            attribution /
            attribution.max()
        )


    return attribution


def save_integrated_gradients(
    image,
    attribution,
    output_path
):

    image_array = (
        np.asarray(
            image.convert("RGB")
        ) / 255.0
    )


    figure, _ = (
        viz.visualize_image_attr(
            attribution,
            image_array,
            method="blended_heat_map",
            sign="positive",
            show_colorbar=True,
            use_pyplot=False
        )
    )


    figure.savefig(
        output_path,
        bbox_inches="tight"
    )
    figure.clf()
    
    
    
    
    
    
    