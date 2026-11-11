from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    reference_answer: str
    expected_sources: tuple[str, ...] = ()


def evaluate_cases(
    cases: Iterable[EvaluationCase],
    answer: Callable[[str], dict],
) -> dict[str, float]:
    cases = list(cases)
    if not cases:
        return {"answer_match": 0.0, "source_recall": 0.0}

    answer_matches = 0
    source_hits = 0
    source_total = 0
    for case in cases:
        result = answer(case.question)
        generated = str(result.get("answer", "")).strip().lower()
        reference = case.reference_answer.strip().lower()
        answer_matches += int(reference in generated)
        actual_sources = {source.get("document_id") for source in result.get("sources", [])}
        expected_sources = set(case.expected_sources)
        source_total += len(expected_sources)
        source_hits += len(actual_sources & expected_sources)

    return {
        "answer_match": answer_matches / len(cases),
        "source_recall": source_hits / source_total if source_total else 1.0,
    }
