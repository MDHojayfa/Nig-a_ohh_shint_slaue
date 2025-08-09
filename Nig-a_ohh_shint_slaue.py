#!/usr/bin/env python3
"""
Nig-a_ohh_shint_slaue: The Ultimate cross-platform OSINT toolkit.
Made By @MDHojayfa - Enhanced with advanced features for 2025

Features:
- Modular platform fetchers: Instagram, Twitter, Facebook, Reddit
- Google Dorking and HaveIBeenPwned email checking (placeholder)
- EXIF geolocation extraction from images
- NLP sentiment analysis and expanded text analytics
- Tor integration for anonymity
- Multi-threaded fetching with progress bars
- JSON report saving with option for full output
- Extended with:
  * Rate-limiting, retry with exponential backoff
  * Basic cache to avoid redundant queries per run
  * Better prompt input validation and robust CLI UX
  * Enhanced error handling and logging
  * Extensible framework for adding more platforms
  * Detailed instructions below for setup and use
"""

import sys
import subprocess
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Setup logging (you may redirect to a file if wanted)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- Dependency check & install ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.text import Text
    from rich.panel import Panel
    import requests
    import instaloader
    import tweepy
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    import praw
    import networkx as nx
    from geopy.geocoders import Nominatim
    from PIL import Image, ExifTags
    from googlesearch import search as google_search
except ImportError:
    # Install missing dependencies then exit to re-run after install
    console = Console()
    console.print(Panel("[yellow]Missing dependencies detected. Installing...[/yellow]", title="Setup"))
    packages = [
        "rich",
        "requests[socks]",
        "instaloader",
        "tweepy",
        "vaderSentiment",
        "praw",
        "networkx",
        "geopy",
        "Pillow",
        "googlesearch-python"
    ]
    subprocess.call([sys.executable, '-m', 'pip', 'install', *packages])
    print("Dependencies installed. Please re-run the script.")
    sys.exit(0)

# --- Globals ---
console = Console()
CONFIG_FILE = Path("credentials.json")

# Simple in-memory cache per run to reduce redundant requests
_cached_results = {}

def load_config():
    """Load credentials and API keys from credentials.json"""
    if not CONFIG_FILE.exists():
        console.print(Panel(
            "⚠️ [yellow]credentials.json not found![/yellow]\nPlease create it with API keys and login credentials.",
            border_style="yellow"))
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logging.info("Loaded credentials.json config.")
            return config
    except json.JSONDecodeError:
        console.print(Panel(
            "🚨 [red]Error reading credentials.json.[/red] File is malformed.",
            border_style="red"))
        return {}

# --- Utility functions ---
def retry_request(func, retries=3, backoff=2, *args, **kwargs):
    """Retry decorator for network functions with exponential backoff"""
    delay = 1
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= backoff
            else:
                raise

def validate_choice(input_str, options_len):
    """Validate comma separated list of IDs allowing multiple selections"""
    chosen = set()
    for item in input_str.split(','):
        item = item.strip()
        if not item.isdigit():
            return None
        idx = int(item)
        if idx < 1 or idx > options_len:
            return None
        chosen.add(idx)
    return sorted(chosen)

def safe_get(data, key, default=None):
    """Safe dict get helper."""
    try:
        return data[key]
    except KeyError:
        return default

# --- Anonymity & Networking ---
def check_tor_connection(session):
    """Checks Tor proxy is working."""
    try:
        r = session.get('https://check.torproject.org', timeout=5)
        return "Congratulations. This browser is configured to use Tor." in r.text
    except requests.RequestException as e:
        logging.error(f"Tor check request failed: {e}")
        return False

def get_session(use_tor=False):
    session = requests.Session()
    if use_tor:
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        if not check_tor_connection(session):
            console.print(Panel("[red]Tor connection failed. Is Tor running on port 9050?[/red]", border_style="red"))
            return None
    return session

# --- Platform Fetchers ---

