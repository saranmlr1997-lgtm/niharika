import json
import os
import re
import sqlite3
from contextlib import contextmanager


def tenant_slug_from_text(value):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return slug or "tenant"


class SaaSStore:
    def __init__(self, base_dir):
        self.db_path = os.path.join(base_dir, "niharika_saas.db")
        self._initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS businesses (
                    email TEXT PRIMARY KEY,
                    tenant_slug TEXT NOT NULL,
                    business_name TEXT NOT NULL,
                    license_key TEXT,
                    license_hash TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    data_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    tenant_slug TEXT NOT NULL,
                    business_email TEXT,
                    created_at TEXT,
                    status TEXT,
                    data_json TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_businesses_tenant ON businesses(tenant_slug)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_leads_tenant ON leads(tenant_slug)")

    def load_businesses(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT data_json FROM businesses ORDER BY created_at DESC, email ASC").fetchall()
        businesses = {}
        for row in rows:
            business = json.loads(row["data_json"])
            businesses[business["email"]] = business
        return businesses

    def save_businesses(self, businesses):
        with self.connect() as connection:
            connection.execute("DELETE FROM businesses")
            for business in businesses.values():
                tenant_slug = business.get("tenant_slug") or tenant_slug_from_text(business.get("business_name") or business.get("email"))
                payload = dict(business)
                payload["tenant_slug"] = tenant_slug
                connection.execute(
                    """
                    INSERT INTO businesses (email, tenant_slug, business_name, license_key, license_hash, created_at, updated_at, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.get("email"),
                        tenant_slug,
                        payload.get("business_name", ""),
                        payload.get("license_key"),
                        payload.get("license_hash"),
                        payload.get("created_at"),
                        payload.get("updated_at"),
                        json.dumps(payload),
                    ),
                )

    def load_leads(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT data_json FROM leads ORDER BY created_at DESC, id DESC").fetchall()
        return [json.loads(row["data_json"]) for row in rows]

    def save_leads(self, leads):
        with self.connect() as connection:
            connection.execute("DELETE FROM leads")
            for lead in leads:
                tenant_slug = lead.get("tenant_slug") or "public"
                payload = dict(lead)
                payload["tenant_slug"] = tenant_slug
                connection.execute(
                    """
                    INSERT INTO leads (id, tenant_slug, business_email, created_at, status, data_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.get("id"),
                        tenant_slug,
                        payload.get("business_email"),
                        payload.get("created_at"),
                        payload.get("status"),
                        json.dumps(payload),
                    ),
                )

    def tenant_summary(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT tenant_slug, COUNT(*) AS business_count
                FROM businesses
                GROUP BY tenant_slug
                ORDER BY tenant_slug ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]
