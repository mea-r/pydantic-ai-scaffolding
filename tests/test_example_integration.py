import pytest
from ai_helper import AiHelper

models_to_test = [
    ["google", "google/gemini-2.0-flash-lite-001"],  # provider first, model second
    ["open_router", "anthropic/claude-3-haiku"],
    ["anthropic", "anthropic/claude-3-haiku-20240307"],
    ["openai", "openai/gpt-4"],

    # these are supposed to throw an error
    ["open_router", "deepseek/deepseek-prover-v2:free"],
    ["openai", "error"],
    ["openai", "openai/errormodel"],
]

@pytest.mark.parametrize("provider, model", models_to_test)
def test_ai_helper_integration(provider, model):
    """
    Integration test for the AiHelper class using various models and providers.
    """
    base = AiHelper()

    # Models expected to fail
    if model == "error":
        with pytest.raises(Exception, match=r"Model name 'error' must be in the format 'provider/model_name'\."):
            base.test(model_name=model, provider=provider)
    elif model == "openai/errormodel":
         with pytest.raises(Exception, match=r"status_code: 404, model_name: errormodel"):
            base.test(model_name=model, provider=provider)
    elif model == "deepseek/deepseek-prover-v2:free":
         with pytest.raises(Exception, match=r"status_code: 404, model_name: deepseek/deepseek-prover-v2:free"):
            base.test(model_name=model, provider=provider)
    else:
        # Models expected to succeed
        try:
            result, report = base.test(model_name=model, provider=provider)
            # Basic assertions to check if the test ran and returned something
            assert result is not None
            assert report is not None
            # Assertions for fill_percentage and cost
            assert report.fill_percentage == 100
            assert report.cost > 0
        except Exception as e:
            pytest.fail(f"Test failed for model {model} with provider {provider}: {e}")