# Instagram
def fetch_instagram(target, config, session):
    """Fetch Instagram profile info with login & error handling."""
    cache_key = f"instagram_{target}"
    if cache_key in _cached_results:
        return _cached_results[cache_key]

    L = instaloader.Instaloader(dirname_pattern=f"{target}_insta", save_metadata=False, download_videos=False, quiet=True)
    username = target.lstrip('@')
    ig_cfg = config.get('instagram', {})
    if ig_cfg.get('username') and ig_cfg.get('password'):
        try:
            L.login(ig_cfg['username'], ig_cfg['password'])
        except instaloader.exceptions.BadCredentialsException:
            res = {'raw': None, 'summary': f'Instagram error: Bad credentials for {ig_cfg.get("username")}'}
            _cached_results[cache_key] = res
            return res
        except Exception as e:
            res = {'raw': None, 'summary': f'Instagram login error: {e}'}
            _cached_results[cache_key] = res
            return res
    try:
        profile = retry_request(instaloader.Profile.from_username, 3, 2, L.context, username)
        data = {
            'username': profile.username,
            'fullname': profile.full_name,
            'bio': profile.biography,
            'followers': profile.followers,
            'following': profile.followees,
            'posts_count': profile.mediacount,
            'is_private': profile.is_private,
            'latest_posts': []
        }
        # Fetch up to 10 latest posts
        for idx, post in enumerate(profile.get_posts()):
            if idx >= 10:
                break
            data['latest_posts'].append({
                'shortcode': post.shortcode,
                'caption': post.caption,
                'likers': post.likes,
                'comments': post.comments,
                'datetime_utc': post.date_utc.isoformat(),
                'location': str(post.location) if post.location else None
            })
        summary = (f"Instagram {data['username']} - {data['posts_count']} posts, "
                   f"Followers: {data['followers']}")
        res = {'raw': data, 'summary': summary}
        _cached_results[cache_key] = res
        return res
    except instaloader.exceptions.ProfileNotExistsException:
        res = {'raw': None, 'summary': f'Instagram error: Profile {username} not found.'}
        _cached_results[cache_key] = res
        return res
    except Exception as e:
        res = {'raw': None, 'summary': f'Instagram error: {e}'}
        _cached_results[cache_key] = res
        return res

# Twitter
def fetch_twitter(target, config, session):
    """Fetch Twitter user data and tweets using Tweepy."""
    cache_key = f"twitter_{target}"
    if cache_key in _cached_results:
        return _cached_results[cache_key]

    creds = config.get('twitter')
    if not creds:
        res = {'raw': None, 'summary': "Twitter skipped (missing or incomplete credentials)"}
        _cached_results[cache_key] = res
        return res
    try:
        client = tweepy.Client(
            bearer_token=creds.get('bearer_token'),
            consumer_key=creds.get('api_key'),
            consumer_secret=creds.get('api_secret'),
            access_token=creds.get('access_token'),
            access_token_secret=creds.get('access_secret'),
            wait_on_rate_limit=True
        )
        # Get user info
        user_response = client.get_user(username=target.lstrip('@'), user_fields=['public_metrics'])
        user_data = user_response.data
        if not user_data:
            res = {'raw': None, 'summary': f"Twitter error: User {target} not found."}
            _cached_results[cache_key] = res
            return res

        uid = user_data.id
        tweets_resp = client.get_users_tweets(id=uid, max_results=100, tweet_fields=['public_metrics', 'created_at'])
        tweets = []
        for t in tweets_resp.data or []:
            tweets.append({
                'id': t.id,
                'text': t.text,
                'retweets': t.public_metrics.get('retweet_count', 0),
                'likes': t.public_metrics.get('like_count', 0),
                'created_at': t.created_at.isoformat()
            })
        summary = f"Twitter @{user_data.username}: fetched {len(tweets)} tweets."
        res = {'raw': {'user_info': user_data.data, 'posted_tweets': tweets}, 'summary': summary}
        _cached_results[cache_key] = res
        return res
    except tweepy.TweepyException as e:
        res = {'raw': None, 'summary': f"Twitter API error: {e}"}
        _cached_results[cache_key] = res
        return res
    except Exception as e:
        res = {'raw': None, 'summary': f"Twitter unknown error: {e}"}
        _cached_results[cache_key] = res
        return res

# Facebook
def fetch_facebook(target, config, session):
    """Fetch Facebook profile/posts using Graph API access token."""
    cache_key = f"facebook_{target}"
    if cache_key in _cached_results:
        return _cached_results[cache_key]

    fb_cfg = config.get('facebook', {})
    token = fb_cfg.get('access_token')
    if not token:
        res = {'raw': None, 'summary': "Facebook skipped (no access_token in credentials.json)"}
        _cached_results[cache_key] = res
        return res

    try:
        whoami = retry_request(session.get, 3, 2, f"https://graph.facebook.com/v21.0/me?access_token={token}")
        whoami.raise_for_status()
        me = whoami.json()

        feed_resp = retry_request(session.get, 3, 2,
                                  f"https://graph.facebook.com/v21.0/{me['id']}/feed",
                                  params={'access_token': token, 'limit': 10, 'fields': 'message,created_time,id,attachments'})
        feed_resp.raise_for_status()
        posts = feed_resp.json().get('data', [])

        posts_clean = [{'id': p.get('id'), 'message': p.get('message', ''), 'created_time': p.get('created_time')} for p in posts]
        summary = f"Facebook user/page {me.get('name')} • {len(posts_clean)} recent posts"
        res = {'raw': {'profile': me, 'recent_posts': posts_clean}, 'summary': summary}
        _cached_results[cache_key] = res
        return res
    except requests.exceptions.HTTPError as e:
        res = {'raw': None, 'summary': f"Facebook API error: {e}"}
        _cached_results[cache_key] = res
        return res
    except Exception as e:
        res = {'raw': None, 'summary': f"Facebook unknown error: {e}"}
        _cached_results[cache_key] = res
        return res

