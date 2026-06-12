import hashlib
import json
import secrets
import sys
from datetime import datetime, timedelta, timezone


def make_license_key():
    return "PW-" + secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:22].upper()


def license_hash(license_key):
    return hashlib.sha256(license_key.encode("utf-8")).hexdigest()


def main():
    customer = sys.argv[1] if len(sys.argv) > 1 else "New Customer"
    plan = sys.argv[2] if len(sys.argv) > 2 else "starter"
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 365
    license_key = make_license_key()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()

    record = {
        license_hash(license_key): {
            "customer": customer,
            "plan": plan,
            "status": "active",
            "expires_at": expires_at,
            "features": ["license.verify", "recommend.rank", "mentor.match"],
        }
    }

    print("LICENSE_KEY=" + license_key)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
