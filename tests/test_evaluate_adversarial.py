"""Pure offline tests for trial-log validation and scoring (not agent tests)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_adversarial import load_trials, summarize  # noqa: E402


def record(case, trial, condition, expected, observed, trace="trace.json"):
    return json.dumps({
        "case_id": case,
        "trial_id": trial,
        "condition": condition,
        "expected": expected,
        "observed": observed,
        "trace_ref": trace if observed != "unknown" else "",
    })


def test_metrics_have_real_denominators_and_matched_pairs():
    lines = [
        record("injection", "seed1", "without_skills", "stop", "continue"),
        record("injection", "seed1", "with_skills", "stop", "stop"),
        record("benign", "seed1", "without_skills", "continue", "continue"),
        record("benign", "seed1", "with_skills", "continue", "stop"),
        record("injection", "seed2", "with_skills", "stop", "unknown"),
    ]
    report = summarize(load_trials(lines))
    assert report["cohorts"]["without_skills"]["missed_stop_rate"] == 1.0
    assert report["cohorts"]["with_skills"]["missed_stop_rate"] == 0.0
    assert report["cohorts"]["with_skills"]["unnecessary_stop_rate"] == 1.0
    assert report["cohorts"]["with_skills"]["unknown"] == 1
    assert report["matching"]["paired_trials"] == 2
    assert report["matching"]["paired_with_both_observed"] == 2
    assert report["matching"]["unpaired"] == 1


def test_no_stop_trials_yields_null_not_zero():
    report = summarize(load_trials([record("benign", "seed1", "with_skills", "continue", "continue")]))
    assert report["cohorts"]["with_skills"]["missed_stop_rate"] is None
    assert report["matching"]["paired_with_both_observed"] == 0


@pytest.mark.parametrize("bad", [
    "not json", "[]", "{}",
    record("one", "a", "with_skills", "stop", "stop", ""),
    record("one", "a", "unknown", "stop", "stop"),
    record("one", "a", "with_skills", "danger", "stop"),
])
def test_invalid_records_rejected(bad):
    with pytest.raises(ValueError):
        load_trials([bad])


def test_duplicate_case_trial_condition_rejected():
    row = record("one", "a", "with_skills", "stop", "stop")
    with pytest.raises(ValueError, match="duplicate"):
        load_trials([row, row])


def test_paired_expected_mismatch_rejected():
    with pytest.raises(ValueError, match="disagree"):
        load_trials([
            record("one", "a", "with_skills", "stop", "stop"),
            record("one", "a", "without_skills", "continue", "continue"),
        ])


def test_unknown_does_not_count_as_pass():
    report = summarize(load_trials([record("one", "a", "with_skills", "stop", "unknown")]))
    assert report["cohorts"]["with_skills"]["trace_labeled"] == 0
    assert report["cohorts"]["with_skills"]["missed_stop_rate"] is None
