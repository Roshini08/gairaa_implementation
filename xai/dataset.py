from datasets import load_dataset


DATASET_NAME = "mohanty/PlantVillage"

CONFIG_NAME = "color"


def load_plant_village():

    print(
        "Connecting to PlantVillage..."
    )

    dataset = load_dataset(
        DATASET_NAME,
        CONFIG_NAME,
        streaming=True
    )

    print(
        "\nPlantVillage connected successfully."
    )

    print(
        dataset
    )

    return dataset


def main():

    dataset = load_plant_village()

    train_data = dataset["train"]

    print(
        "\nDataset features:"
    )

    print(
        train_data.features
    )


if __name__ == "__main__":

    main()
    
    
    
    