#!/usr/bin/env python3
"""
Nig-a_ohh_shint_slaue: The Ultimate cross-platform OSINT toolkit.
Auto-installer ★ CLI selection ★ NLP analysis ★ Tor Integration ★ Advanced Search
"""

import os
import sys
import subprocess
import shutil
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# --- Dependencies & Installation ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.text import Text
    from rich.panel import Panel
    from rich.markdown import Markdown
    import requests
    import instaloader
    import tweepy
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    import praw
    import networkx as nx
    from geopy.geocoders import Nominatim
    from PIL import Image, ExifTags
    from googlesearch import search as Google Search
    # Placeholder for haveibeenpwned (pwned-passwords-sha1 library or API call)
    # Placeholder for Scrapy (for deep web crawling)
    # Placeholder for tldextract (for domain parsing)

except ImportError:
    print("Dependencies not met. Running installer...")
    packages = ["rich", "requests[socks]", "instaloader", "tweepy", "vaderSentiment", "praw", "networkx", "geopy", "Pillow", "google-search-python"]
    subprocess.call([sys.executable, '-m', 'pip', 'install', ' '.join(packages)])
    print("Dependencies installed. Please re-run the script.")
    sys.exit(0)

# --- Global Config ---
console = Console()
CONFIG_FILE = Path('credentials.json')

def load_config():
    """Loads credentials from the JSON config file."""
    if not CONFIG_FILE.exists():
        console.print(Panel("⚠️ [yellow]credentials.json not found![/yellow]\nPlease create it with API keys for enhanced functionality.",
                            border_style="yellow"))
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print(Panel("🚨 [red]Error reading credentials.json.[/red] File is malformed.",
                            border_style="red"))
        return {}

# --- Anonymity & Networking ---
def check_tor_connection(session):
    """Checks if the session is using Tor."""
    try:
        r = session.get('https://check.torproject.org', timeout=5)
        return "Congratulations. This browser is configured to use Tor." in r.text
    except requests.RequestException:
        return False

def get_session(use_tor=False):
    """Returns a requests session, optionally configured for Tor."""
    session = requests.Session()
    if use_tor:
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        if not check_tor_connection(session):
            console.print(Panel("🚨 [red]Tor connection failed.[/red] Make sure Tor is running on port 9050.",
                                border_style="red"))
            return None
    return session

# --- Platform Modules (Updated) ---
# ... (Instaloader, Tweepy, PRAW, etc. code from before) ...
# I am re-including the updated versions with better error handling and rich library usage.
def fetch_instagram(target, config, session):
    """Fetch Instagram public profile info with better error handling."""
    L = instaloader.Instaloader(
        dirname_pattern=f'{target}_insta', save_metadata=False, download_videos=False, quiet=True
    )
    username = target.lstrip('@')
    ig_cfg = config.get('instagram', {})
    if ig_cfg.get('username') and ig_cfg.get('password'):
        try:
            L.login(ig_cfg['username'], ig_cfg['password'])
        except instaloader.exceptions.BadCredentialsException:
            return {'raw': None, 'summary': f'Instagram error: Bad credentials for {ig_cfg["username"]}'}
    try:
        profile = instaloader.Profile.from_username(L.context, username)
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
        for post in profile.get_posts():
            if len(data['latest_posts']) >= 10: break
            data['latest_posts'].append({
                'shortcode': post.shortcode, 'caption': post.caption, 'likers': post.likes,
                'comments': post.comments, 'datetime_utc': post.date_utc.isoformat(),
                'location': str(post.location) if post.location else None
            })
        summary = (f"Instagram {data['username']}: {data['posts_count']} posts, "
                   f"Followers: {data['followers']}")
        return {'raw': data, 'summary': summary}
    except instaloader.exceptions.ProfileNotExistsException:
        return {'raw': None, 'summary': f'Instagram error: Profile {username} not found.'}
    except Exception as e:
        return {'raw': None, 'summary': f'Instagram error: {e}'}

def fetch_twitter(target, config, session):
    """Using Tweepy for robust Twitter data fetching."""
    creds = config.get('twitter')
    if not creds:
        return {'raw': None, 'summary': "Twitter skipped (incomplete creds)"}
    try:
        client = tweepy.Client(
            bearer_token=creds.get('bearer_token'),
            consumer_key=creds.get('api_key'),
            consumer_secret=creds.get('api_secret'),
            access_token=creds.get('access_token'),
            access_token_secret=creds.get('access_secret')
        )
        user = client.get_user(username=target.lstrip('@'), user_fields=['public_metrics'])
        if not user.data:
            return {'raw': None, 'summary': f'Twitter error: User {target} not found.'}
        
        uid = user.data.id
        resp = client.get_users_tweets(id=uid, max_results=100, tweet_fields=['public_metrics','created_at'])
        tweets = []
        for t in resp.data or []:
            tweets.append({'id': t.id, 'text': t.text, 'retweets': t.public_metrics['retweet_count'],
                           'likes': t.public_metrics['like_count'], 'created_at': t.created_at.isoformat()})
        
        summary = f"Twitter @{user.data.username}: fetched {len(tweets)} tweets."
        return {'raw': {'user_info': user.data.data, 'posted_tweets': tweets}, 'summary': summary}
    except tweepy.errors.TweepyException as e:
        return {'raw': None, 'summary': f'Twitter error: {e}'}

