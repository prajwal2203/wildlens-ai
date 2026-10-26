from transformers import pipeline

# Load the image classification model
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)


def predict_animal(image):
    """
    Predict the contents of an uploaded image.
    """
    results = classifier(image)

    return results[:5]