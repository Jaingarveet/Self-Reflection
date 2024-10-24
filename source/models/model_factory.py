from models.model import Model
from models.openai_model import OpenAIModel
# from models.azure_model import AzureModel
# from models.google_model import GoogleModel
# from models.anthropic_model import AnthropicModel

class ModelFactory:

    def create(self, model_name: str) -> Model:
        model_types = {
            "gpt-4": "openai"
        }

        model_type = model_types[model_name]

        if model_type == "openai":
            return OpenAIModel(model_name)

        elif model_type == "azure":
            return AzureModel(model_name)

        elif model_type == "google":
            return GoogleModel(model_name)

        elif model_type == "anthropic":
            return AnthropicModel(model_name)

        else:
            raise Exception(f"Unknown model type: {model_name}")

