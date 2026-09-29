"""S12: Compliance Radar reminder job.

For every company profile, finds obligations due within
COMPLIANCE_REMINDER_DAYS_AHEAD days that haven't been reminded about yet
(obligation_reminders_sent dedups by user+obligation+period) and emails the
profile's reminder address via Resend. Intended to run once a day (Render
cron, or any scheduler) - safe to re-run any number of times since sending
is guarded by that dedup table, not by the run itself.

    python3 backend/scripts/send_compliance_reminders.py [--dry-run]
"""
from __future__ import annotations

import datetime
import logging
import os
import sys

import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from app import compliance, config, supa  # noqa: E402

log = logging.getLogger("kanooni.compliance_reminders")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _send_email(to: str, subject: str, html: str) -> bool:
    if not config.RESEND_API_KEY:
        log.warning("RESEND_API_KEY not set - skipping send to %s: %s", to, subject)
        return False
    r = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
        json={"from": config.RESEND_FROM_EMAIL, "to": [to], "subject": subject, "html": html},
        timeout=10.0,
    )
    if r.status_code >= 300:
        log.error("Resend send failed (%s) for %s: %s", r.status_code, to, r.text[:300])
        return False
    return True


def _render_email(company_name: str, due: list[dict]) -> tuple[str, str]:
    subject = f"Kanooni Sathi: {len(due)} compliance deadline(s) coming up for {company_name}"
    rows = "".join(
        f"<li><b>{ob['title_en']}</b> - due {ob['due_date_ad']} ({ob['due_date_bs']} B.S.), "
        f"{ob['days_remaining']} day(s) away. <i>{ob['citation']}</i></li>"
        for ob in due
    )
    html = f"<p>Upcoming compliance deadlines for <b>{company_name}</b>:</p><ul>{rows}</ul>"
    return subject, html


def run(dry_run: bool = False) -> int:
    if not supa.available():
        log.warning("Supabase not configured - nothing to do")
        return 0
    profiles = supa.all_company_profiles()
    all_obligations = supa.obligations_list()
    today = datetime.date.today()
    horizon_days = config.COMPLIANCE_REMINDER_DAYS_AHEAD
    sent_count = 0
    for profile in profiles:
        to = profile.get("reminder_email")
        if not to:
            continue
        due_for_profile: list[dict] = []
        for ob in all_obligations:
            if not compliance.applies_to(ob["applies_if"], profile):
                continue
            result = compliance.next_due(ob, today)
            if result is None:
                continue
            period, due_bs = result
            due_ad = compliance.bs_to_ad(due_bs.year, due_bs.month, due_bs.day)
            days_remaining = (due_ad - today).days
            if days_remaining > horizon_days:
                continue
            if supa.reminder_already_sent(profile["user_id"], ob["id"], period):
                continue
            due_for_profile.append({
                "obligation_id": ob["id"], "title_en": ob["title_en"], "citation": ob["citation"],
                "period": period, "due_date_bs": str(due_bs), "due_date_ad": due_ad.isoformat(),
                "days_remaining": days_remaining,
            })
        if not due_for_profile:
            continue
        subject, html = _render_email(profile["company_name"], due_for_profile)
        if dry_run:
            log.info("[dry-run] would email %s: %s", to, subject)
            ok = True
        else:
            ok = _send_email(to, subject, html)
        if ok:
            for ob in due_for_profile:
                if not dry_run:
                    supa.reminder_record_sent(
                        profile["user_id"], ob["obligation_id"], ob["period"],
                        ob["due_date_bs"], ob["due_date_ad"],
                    )
                sent_count += 1
    log.info("compliance reminder job done: %d obligation reminder(s) sent across %d profile(s)",
              sent_count, len(profiles))
    return sent_count


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
