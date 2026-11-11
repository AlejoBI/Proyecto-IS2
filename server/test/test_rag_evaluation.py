from server.services.rag_evaluation import EvaluationCase, evaluate_cases


def test_reference_evaluation_measures_answers_and_sources():
    cases = [EvaluationCase("Where?", "Madrid", ("doc-1",))]
    metrics = evaluate_cases(
        cases,
        lambda _: {"answer": "The answer is Madrid", "sources": [{"document_id": "doc-1"}]},
    )

    assert metrics == {"answer_match": 1.0, "source_recall": 1.0}
