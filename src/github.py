import httpx
from typing import Optional, Dict, Any
from .config import settings

BASE_URL = "https://api.github.com/repos/{owner}/{repo}"

async def fetch_github_data(url: str, token: Optional[str] = None) -> Dict[str, Any]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_github_metric(owner: str, repo: str, metric: str) -> str:
    token = settings.GITHUB_TOKEN
    repo_url = BASE_URL.format(owner=owner, repo=repo)

    if metric in ["stars", "forks", "watchers", "open_issues", "size"]:
        data = await fetch_github_data(repo_url, token)
        if metric == "watchers":
            return str(data.get("subscribers_count", 0))
        return str(data.get(metric, 0))

    elif metric == "open_prs":
        pr_url = f"{repo_url}/pulls?state=open"
        data = await fetch_github_data(pr_url, token)
        return str(len(data))

    elif metric == "last_commit":
        commits_url = f"{repo_url}/commits?per_page=1"
        data = await fetch_github_data(commits_url, token)
        if data:
            date = data[0]["commit"]["committer"]["date"]
            return date.split("T")[0]  # YYYY-MM-DD
        return "unknown"

    elif metric == "contributors":
        contrib_url = f"{repo_url}/contributors?per_page=1"
        data = await fetch_github_data(contrib_url, token)
        # GitHub API doesn't give total count directly, this is approximate
        return str(len(data)) if data else "0"

    elif metric == "release":
        releases_url = f"{repo_url}/releases/latest"
        try:
            data = await fetch_github_data(releases_url, token)
            return data.get("tag_name", "none")
        except httpx.HTTPStatusError:
            return "none"

    elif metric == "license":
        data = await fetch_github_data(repo_url, token)
        license_info = data.get("license")
        return license_info.get("spdx_id", "none") if license_info else "none"

    elif metric == "ci_status":
        actions_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=1"
        try:
            data = await fetch_github_data(actions_url, token)
            if data["workflow_runs"]:
                status = data["workflow_runs"][0]["conclusion"]
                return status if status else "unknown"
            return "no_runs"
        except httpx.HTTPStatusError:
            return "unknown"

    else:
        raise ValueError(f"Unknown metric: {metric}")