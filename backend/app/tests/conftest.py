import sys
import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # config 在 import 时固化 DB_PATH, 需清掉已导入的 app* 让其按新 DATA_DIR 重建
    for name in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
        sys.modules.pop(name)
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
