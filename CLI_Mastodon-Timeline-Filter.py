#!/usr/bin/env python3
"""
Mastodon Timeline Filter - Filtere deine Beiträge nach Zeiträumen
"""

import requests
from datetime import datetime
import argparse
import sys
from typing import List, Dict


class MastodonTimelineFilter:
    def __init__(self, instance_url: str, access_token: str):
        """
        Initialisiere den Mastodon Client

        Args:
            instance_url: URL deiner Mastodon-Instanz (z.B. 'https://mastodon.social')
            access_token: Dein Access Token
        """
        self.instance_url = instance_url.rstrip('/')
        self.access_token = access_token
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def get_account_id(self) -> str:
        """Hole die Account-ID des authentifizierten Users"""
        url = f"{self.instance_url}/api/v1/accounts/verify_credentials"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Fehler beim Abrufen der Account-Daten: {response.status_code}")
            sys.exit(1)

        return response.json()['id']

    def get_statuses(self, account_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Hole alle Beiträge im angegebenen Zeitraum

        Args:
            account_id: Die Account-ID
            start_date: Startdatum
            end_date: Enddatum

        Returns:
            Liste von Beiträgen
        """
        url = f"{self.instance_url}/api/v1/accounts/{account_id}/statuses"
        all_statuses = []
        max_id = None

        print(f"Suche Beiträge zwischen {start_date.date()} und {end_date.date()}...")

        while True:
            params = {
                'limit': 40,  # Maximum pro Request
                'exclude_replies': False,
                'exclude_reblogs': True
            }

            if max_id:
                params['max_id'] = max_id

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                print(f"Fehler beim Abrufen der Beiträge: {response.status_code}")
                break

            statuses = response.json()

            if not statuses:
                break

            for status in statuses:
                created_at = datetime.fromisoformat(status['created_at'].replace('Z', '+00:00'))

                # Wenn wir vor dem Startzeitraum sind, können wir aufhören
                if created_at < start_date:
                    return all_statuses

                # Nur Beiträge im Zeitraum hinzufügen
                if start_date <= created_at <= end_date:
                    all_statuses.append(status)

            # Paginierung: nächste Seite mit max_id
            max_id = statuses[-1]['id']
            print(f"  Gefunden: {len(all_statuses)} Beiträge...", end='\r')

        print()  # Neue Zeile nach Progress
        return all_statuses

    def display_status(self, status: Dict, show_content: bool = False):
        """Zeige einen Beitrag formatiert an"""
        created_at = datetime.fromisoformat(status['created_at'].replace('Z', '+00:00'))

        # HTML-Tags aus Content entfernen für bessere Lesbarkeit
        from html import unescape
        import re
        content = unescape(re.sub('<[^<]+?>', '', status['content']))

        # Kürze Content wenn zu lang
        if len(content) > 150 and not show_content:
            content = content[:150] + "..."

        print(f"\n{'=' * 80}")
        print(f"Datum: {created_at.strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"URL: {status['url']}")

        if status.get('tags'):
            tags = [tag['name'] for tag in status['tags']]
            print(f"Hashtags: {', '.join(['#' + tag for tag in tags])}")

        if status.get('media_attachments'):
            print(f"Medien: {len(status['media_attachments'])} Anhang/Anhänge")
            for media in status['media_attachments']:
                print(f"  - {media['type']}: {media['url']}")

        print(f"\nInhalt:\n{content}")


def parse_date(date_string: str) -> datetime:
    """Parse Datum im Format DD.MM.YYYY oder YYYY-MM-DD"""
    for fmt in ['%d.%m.%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Ungültiges Datumsformat: {date_string}. Nutze DD.MM.YYYY oder YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(
        description='Filtere deine Mastodon-Beiträge nach Zeiträumen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --start 01.07.2023 --end 31.07.2023
  %(prog)s --start 2023-07-01 --end 2023-07-31 --full

Erstelle zunächst einen Access Token:
  1. Gehe zu Einstellungen > Entwicklung auf deiner Mastodon-Instanz
  2. Erstelle eine neue Anwendung
  3. Kopiere den Access Token
  4. Setze Umgebungsvariablen:
     export MASTODON_INSTANCE="https://deine-instanz.social"
     export MASTODON_TOKEN="dein-access-token"
        """
    )

    parser.add_argument('--start', required=True, help='Startdatum (DD.MM.YYYY oder YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='Enddatum (DD.MM.YYYY oder YYYY-MM-DD)')
    parser.add_argument('--full', action='store_true', help='Zeige vollständigen Content')
    parser.add_argument('--instance', help='Mastodon-Instanz URL (oder MASTODON_INSTANCE env var)')
    parser.add_argument('--token', help='Access Token (oder MASTODON_TOKEN env var)')

    args = parser.parse_args()

    # Hole Credentials aus args oder Umgebungsvariablen
    import os
    instance = args.instance or os.getenv('MASTODON_INSTANCE')
    token = args.token or os.getenv('MASTODON_TOKEN')

    if not instance or not token:
        print("Fehler: Mastodon-Instanz und Access Token erforderlich!")
        print("Setze --instance und --token oder die Umgebungsvariablen MASTODON_INSTANCE und MASTODON_TOKEN")
        sys.exit(1)

    try:
        from datetime import timezone

        start_date = parse_date(args.start)
        end_date = parse_date(args.end)

        # Setze Uhrzeit für den ganzen Tag und füge UTC Timezone hinzu
        start_date = start_date.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
        end_date = end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)

        if start_date > end_date:
            print("Fehler: Startdatum muss vor Enddatum liegen!")
            sys.exit(1)

    except ValueError as e:
        print(f"Fehler: {e}")
        sys.exit(1)

    # Initialisiere Client und hole Beiträge
    client = MastodonTimelineFilter(instance, token)
    account_id = client.get_account_id()
    statuses = client.get_statuses(account_id, start_date, end_date)

    print(f"\n{'=' * 80}")
    print(f"Gefundene Beiträge: {len(statuses)}")
    print(f"{'=' * 80}")

    for status in statuses:
        client.display_status(status, show_content=args.full)

    print(f"\n{'=' * 80}")
    print(f"Insgesamt {len(statuses)} Beiträge im Zeitraum gefunden.")


if __name__ == '__main__':
    main()