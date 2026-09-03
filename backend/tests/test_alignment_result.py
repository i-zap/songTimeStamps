from uuid import uuid4

from app.alignment.result import (
    AlignmentResult,
    EvidenceItem,
    GlobalAlignmentEvidence,
    LocalAlignmentEvidence,
)


def test_alignment_result_supports_local_and_global_evidence():
    alignment_id = uuid4()

    local_evidence = LocalAlignmentEvidence(
        alignment_id=alignment_id,
        items=[
            EvidenceItem(
                name="vocal_activity",
                score=0.92,
                source="energy_detector",
            ),
        ],
        confidence=0.91,
    )

    global_evidence = GlobalAlignmentEvidence(
        items=[
            EvidenceItem(
                name="sequence_consistency",
                score=0.95,
                source="sequence_aligner",
            ),
        ],
        confidence=0.94,
    )

    result = AlignmentResult(
        alignments=[alignment_id],
        local_evidence=[local_evidence],
        global_evidence=global_evidence,
    )

    assert result.alignments == [alignment_id]
    assert result.local_evidence[0].confidence == 0.91
    assert result.global_evidence.confidence == 0.94


def test_evidence_score_must_be_between_zero_and_one():
    try:
        EvidenceItem(
            name="invalid",
            score=1.5,
            source="test",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected score validation to fail")
