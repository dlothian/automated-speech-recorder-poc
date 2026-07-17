#!/usr/bin/env python3

import json
import os
from datetime import datetime, timezone

import requests
import yaml


LIMITS_FILE = "ops/cloudflare_limits.yaml"

API_BASE = "https://api.cloudflare.com/client/v4"
GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

def get_account_id():
    account_id = os.getenv(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    if not account_id:
        raise RuntimeError(
            "Missing CLOUDFLARE_ACCOUNT_ID"
        )

    return account_id


def headers():
    token = os.getenv(
        "CLOUDFLARE_API_TOKEN"
    )

    if not token:
        raise RuntimeError(
            "Missing CLOUDFLARE_API_TOKEN"
        )

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------
# API helpers
# ---------------------------------------------------------

def api_get(path):

    response = requests.get(
        API_BASE + path,
        headers=headers(),
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not result["success"]:
        raise RuntimeError(result)

    return result["result"]


def graphql(query, variables):

    response = requests.post(
        GRAPHQL_URL,
        headers=headers(),
        json={
            "query": query,
            "variables": variables,
        },
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise RuntimeError(result["errors"])

    return result["data"]


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

def load_config():

    with open(LIMITS_FILE) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------
# Pages
# ---------------------------------------------------------

def pages_usage(account_id):

    projects = api_get(
        f"/accounts/{account_id}/pages/projects"
    )

    now = datetime.now(timezone.utc)

    month_start = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc,
    )

    total = 0

    project_details = []

    for project in projects:

        name = project["name"]

        deployments = api_get(
            f"/accounts/{account_id}/pages/projects/"
            f"{name}/deployments"
        )

        count = 0

        for deployment in deployments:

            created = deployment.get(
                "created_on"
            )

            if not created:
                continue

            created_date = datetime.fromisoformat(
                created.replace(
                    "Z",
                    "+00:00"
                )
            )

            if created_date >= month_start:
                count += 1

        total += count

        project_details.append(
            {
                "name": name,
                "builds": count,
            }
        )

    return {
        "builds": total,
        "projects": project_details,
    }


# ---------------------------------------------------------
# Workers Analytics
# ---------------------------------------------------------

def workers_usage(account_id):

    query = """
    query($account_id: string!, $datetimeStart: Time!, $datetimeEnd: Time!) {
      viewer {
        accounts(filter: {accountTag: $account_id}) {
          workersInvocationsAdaptive(
            limit: 1000,
            filter: {
              datetime_geq: $datetimeStart,
              datetime_leq: $datetimeEnd
            }
          ) {
            sum {
              requests
            }
            quantiles {
              cpuTimeP50
            }
          }
        }
      }
    }
    """

    now = datetime.now(timezone.utc)

    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    data = graphql(
        query,
        {
            "accountTag": account_id,
            "datetimeStart": start.isoformat(),
            "datetimeEnd": now.isoformat(),
        },
    )

    account = data["viewer"]["accounts"][0]

    rows = account["workersInvocationsAdaptive"]

    total_requests = 0
    estimated_cpu_ms = 0

    for row in rows:

        requests = (
            row.get("sum", {})
            .get("requests", 0)
            or 0
        )

        cpu_p50 = (
            row.get("quantiles", {})
            .get("cpuTimeP50", 0)
            or 0
        )

        total_requests += requests

        estimated_cpu_ms += (
            requests * cpu_p50
        )

    return {
        "requests": total_requests,
        "cpu_ms": estimated_cpu_ms,
        "cpu_estimate_method": "P50 CPU time × requests",
    }


# ---------------------------------------------------------
# D1 Analytics
# ---------------------------------------------------------

def d1_usage(account_id):

    databases = api_get(
        f"/accounts/{account_id}/d1/database"
    )

    # D1 analytics currently varies by account.
    # Keep discovery separate from metrics.

    return {
        "databases": [
            db["name"]
            for db in databases
        ],
        "count": len(databases),
        "reads": 0,
        "writes": 0,
        "storage_gb": 0,
    }


# ---------------------------------------------------------
# R2
# ---------------------------------------------------------

def r2_usage(account_id):

    buckets = api_get(
        f"/accounts/{account_id}/r2/buckets"
    )

    return {
        "buckets": [
            bucket["name"]
            for bucket in buckets
        ],
        "count": len(buckets),
        "storage_gb": 0,
        "class_a": 0,
        "class_b": 0,
    }


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

def pct(value, limit):

    if limit == 0:
        return 0

    return round(
        value / limit * 100,
        1,
    )


def warning(value, limit, threshold):

    return pct(value, limit) >= threshold


def generate_report(config, usage):

    filename = (
        config["monitoring"]
        ["report"]
        ["filename"]
    )

    limits = config["cloudflare"]

    lines = []

    lines.append(
        "# Cloudflare Usage Report\n"
    )

    lines.append(
        datetime.now(timezone.utc)
        .isoformat()
    )

    # Pages

    page_limit = (
        limits["pages"]
        ["builds"]
        ["monthly_limit"]
    )

    lines.append(
        "\n## Pages"
    )

    lines.append(
        f"\nBuilds: "
        f"{usage['pages']['builds']}/"
        f"{page_limit}"
    )

    # Workers

    worker_limit = (
        limits["workers"]
        ["requests"]
        ["daily_limit"]
    )

    lines.append(
        "\n\n## Workers"
    )

    lines.append(
        f"\nRequests: "
        f"{usage['workers']['requests']}/"
        f"{worker_limit}"
    )

    lines.append(
        f"\nCPU ms: "
        f"{usage['workers']['cpu_ms']}"
    )

    lines.append(
        f"\nEstimation Method: "
        f"{usage['workers']['cpu_estimate_method']}"
    )


    # D1

    lines.append(
        "\n\n## D1"
    )

    lines.append(
        f"\nDatabases: "
        f"{usage['d1']['count']}"
    )

    lines.append(
        f"\nReads: "
        f"{usage['d1']['reads']}"
    )

    lines.append(
        f"\nWrites: "
        f"{usage['d1']['writes']}"
    )

    # R2

    lines.append(
        "\n\n## R2"
    )

    lines.append(
        f"\nBuckets: "
        f"{usage['r2']['count']}"
    )

    lines.append(
        f"\nStorage GB: "
        f"{usage['r2']['storage_gb']}"
    )

    lines.append(
        f"\nClass A: "
        f"{usage['r2']['class_a']}"
    )

    lines.append(
        f"\nClass B: "
        f"{usage['r2']['class_b']}"
    )

    with open(filename, "w") as f:
        f.write(
            "\n".join(lines)
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    account_id = get_account_id()

    config = load_config()

    usage = {}

    print("Pages...")
    usage["pages"] = pages_usage(
        account_id
    )

    print("Workers...")
    usage["workers"] = workers_usage(
        account_id
    )

    print("D1...")
    usage["d1"] = d1_usage(
        account_id
    )

    print("R2...")
    usage["r2"] = r2_usage(
        account_id
    )

    generate_report(
        config,
        usage,
    )


if __name__ == "__main__":
    main()
