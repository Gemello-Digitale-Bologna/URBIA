import os
import base64
import pytest
from dotenv import load_dotenv

from backend.modal_runtime.functions import app
from backend.modal_runtime.session import volume_name

def _have_modal_tokens() -> bool:
    load_dotenv()
    return bool(os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"))

@app.local_entrypoint()
@pytest.mark.skipif(not _have_modal_tokens(), reason="Modal tokens not configured; skipping Modal integration tests")
def test_dataset_functions_flow_write_list_then_optional_export():

    from backend.modal_runtime.functions import write_dataset_bytes, list_loaded_datasets #, export_dataset

    # Prepare a tiny CSV
    csv_data = b"a,b\n1,2\n3,4\n"
    b64 = base64.b64encode(csv_data).decode("ascii")


    print("Running in sandbox")
    print("volume name:", volume_name())
    
    # 1) Write into sandbox under /workspace/datasets/unit.csv
    res = write_dataset_bytes.remote(dataset_id="unit", data_b64=b64, ext="csv")
    assert res["dataset_id"] == "unit"
    assert res["rel_path"].endswith("datasets/unit.csv")
    assert res.get("columns") == ["a", "b"]
    assert res.get("shape") == [2, 2]

    # 2) List datasets should include our file
    files = list_loaded_datasets.remote()
    names = {f.get("path") for f in files}
    assert "unit.csv" in names

    '''# 3) Optionally export to S3 if creds and bucket are configured
    have_s3 = bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY") and os.getenv("S3_BUCKET"))
    if have_s3:
        uploaded = export_dataset.remote("datasets/unit.csv", bucket=os.environ["S3_BUCKET"])
        assert uploaded.get("s3_key") and uploaded.get("s3_url")'''
