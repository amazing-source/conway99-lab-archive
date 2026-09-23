#!/usr/bin/env python3
"""Collect the frozen Wave 26 literature queries from reproducible public APIs.

The script preserves exact response bytes for transient inspection and writes
a parsed index. Those bulk files were deliberately omitted from the published
audit package after deriving ``query-ledger.json``. This is a discovery aid,
not a relevance classifier or novelty certificate.
"""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


QUERIES = [
    ("Q01", '"srg(99,14,1,2)" lattice'),
    ("Q02", '"srg(99,14,1,2)" projector'),
    ("Q03", '"strongly regular graph" "99,14,1,2" lattice'),
    ("Q04", '"n3 = 708" lattice'),
    ("Q05", '"231-row" projector lattice'),
    ("Q06", '"231 rows" projector Gram lattice'),
    ("Q07", '"E8^5" "A2^2"'),
    ("Q08", '"E_8^5" "A_2^2"'),
    ("Q09", '"orthogonal A2 summand" lattice'),
    ("Q10", '"A2 summand" projector lattice'),
    ("Q11", '"A_2" "orthogonal summand" even lattice'),
    ("Q12", '"integral tight frame" lattice projector'),
    ("Q13", '"integer tight frame" Gram projector'),
    ("Q14", '"finite unit norm tight frame" integral Gram matrix'),
    ("Q15", '"rational tight frame" lattice Gram matrix'),
    ("Q16", '"projector Gram matrix" lattice'),
    ("Q17", '"idempotent Gram matrix" tight frame lattice'),
    ("Q18", "eutaxy lattice spherical 2-design Gram matrix"),
    ("Q19", '"strongly eutactic" lattice root system A2'),
    ("Q20", '"spherical 2-design" lattice projector'),
    ("Q21", '"spherical 3-design" lattice moment obstruction'),
    ("Q22", '"spherical design" "A2" lattice eutaxy'),
    ("Q23", '"Schur complement" Gram matrix moment identity'),
    ("Q24", '"Schur complement" tight frame projector'),
    ("Q25", '"Schur complement" lattice projector'),
    ("Q26", '"moment identity" projector Gram matrix'),
    ("Q27", '"root lattice A2" tight frame'),
    ("Q28", '"orthogonal direct summand" A2 lattice design'),
]

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw-search-results"
USER_AGENT = (
    "Wave26LiteratureAudit/1.0 "
    "(independent bibliographic research; contact unavailable)"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def request_bytes(url: str, timeout: int = 90) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, application/atom+xml, text/html;q=0.9, */*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return (
                int(response.status),
                response.read(),
                {k.lower(): v for k, v in response.headers.items()},
            )
    except urllib.error.HTTPError as exc:
        return (
            int(exc.code),
            exc.read(),
            {k.lower(): v for k, v in exc.headers.items()},
        )


def write_raw(service: str, query_id: str, suffix: str, body: bytes) -> Path:
    directory = RAW / service
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{query_id}.{suffix}"
    path.write_bytes(body)
    return path


def base_record(
    service: str,
    query_id: str,
    query: str,
    url: str,
    status: int,
    body: bytes,
    path: Path,
    started: str,
    finished: str,
) -> dict[str, Any]:
    return {
        "service": service,
        "query_id": query_id,
        "query": query,
        "url": url,
        "started_utc": started,
        "finished_utc": finished,
        "http_status": status,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "raw_path": path.relative_to(ROOT).as_posix(),
    }


def fetch_crossref(query_id: str, query: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(query, safe="")
    url = (
        "https://api.crossref.org/works"
        f"?query.bibliographic={encoded}&rows=20"
        "&select=DOI,title,author,published,type,URL,container-title,score"
    )
    started = utc_now()
    status, body, _ = request_bytes(url)
    finished = utc_now()
    path = write_raw("crossref", query_id, "json", body)
    record = base_record(
        "Crossref Works API",
        query_id,
        query,
        url,
        status,
        body,
        path,
        started,
        finished,
    )
    try:
        payload = json.loads(body)
        message = payload.get("message", {})
        items = message.get("items", [])
        record["total_results"] = message.get("total-results")
        record["returned_results"] = len(items)
        record["results"] = [
            {
                "title": (item.get("title") or [None])[0],
                "doi": item.get("DOI"),
                "url": item.get("URL"),
                "type": item.get("type"),
                "score": item.get("score"),
            }
            for item in items
        ]
    except Exception as exc:  # noqa: BLE001 - retained in audit output
        record["parse_error"] = f"{type(exc).__name__}: {exc}"
    return record


def fetch_openalex(query_id: str, query: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(query, safe="")
    fields = (
        "id,doi,title,display_name,publication_year,type,primary_location,"
        "authorships,cited_by_count,relevance_score"
    )
    url = (
        "https://api.openalex.org/works"
        f"?search={encoded}&per-page=20&select={fields}"
    )
    started = utc_now()
    status, body, _ = request_bytes(url)
    finished = utc_now()
    path = write_raw("openalex", query_id, "json", body)
    record = base_record(
        "OpenAlex Works API",
        query_id,
        query,
        url,
        status,
        body,
        path,
        started,
        finished,
    )
    try:
        payload = json.loads(body)
        items = payload.get("results", [])
        record["total_results"] = (payload.get("meta") or {}).get("count")
        record["returned_results"] = len(items)
        record["results"] = [
            {
                "title": item.get("display_name") or item.get("title"),
                "doi": item.get("doi"),
                "url": item.get("id"),
                "year": item.get("publication_year"),
                "type": item.get("type"),
                "relevance_score": item.get("relevance_score"),
            }
            for item in items
        ]
    except Exception as exc:  # noqa: BLE001
        record["parse_error"] = f"{type(exc).__name__}: {exc}"
    return record


def _zb_identifier(item: dict[str, Any]) -> tuple[str | None, str | None]:
    doi = None
    arxiv = None
    identifier = item.get("identifier")
    if isinstance(identifier, dict):
        doi_value = identifier.get("doi")
        arxiv_value = identifier.get("arxiv")
        if isinstance(doi_value, list):
            doi = doi_value[0] if doi_value else None
        else:
            doi = doi_value
        if isinstance(arxiv_value, list):
            arxiv = arxiv_value[0] if arxiv_value else None
        else:
            arxiv = arxiv_value
    return doi, arxiv


def fetch_zbmath(query_id: str, query: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(query, safe="")
    url = (
        "https://api.zbmath.org/v1/document/_search"
        f"?search_string={encoded}&page=0&results_per_page=20"
    )
    started = utc_now()
    status, body, _ = request_bytes(url)
    finished = utc_now()
    path = write_raw("zbmath", query_id, "json", body)
    record = base_record(
        "zbMATH Open REST API",
        query_id,
        query,
        url,
        status,
        body,
        path,
        started,
        finished,
    )
    try:
        payload = json.loads(body)
        items = payload.get("result") or []
        status_data = payload.get("status") or {}
        record["total_results"] = status_data.get("nr_total_results")
        record["returned_results"] = len(items)
        results = []
        for item in items:
            doi, arxiv = _zb_identifier(item)
            results.append(
                {
                    "title": item.get("title"),
                    "doi": doi,
                    "arxiv": arxiv,
                    "url": item.get("zbmath_url"),
                    "year": item.get("year"),
                    "zbl_id": item.get("id"),
                }
            )
        record["results"] = results
        if status == 404 and status_data.get("internal_code") == (
            "successful access. No results found."
        ):
            record["total_results"] = 0
            record["returned_results"] = 0
    except Exception as exc:  # noqa: BLE001
        record["parse_error"] = f"{type(exc).__name__}: {exc}"
    return record


def fetch_arxiv(query_id: str, query: str) -> dict[str, Any]:
    service_query = f"all:{query}"
    encoded = urllib.parse.quote(service_query, safe="")
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query={encoded}&start=0&max_results=20"
        "&sortBy=relevance&sortOrder=descending"
    )
    started = utc_now()
    status, body, _ = request_bytes(url)
    finished = utc_now()
    path = write_raw("arxiv", query_id, "xml", body)
    record = base_record(
        "arXiv API",
        query_id,
        query,
        url,
        status,
        body,
        path,
        started,
        finished,
    )
    record["service_query"] = service_query
    try:
        root = ET.fromstring(body)
        atom = "{http://www.w3.org/2005/Atom}"
        opensearch = "{http://a9.com/-/spec/opensearch/1.1/}"
        total_element = root.find(f"{opensearch}totalResults")
        entries = root.findall(f"{atom}entry")
        record["total_results"] = (
            int(total_element.text) if total_element is not None else None
        )
        record["returned_results"] = len(entries)
        record["results"] = [
            {
                "title": " ".join(
                    (entry.findtext(f"{atom}title") or "").split()
                ),
                "url": entry.findtext(f"{atom}id"),
                "published": entry.findtext(f"{atom}published"),
                "authors": [
                    author.findtext(f"{atom}name")
                    for author in entry.findall(f"{atom}author")
                ],
            }
            for entry in entries
        ]
    except Exception as exc:  # noqa: BLE001
        record["parse_error"] = f"{type(exc).__name__}: {exc}"
    return record


RESULT_LINK_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def fetch_duckduckgo(query_id: str, query: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(query, safe="")
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    started = utc_now()
    status, body, _ = request_bytes(url)
    finished = utc_now()
    path = write_raw("duckduckgo", query_id, "html", body)
    record = base_record(
        "DuckDuckGo HTML",
        query_id,
        query,
        url,
        status,
        body,
        path,
        started,
        finished,
    )
    try:
        page = body.decode("utf-8", errors="replace")
        results = []
        for href, title_markup in RESULT_LINK_RE.findall(page):
            href = html.unescape(href)
            parsed = urllib.parse.urlparse(href)
            parameters = urllib.parse.parse_qs(parsed.query)
            target = parameters.get("uddg", [href])[0]
            title = html.unescape(TAG_RE.sub("", title_markup)).strip()
            results.append({"title": " ".join(title.split()), "url": target})
        record["returned_results"] = len(results)
        record["total_results"] = None
        record["results"] = results
        record["explicit_no_results"] = "No results found for" in page
    except Exception as exc:  # noqa: BLE001
        record["parse_error"] = f"{type(exc).__name__}: {exc}"
    return record


def run_service(
    name: str,
    fetcher: Callable[[str, str], dict[str, Any]],
    delay_seconds: float,
) -> list[dict[str, Any]]:
    records = []
    for index, (query_id, query) in enumerate(QUERIES):
        try:
            records.append(fetcher(query_id, query))
        except Exception as exc:  # noqa: BLE001
            records.append(
                {
                    "service": name,
                    "query_id": query_id,
                    "query": query,
                    "started_utc": utc_now(),
                    "finished_utc": utc_now(),
                    "fatal_error": f"{type(exc).__name__}: {exc}",
                }
            )
        if delay_seconds and index + 1 < len(QUERIES):
            time.sleep(delay_seconds)
    return records


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    services = [
        ("Crossref Works API", fetch_crossref, 0.15),
        ("OpenAlex Works API", fetch_openalex, 0.15),
        ("zbMATH Open REST API", fetch_zbmath, 0.15),
        ("arXiv API", fetch_arxiv, 3.1),
        ("DuckDuckGo HTML", fetch_duckduckgo, 1.25),
    ]
    all_records: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
        futures = {
            executor.submit(run_service, name, fetcher, delay): name
            for name, fetcher, delay in services
        }
        for future in concurrent.futures.as_completed(futures):
            all_records.extend(future.result())
    order = {query_id: index for index, (query_id, _) in enumerate(QUERIES)}
    service_order = {service[0]: index for index, service in enumerate(services)}
    all_records.sort(
        key=lambda record: (
            order.get(record.get("query_id"), 999),
            service_order.get(record.get("service"), 999),
        )
    )
    payload = {
        "schema": "wave26-literature-api-query-results-v1",
        "started_utc": started,
        "finished_utc": utc_now(),
        "query_count": len(QUERIES),
        "services": [service[0] for service in services],
        "service_limits": {
            "Crossref Works API": "first 20 records by API relevance",
            "OpenAlex Works API": "first 20 records by API relevance",
            "zbMATH Open REST API": "first 20 records returned by one-line search",
            "arXiv API": "first 20 records sorted by relevance",
            "DuckDuckGo HTML": "first HTML results page returned",
        },
        "interpretation": (
            "Search responses are discovery evidence only. Zero or irrelevant "
            "results do not prove nonexistence or novelty."
        ),
        "queries": [{"query_id": qid, "query": query} for qid, query in QUERIES],
        "records": all_records,
    }
    output = ROOT / "api-query-results.json"
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": output.relative_to(ROOT).as_posix(),
                "records": len(all_records),
                "started_utc": payload["started_utc"],
                "finished_utc": payload["finished_utc"],
                "fatal_errors": sum(
                    1 for record in all_records if "fatal_error" in record
                ),
                "parse_errors": sum(
                    1 for record in all_records if "parse_error" in record
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
