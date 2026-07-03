from pathlib import Path

from hermes_agent import HermesControlPlane


def test_plan_app_creates_manifest(tmp_path: Path):
    control = HermesControlPlane(repo_root=tmp_path)
    manifest = control.plan_app("A quote app for painting contractors")
    assert manifest.app_name == "PainterQuote Pro"
    assert manifest.crews
    assert any(entity.name == "Estimate" for entity in manifest.entities)


def test_scaffold_crew_writes_contract_files(tmp_path: Path):
    (tmp_path / "crews" / "generated").mkdir(parents=True)
    control = HermesControlPlane(repo_root=tmp_path)
    manifest = control.create_crew_blueprint("Lead intake crew")
    paths = control.scaffold_crew(manifest)
    assert f"crews/generated/{manifest.id}/manifest.json" in paths
    assert (tmp_path / "crews" / "generated" / manifest.id / "crew.py").exists()
