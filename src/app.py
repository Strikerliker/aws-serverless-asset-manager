import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table = boto3.resource("dynamodb").Table(os.environ.get("ASSETS_TABLE", "Assets"))
ALLOWED_FIELDS = {"name", "asset_type", "environment", "owner", "status", "hostname"}
REQUIRED_FIELDS = {"name", "asset_type", "environment", "status"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def parse_body(event):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must be valid JSON") from exc
    if not isinstance(body, dict):
        raise ValueError("Request body must be a JSON object")
    return body


def validate(body, creating=False):
    unknown = set(body) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"Unsupported fields: {', '.join(sorted(unknown))}")
    if creating:
        missing = [field for field in REQUIRED_FIELDS if not body.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
    if "status" in body and body["status"] not in {"active", "inactive", "maintenance", "retired"}:
        raise ValueError("status must be active, inactive, maintenance, or retired")


def create_asset(event):
    body = parse_body(event)
    validate(body, creating=True)
    timestamp = now_iso()
    item = {"asset_id": str(uuid.uuid4()), **body, "created_at": timestamp, "updated_at": timestamp}
    table.put_item(Item=item, ConditionExpression="attribute_not_exists(asset_id)")
    return response(201, item)


def list_assets():
    result = table.scan()
    return response(200, {"items": result.get("Items", []), "count": result.get("Count", 0)})


def get_asset(asset_id):
    item = table.get_item(Key={"asset_id": asset_id}).get("Item")
    if not item:
        return response(404, {"message": "Asset not found"})
    return response(200, item)


def update_asset(event, asset_id):
    body = parse_body(event)
    validate(body)
    if not body:
        raise ValueError("At least one field is required")
    existing = table.get_item(Key={"asset_id": asset_id}).get("Item")
    if not existing:
        return response(404, {"message": "Asset not found"})
    updated = {**existing, **body, "updated_at": now_iso()}
    table.put_item(Item=updated)
    return response(200, updated)


def delete_asset(asset_id):
    result = table.delete_item(Key={"asset_id": asset_id}, ReturnValues="ALL_OLD")
    if not result.get("Attributes"):
        return response(404, {"message": "Asset not found"})
    return response(200, {"message": "Asset deleted", "asset_id": asset_id})


def lambda_handler(event, context):
    request_id = getattr(context, "aws_request_id", "local")
    method = event.get("requestContext", {}).get("http", {}).get("method", event.get("httpMethod", ""))
    asset_id = (event.get("pathParameters") or {}).get("asset_id")
    logger.info(json.dumps({"event": "asset_request", "request_id": request_id, "method": method, "asset_id": asset_id}))
    try:
        if method == "POST":
            return create_asset(event)
        if method == "GET" and asset_id:
            return get_asset(asset_id)
        if method == "GET":
            return list_assets()
        if method in {"PUT", "PATCH"} and asset_id:
            return update_asset(event, asset_id)
        if method == "DELETE" and asset_id:
            return delete_asset(asset_id)
        return response(405, {"message": "Method not allowed"})
    except ValueError as exc:
        return response(400, {"message": str(exc)})
    except Exception:
        logger.exception("Unhandled asset manager error")
        return response(500, {"message": "Internal server error"})