# Reddit
def fetch_reddit(target, config, session):
    """Fetch Reddit user's recent submissions using PRAW."""
    cache_key = f"reddit_{target}"
    if cache_key in _cached_results:
        return _cached_results[cache_key]

    cfg = config.get('reddit', {})
    required = ('client_id', 'client_secret', 'user_agent')
    if not all(k in cfg for k in required):
        res = {'raw': None, 'summary': "Reddit skipped (incomplete credentials)"}
        _cached_results[cache_key] = res
        return res

    try:
        reddit_client = praw.Reddit(
            client_id=cfg['client_id'],
            client_secret=cfg['client_secret'],
            user_agent=cfg['user_agent'],
            requestor_kwargs={'session': session}
        )
        redditor = reddit_client.redditor(target)
        submissions = []
        for sub in redditor.submissions.new(limit=20):
            submissions.append({
                'id': sub.id,
                'title': sub.title,
                'subreddit': sub.subreddit.display_name,
                'score': sub.score,
                'created_utc': datetime.utcfromtimestamp(sub.created_utc).isoformat()
            })
        summary = f"Reddit u/{target}: {len(submissions)} recent submissions"
        res = {'raw': {'submissions': submissions}, 'summary': summary}
        _cached_results[cache_key] = res
        return res
    except Exception as e:
        res = {'raw': None, 'summary': f"Reddit error: {e}"}
        _cached_results[cache_key] = res
        return res

# Google Dorking
def google_dorking_search(target):
    """Perform Google dork queries on common sites."""
    cache_key = f"google_dork_{target}"
    if cache_key in _cached_results:
        return _cached_results[cache_key]

    queries = [
        f'site:facebook.com "{target}"',
        f'site:linkedin.com "{target}"',
        f'site:pastebin.com "{target}"',
        f'"{target}" email'
    ]
    results = {}
    for q in queries:
        try:
            results[q] = [url for url in google_search(q, num_results=5, lang="en")]
        except Exception as e:
            results[q] = f"Search error: {e}"
    res = {'raw': results, 'summary': f"Google Dorking performed with {len(queries)} queries"}
    _cached_results[cache_key] = res
    return res

# HaveIBeenPwned placeholder
def haveibeenpwned_check(email):
    return {'raw': None, 'summary': f"Checking {email} against HaveIBeenPwned (not implemented)"}

# EXIF geolocation extraction
def advanced_geolocation_exif(image_path):
    try:
        image = Image.open(image_path)
        exif_raw = image._getexif()
        if not exif_raw:
            return {'raw': None, 'summary': "No EXIF metadata found."}
        exif_data = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
        gps_info = exif_data.get('GPSInfo')
        if not gps_info:
            return {'raw': None, 'summary': "No GPSInfo in EXIF data."}

        def deg_min_sec_to_decimal(dms):
            d, m, s = dms
            return d + (m / 60.0) + (s / 3600.0)

        lat = deg_min_sec_to_decimal(gps_info[2])
        lon = deg_min_sec_to_decimal(gps_info[4])
        lat_ref = gps_info[1]
        lon_ref = gps_info[3]
        if lat_ref != 'N':
            lat = -lat
        if lon_ref != 'E':
            lon = -lon

        geolocator = Nominatim(user_agent="osint-tool")
        location = geolocator.reverse(f"{lat}, {lon}")
        summary = location.address if location else "Could not reverse geocode coordinates."
        return {'raw': {'latitude': lat, 'longitude': lon}, 'summary': summary}
    except Exception as e:
        return {'raw': None, 'summary': f"EXIF geolocation error: {e}"}

# --- NLP Analysis ---
def apply_nlp(results):
    """Apply sentiment analysis to text fields in results."""
    analyser = SentimentIntensityAnalyzer()
    for platform, block in list(results.items()):
        raw = block.get('raw')
        if not raw:
            continue
        texts = []
        if platform == 'instagram':
            texts = [post.get('caption', '') or '' for post in raw.get('latest_posts', [])]
        elif platform == 'twitter':
            texts = [tweet.get('text', '') or '' for tweet in raw.get('posted_tweets', [])]
        elif platform == 'facebook':
            texts = [p.get('message', '') or '' for p in raw.get('recent_posts', [])]
        elif platform == 'reddit':
            texts = [sub.get('title', '') or '' for sub in raw.get('submissions', [])]
        else:
            # No NLP on other platforms by default
            continue

        scores = [analyser.polarity_scores(t) for t in texts if t]
        if scores:
            avg = lambda key: sum(s[key] for s in scores) / len(scores)
            sentiment = {
                'pos': avg('pos'),
                'neu': avg('neu'),
                'neg': avg('neg'),
                'compound': avg('compound')
            }
            block['sentiment'] = sentiment
    return results

