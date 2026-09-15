# AWS Serverless Asset Manager

A production-style serverless CRUD application for managing cloud and IT assets using AWS Lambda, Amazon API Gateway, Amazon DynamoDB, and Python.

## What this project demonstrates

- Full Create, Read, Update, Delete (CRUD) REST API
- Serverless AWS application architecture
- DynamoDB data modeling
- Input validation and consistent API responses
- Least-privilege IAM through AWS SAM
- CloudWatch-ready structured logging
- Automated testing and GitHub Actions CI
- Infrastructure as code

## Architecture

```text
Web UI / API Client
        |
        v
Amazon API Gateway
        |
        v
AWS Lambda (Python)
        |
        v
Amazon DynamoDB

Lambda -> Amazon CloudWatch logs
```

## Asset model

Each asset contains fields such as `asset_id`, `name`, `asset_type`, `environment`, `owner`, `status`, `hostname`, `created_at`, and `updated_at`.

## API

| Method | Route | Operation |
|---|---|---|
| POST | `/assets` | Create asset |
| GET | `/assets` | List assets |
| GET | `/assets/{asset_id}` | Get asset |
| PUT | `/assets/{asset_id}` | Update asset |
| DELETE | `/assets/{asset_id}` | Delete asset |

## Deployment target

The project is designed for deployment with AWS SAM. AWS resources are not claimed as deployed until account-side deployment and configuration are completed.

## Portfolio goal

This project demonstrates end-to-end AWS application engineering: API design, Lambda development, NoSQL persistence, security, observability, automated testing, and infrastructure as code.