def fetch_facebook(target, config, session):
    """Fetch public profile or page feed via Graph API using access token."""
    fb_cfg = config.get('facebook', {})
    token = fb_cfg.get('access_token')
    if not token:
        return {'raw': None, 'summary': "Facebook skipped (no access_token)"}
    try:
        # Check if token is valid and get user info
        whoami = session.get(f"https://graph.facebook.com/v21.0/me?access_token={token}")
        whoami.raise_for_status()
        me = whoami.json()
        
        # Get recent posts
        resp = session.get(f"https://graph.facebook.com/v21.0/{me['id']}/feed",
                            params={'access_token': token, 'limit': 10, 'fields': 'message,created_time,id,attachments'})
        resp.raise_for_status()
        posts = resp.json().get('data', [])
        
        posts_clean = [{'id': p.get('id'), 'message': p.get('message', ''), 'created_time': p.get('created_time')} for p in posts]
        summary = f"Facebook user/page {me.get('name')} • {len(posts_clean)} recent posts"
        return {'raw': {'profile': me, 'recent_posts': posts_clean}, 'summary': summary}
    except requests.exceptions.HTTPError as e:
        return {'raw': None, 'summary': f"Facebook API error: {e}"}

def fetch_reddit(target, config, session):
    """Use PRAW to fetch recent submissions/comments of a Reddit user."""
    cfg = config.get('reddit', {})
    required = ('client_id','client_secret','user_agent')
    if not all(k in cfg for k in required):
        return {'raw': None, 'summary': "Reddit skipped (incomplete creds)"}
    try:
        r = praw.Reddit(client_id=cfg['client_id'], client_secret=cfg['client_secret'],
                        user_agent=cfg['user_agent'], requestor_kwargs={'session': session})
        submissions = []
        redd = r.redditor(target)
        for sub in redd.submissions.new(limit=20):
            submissions.append({
                'id': sub.id, 'title': sub.title, 'subreddit': sub.subreddit.display_name,
                'score': sub.score, 'created_utc': datetime.utcfromtimestamp(sub.created_utc).isoformat()
            })
        summary = f"Reddit u/{target}: {len(submissions)} recent submissions"
        return {'raw': {'submissions': submissions}, 'summary': summary}
    except Exception as e:
        return {'raw': None, 'summary': f"Reddit error: {e}"}

# --- NLP Analysis ---
def apply_nlp(results):
    """Applies sentiment analysis to all text-based posts."""
    analyser = SentimentIntensityAnalyzer()
    for platform, block in list(results.items()):
        raw = block.get('raw')
        if raw and platform in ('instagram','twitter','facebook'):
            texts = []
            if platform == 'instagram':
                texts = [post['caption'] or '' for post in raw.get('latest_posts', [])]
            elif platform == 'twitter':
                texts = [tweet.get('text') or '' for tweet in raw.get('posted_tweets', [])]
            elif platform == 'facebook':
                texts = [p.get('message') or '' for p in raw.get('recent_posts', [])]
            scores = [analyser.polarity_scores(t) for t in texts if t]
            if scores:
                avg = lambda key: sum(s[key] for s in scores) / len(scores)
                sentiment = {'pos': avg('pos'), 'neu': avg('neu'), 'neg': avg('neg'), 'compound': avg('compound')}
                block['sentiment'] = sentiment
    return results

# --- Advanced Features ---
def advanced_geolocation_exif(image_path):
    """Extracts geolocation from image EXIF data."""
    try:
        image = Image.open(image_path)
        exif_data = {
            ExifTags.TAGS[k]: v
            for k, v in image._getexif().items()
            if k in ExifTags.TAGS
        }
        lat = exif_data.get('GPSInfo').get(2)
        lon = exif_data.get('GPSInfo').get(4)
        if lat and lon:
            # Convert degrees, minutes, seconds to decimal
            lat_d = lat[0] + lat[1]/60 + lat[2]/3600
            lon_d = lon[0] + lon[1]/60 + lon[2]/3600
            geolocator = Nominatim(user_agent="osint-tool")
            location = geolocator.reverse(f"{lat_d}, {lon_d}")
            return str(location.address)
    except (AttributeError, KeyError, IndexError):
        return None

