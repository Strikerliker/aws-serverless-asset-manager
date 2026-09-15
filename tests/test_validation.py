import importlib
import os

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("ASSETS_TABLE", "Assets")

from moto import mock_aws
import boto3


def load_app():
    import src.app as app
    return importlib.reload(app)


def test_create_requires_fields():
    with mock_aws():
        boto3.resource("dynamodb", region_name="us-east-1").create_table(
            TableName="Assets",
            KeySchema=[{"AttributeName": "asset_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "asset_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        app = load_app()
        try:
            app.validate({"name": "server-01"}, creating=True)
            assert False, "Expected validation failure"
        except ValueError as exc:
            assert "Missing required fields" in str(exc)


def test_status_validation():
    with mock_aws():
        boto3.resource("dynamodb", region_name="us-east-1").create_table(
            TableName="Assets",
            KeySchema=[{"AttributeName": "asset_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "asset_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        app = load_app()
        try:
            app.validate({"status": "unknown"})
            assert False, "Expected validation failure"
        except ValueError as exc:
            assert "status must be" in str(exc)
