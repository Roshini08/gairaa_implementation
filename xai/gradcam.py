import numpy as np

import torch

import matplotlib.pyplot as plt

from captum.attr import (
    LayerGradCam,
    LayerAttribution
)


def find_last_conv_layer(
    model
):

    last_conv = None

    for module in model.modules():

        if isinstance(
            module,
            torch.nn.Conv2d
        ):

            last_conv = module

    if last_conv is None:

        raise RuntimeError(
            "No convolution layer found."
        )

    return last_conv


def generate_gradcam(
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


    target_layer = (
        find_last_conv_layer(
            model
        )
    )


    gradcam = LayerGradCam(
        forward_function,
        target_layer
    )


    attribution = (
        gradcam.attribute(
            pixel_values,
            target=target_class
        )
    )


    attribution = (
        LayerAttribution
        .interpolate(
            attribution,
            pixel_values.shape[-2:]
        )
    )


    heatmap = (
        attribution
        .squeeze()
        .detach()
        .cpu()
        .numpy()
    )


    heatmap = np.maximum(
        heatmap,
        0
    )


    if heatmap.max() > 0:

        heatmap = (
            heatmap /
            heatmap.max()
        )


    return heatmap


def save_gradcam(
    image,
    heatmap,
    output_path
):

    plt.figure(
        figsize=(6, 6)
    )


    plt.imshow(
        image.convert("RGB")
    )


    plt.imshow(
        heatmap,
        alpha=0.45,
        cmap="jet"
    )


    plt.axis("off")


    plt.tight_layout()


    plt.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0
    )


    plt.close()
    
    
    
    
    
    