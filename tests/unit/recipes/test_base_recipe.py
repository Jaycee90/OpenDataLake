from unittest.mock import Mock, call

def test_run_executes_pipeline_in_order(recipe):
    raw_data = [{"id": "event-123"}]
    transformed_events = [Mock()]

    # By replacing recipe with pipeline, I've mocked out the recipe-specific methods, 
    # leaving only the orchestration logic in run() to execute. 
    pipeline = Mock()

    pipeline.extract.return_value = raw_data
    pipeline.transform.return_value = transformed_events

    recipe.extract = pipeline.extract
    recipe.transform = pipeline.transform
    recipe.validate = pipeline.validate
    recipe.load = pipeline.load

    recipe.run()

    assert pipeline.mock_calls == [
        call.extract(),
        call.transform(raw_data),
        call.validate(transformed_events),
        call.load(transformed_events),
    ]