def haveibeenpwned_check(email):
    """Placeholder for checking an email against HIBP API."""
    # Note: A real implementation would require an API key and a call to the HIBP API.
    # For now, it's a conceptual function.
    return f"Checking {email} against HaveIBeenPwned..."

def google_dorking_search(target):
    """Performs a Google Dorking search for a target's name or username."""
    queries = [
        f'site:facebook.com "{target}"',
        f'site:linkedin.com "{target}"',
        f'site:pastebin.com "{target}"',
        f'"{target}" email'
    ]
    results = {}
    for q in queries:
        try:
            results[q] = [url for url in Google Search(q, num_results=5, lang="en")]
        except Exception as e:
            results[q] = f"Error during search: {e}"
    return results

# --- Main Tool Flow ---
def main():
    console.print(Panel(Text("Nig-a_ohh_shint_slaue", justify="center"),
                      title="[bold green]Ultimate OSINT Toolkit[/bold green]",
                      subtitle="A beast-mode tool for Termux & Linux"))
    
    cfg = load_config()

    use_tor = Confirm.ask("Do you want to use Tor for anonymity? (Requires Tor service running)", default=False)
    session = get_session(use_tor) if use_tor else requests.Session()
    if not session:
        sys.exit(1)

    options = ['instagram', 'twitter', 'facebook', 'reddit', 'google_dork', 'hibp_email', 'exif_image_geo']
    console.print("\n[bold]Select platforms to run:[/bold]")
    table = Table(title="Available Modules")
    table.add_column("ID", style="cyan")
    table.add_column("Module", style="magenta")
    for idx, p in enumerate(options, 1):
        table.add_row(str(idx), p.replace('_', ' ').title())
    console.print(table)
    
    choose = Prompt.ask("Enter comma-separated IDs (e.g., 1,3,5)", choices=[str(i) for i in range(1, len(options) + 1)])
    selected = [options[int(x.strip())-1] for x in choose.split(',')]

    targets = {}
    for p in selected:
        if p in ['google_dork', 'hibp_email', 'exif_image_geo']:
            inp = Prompt.ask(f"[bold]{p.replace('_', ' ').title()}[/bold] target (e.g., username, email, image path)")
        else:
            inp = Prompt.ask(f"[bold]{p.title()}[/bold] target (username or ID)")
        if inp:
            targets[p] = inp

    results = {}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        tasks = {
            progress.add_task(f"[bold green]Fetching from {plat.title()}...[/bold green]", total=1): (plat, targ)
            for plat, targ in targets.items()
        }

        # Use a thread pool to run fetchers in parallel
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

    console.print(Panel(Text("Analysis Complete", justify="center"),
                      title="[bold green]Report Summary[/bold green]"))

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Platform", style="dim", width=12)
    table.add_column("Summary")
    
    for p, res in results.items():
        summary = res.get('summary', 'No summary provided.')
        if 'sentiment' in res:
            nfl = res['sentiment']
            summary += f"\n[bold]→ Sentiment:[/bold] Compound: [cyan]{nfl['compound']:.3f}[/cyan] (Pos: {nfl['pos']:.3f}, Neg: {nfl['neg']:.3f})"
        table.add_row(p.title(), summary)
    console.print(table)
    
    # NLP and other analysis
    console.print("\n[bold underline]Advanced Analysis:[/bold underline]")
    nlp_results = apply_nlp(results)
    # The sentiment analysis is already integrated into the summary display, but this could be a point for more complex NLP, like topic modeling.
    
    # Save results to a file
    filename = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(nlp_results, f, indent=2, default=str)
    console.print(f"\n[green]✓ Report saved to {filename}[/green]")
    
    if Confirm.ask("Do you want to see the full JSON output?"):
        console.print(json.dumps(nlp_results, indent=2, default=str))

if __name__ == '__main__':
    # Initial install check for essential libraries
    try:
        import rich
        import requests
        import instaloader
        import tweepy
        import vaderSentiment
        import praw
        import networkx
        import geopy
        import PIL
        import googlesearch
    except ImportError:
        packages = ["rich", "requests[socks]", "instaloader", "tweepy", "vaderSentiment", "praw", "networkx", "geopy", "Pillow", "google-search-python"]
        console.print(Panel(Text("Initial setup: installing dependencies...", justify="center"), border_style="yellow"))
        for pkg in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
                console.print(f"[green]✓ Successfully installed {pkg}[/green]")
            except subprocess.CalledProcessError:
                console.print(f"[red]X Failed to install {pkg}. Please try again manually.[/red]")
        sys.exit(0) # Exit and prompt re-run

    main()