# --- Main entry point ---
def main():
    console.print(Panel(Text("Nig-a_ohh_shint_slaue", justify="center"),
                        title="[bold green]Ultimate OSINT Toolkit[/bold green]",
                        subtitle="A beast-mode tool for Termux & Linux"))

    cfg = load_config()
    if not cfg:
        console.print("[red]Please set up your credentials.json file before running the tool.[/red]")
        sys.exit(1)

    use_tor = Confirm.ask("Do you want to use Tor for anonymity? (Tor proxy must be running on port 9050)", default=False)
    session = get_session(use_tor) if use_tor else requests.Session()
    if not session:
        console.print("[red]Failed to create HTTP session with Tor. Exiting.[/red]")
        sys.exit(1)

    options = [
        'instagram',
        'twitter',
        'facebook',
        'reddit',
        'google_dork',
        'hibp_email',
        'exif_image_geo'
    ]
    console.print("\n[bold]Select platforms to run (comma-separated IDs):[/bold]")
    table = Table(title="Available Modules")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Module", style="magenta")
    for idx, name in enumerate(options, 1):
        table.add_row(str(idx), name.replace('_', ' ').title())
    console.print(table)

    while True:
        choice_str = Prompt.ask("Enter comma-separated IDs (e.g., 1,3,5)", default="1")
        selected_ids = validate_choice(choice_str, len(options))
        if selected_ids:
            break
        console.print("[red]Invalid selection. Please enter valid IDs separated by commas.[/red]")

    selected = [options[i-1] for i in selected_ids]
    targets = {}

    for module in selected:
        prompt_text = ""
        if module == 'google_dork':
            prompt_text = "Google Dork target (e.g., name, username, email)"
        elif module == 'hibp_email':
            prompt_text = "Email to check on HaveIBeenPwned"
        elif module == 'exif_image_geo':
            prompt_text = "Image file path to extract EXIF geolocation"
        else:
            prompt_text = f"{module.title()} target (username or ID)"
        target = Prompt.ask(f"[bold]{prompt_text}[/bold]")
        if target:
            targets[module] = target

    if not targets:
        console.print("[red]No targets specified. Exiting.[/red]")
        sys.exit(0)

    results = {}
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
    ) as progress:

        tasks = {
            progress.add_task(f"[green]Fetching from {plat.title()}...[/green]", total=1): (plat, targ)
            for plat, targ in targets.items()
        }

        with ThreadPoolExecutor(max_workers=len(targets)) as executor:
            futures = {
                executor.submit(
                    globals().get(f'fetch_{plat}', lambda t, c, s: {'raw': None, 'summary': f'{plat.title()} module not found.'})(targ, cfg, session)
                ): task_id
                for task_id, (plat, targ) in tasks.items()
            }

            for future in futures:
                task_id = futures[future]
                plat, _ = tasks[task_id]
                try:
                    results[plat] = future.result()
                except Exception as e:
                    results[plat] = {'raw': None, 'summary': f'{plat.title()} error: {e}'}
                progress.update(task_id, completed=1)

    # NLP sentiment analysis (expanded)
    nlp_results = apply_nlp(results)

    console.print(Panel(Text("Analysis Complete", justify="center"), title="[bold green]Report Summary[/bold green]"))

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Platform", style="dim", width=16)
    table.add_column("Summary", overflow="fold")

    for platform, res in nlp_results.items():
        summary = safe_get(res, 'summary', 'No summary available.')
        if 'sentiment' in res:
            sentiment = res['sentiment']
            summary += f"\n[bold]→ Sentiment:[/bold] Compound: [cyan]{sentiment['compound']:.3f}[/cyan], Pos: {sentiment['pos']:.3f}, Neg: {sentiment['neg']:.3f}"
        table.add_row(platform.title(), summary)
    console.print(table)

    # Save full JSON report to file
    filename = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(nlp_results, f, indent=2, default=str)
    console.print(f"\n[green]✓ Report saved to [bold]{filename}[/bold][/green]")

    if Confirm.ask("Do you want to see the full JSON output?"):
        console.print_json(json.dumps(nlp_results, indent=2, default=str))


if __name__ == "__main__":
    main()
