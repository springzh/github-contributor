#!/usr/bin/env python3
"""
Simplified GitHub Blockchain Contributors Extractor
A more robust version with better rate limit management
"""

import requests
import csv
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleGitHubExtractor:
    def __init__(self, token: Optional[str] = None, blockchain_csv_path: str = 'evm_blockchains.csv'):
        """Initialize the extractor with optional GitHub token and blockchain CSV data"""
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Blockchain-Contributors-Extractor'
        })
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        
        self.base_url = 'https://api.github.com'
        self.last_request_time = 0
        self.min_delay = 2.0  # Increased minimum delay between requests to avoid rate limits
        
        # Load blockchain data from CSV file
        self.blockchain_repos = self._load_blockchain_data(blockchain_csv_path)

    def respect_rate_limit(self):
        """Ensure we don't make requests too quickly"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_delay:
            sleep_time = self.min_delay - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def make_request(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Make a request with retry logic and rate limiting"""
        self.respect_rate_limit()
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                
                # Check for rate limiting
                if response.status_code == 403:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                    wait_time = max(60, reset_time - int(time.time()))
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    return None
                
                if response.status_code != 200:
                    logger.warning(f"Request failed: {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                
                return response.json()
                
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None

    def _load_blockchain_data(self, csv_path: str) -> List[Dict]:
        """Load blockchain data from CSV file and extract GitHub repository information"""
        blockchain_repos = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    github_url = row.get('GitHub Repository URL', '')
                    if github_url:
                        # Parse GitHub URL to extract owner and repo
                        parsed_url = urlparse(github_url)
                        path_parts = parsed_url.path.strip('/').split('/')
                        
                        if len(path_parts) >= 2:
                            owner = path_parts[0]
                            repo = path_parts[1]
                            project_name = row.get('Project Name', f"{owner}/{repo}")
                            
                            blockchain_repos.append({
                                'owner': owner,
                                'repo': repo,
                                'name': project_name,
                                'layer_type': row.get('Layer Type', ''),
                                'category': row.get('Category', ''),
                                'purpose': row.get('Purpose/Specialization', ''),
                                'description': row.get('Description', '')
                            })
                            
            logger.info(f"Loaded {len(blockchain_repos)} blockchain repositories from {csv_path}")
            return blockchain_repos
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading blockchain data from {csv_path}: {e}")
            return []

    def get_top_repositories_for_blockchain(self, owner: str, repo: str, limit: int = 5) -> List[Dict]:
        """Get top repositories for a blockchain organization"""
        logger.info(f"🔍 Fetching top {limit} repositories for {owner}...")
        
        # Get organization repositories
        url = f"{self.base_url}/orgs/{owner}/repos?per_page={limit}&sort=stars&order=desc"
        data = self.make_request(url)
        
        if not data:
            logger.warning(f"⚠️  No repositories found for {owner}")
            return []
        
        if isinstance(data, list):
            repositories = []
            for repo_data in data[:limit]:
                repositories.append({
                    'owner': owner,
                    'repo': repo_data['name'],
                    'name': repo_data['full_name'],
                    'stars': repo_data.get('stargazers_count', 0),
                    'description': repo_data.get('description', '')
                })
            
            logger.info(f"✅ Found {len(repositories)} top repositories for {owner}")
            return repositories
        else:
            logger.error(f"❌ Unexpected data format received")
            return []

    def get_top_contributors(self, owner: str, repo: str, max_contributors: int = 3) -> List[Dict]:
        """Get top contributors for a repository"""
        logger.info(f"🔍 Fetching top {max_contributors} contributors from {owner}/{repo}...")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors?per_page={max_contributors}"
        data = self.make_request(url)
        
        if not data or not isinstance(data, list):
            logger.warning(f"⚠️  No contributors found for {owner}/{repo}")
            return []
        
        # Filter for users only
        contributors = [c for c in data if c.get('type') == 'User'][:max_contributors]
        logger.info(f"✅ Found {len(contributors)} top contributors")
        
        # Show all top contributors
        if contributors:
            top_users = [c['login'] for c in contributors]
            logger.info(f"👥 Top contributors: {', '.join(top_users)}")
        
        return contributors

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        url = f"{self.base_url}/users/{username}"
        return self.make_request(url)

    def extract_contributors_data(self, repo_info: Dict, max_contributors: int = 10) -> List[Dict]:
        """Extract contributor data for a single repository"""
        owner = repo_info['owner']
        repo = repo_info['repo']
        project_name = repo_info['name']
        
        logger.info(f"🚀 Processing {project_name} ({owner}/{repo})")
        
        contributors_data = self.get_top_contributors(owner, repo, max_contributors)
        
        if not contributors_data:
            logger.warning(f"⚠️  No contributors found for {project_name}")
            return []
        
        logger.info(f"📊 Found {len(contributors_data)} top contributors. Fetching detailed profiles...")
        
        results = []
        
        for i, contributor in enumerate(contributors_data, 1):
            username = contributor['login']
            logger.info(f"⏳ [{i}/{len(contributors_data)}] Fetching profile for @{username}")
            
            user_info = self.get_user_info(username)
            
            if user_info:
                contributor_data = {
                    'project_name': project_name,
                    'project_url': f"https://github.com/{owner}/{repo}",
                    'contributor_username': username,
                    'contributor_url': user_info.get('html_url', ''),
                    'contributor_name': user_info.get('name', ''),
                    'contributor_email': user_info.get('email', ''),
                    'contributions': contributor.get('contributions', 0),
                    'twitter': user_info.get('twitter_username', ''),
                    'website': user_info.get('blog', ''),
                    'location': user_info.get('location', ''),
                    'company': user_info.get('company', ''),
                        'followers': user_info.get('followers', 0),
                        'following': user_info.get('following', 0),
                        'public_repos': user_info.get('public_repos', 0),
                        'account_created': user_info.get('created_at', ''),
                        'last_updated': user_info.get('updated_at', '')
                }
                results.append(contributor_data)
                
                # Show sample data for each contributor
                self._show_sample_contributor(contributor_data)
                
                # Sleep between user profile requests to avoid rate limits
                time.sleep(1)
            else:
                logger.warning(f"⚠️  Could not fetch details for @{username}")
        
        logger.info(f"✅ Completed processing {project_name}: {len(results)} top contributor profiles extracted")
        return results
    
    def _show_sample_contributor(self, contributor_info: Dict):
        """Display sample contributor information"""
        name = contributor_info.get('contributor_name', 'N/A')
        username = contributor_info.get('contributor_username', 'N/A')
        contributions = contributor_info.get('contributions', 0)
        email = contributor_info.get('contributor_email', 'N/A')
        twitter = contributor_info.get('twitter', 'N/A')
        
        logger.info(f"👤 {name} (@{username}) - {contributions} contributions")
        if email != 'N/A':
            logger.info(f"   📧 Email: {email}")
        if twitter != 'N/A':
            logger.info(f"   🐦 Twitter: @{twitter}")

    def save_to_csv(self, data: List[Dict], filename: str):
        """Save data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
        
        # Get all unique keys from all dictionaries to handle dynamic fields
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Data saved to {filename}")

    def run_extraction(self, max_contributors_per_repo: int = 3, output_file: str = None) -> str:
        """Run the extraction process"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"blockchain_contributors_{timestamp}.csv"
        
        logger.info("🌟 Starting blockchain contributors extraction")
        logger.info(f"📋 Processing {len(self.blockchain_repos)} top repositories")
        logger.info(f"👥 Getting top {max_contributors_per_repo} contributors per repository")
        
        all_contributors = []
        seen_usernames = set()  # Track unique usernames to avoid duplicates
        
        for i, repo_info in enumerate(self.blockchain_repos, 1):
            repo_name = repo_info['name']
            logger.info(f"\n📁 [{i}/{len(self.blockchain_repos)}] Processing: {repo_name}")
            logger.info("=" * 50)
            
            try:
                repo_contributors = self.extract_contributors_data(repo_info, max_contributors_per_repo)
                
                # Add only new contributors (avoid duplicates)
                new_contributors = []
                for contributor in repo_contributors:
                    username = contributor['contributor_username']
                    if username not in seen_usernames:
                        seen_usernames.add(username)
                        new_contributors.append(contributor)
                    else:
                        logger.info(f"⚠️  Skipping duplicate contributor: @{username}")
                
                all_contributors.extend(new_contributors)
                logger.info(f"✅ Added {len(new_contributors)} new contributors from {repo_name}")
                logger.info(f"📈 Total unique contributors so far: {len(all_contributors)}")
                
                # Save progress after each repository
                self.save_to_csv(all_contributors, output_file)
                
                # Sleep between repositories to avoid rate limits
                if i < len(self.blockchain_repos):
                    logger.info(f"⏳ Sleeping 2 seconds before next repository...")
                    time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error processing {repo_info['name']}: {e}")
                continue
        
        logger.info(f"\n📊 Final Statistics:")
        logger.info(f"   ✅ Successfully processed: {len([r for r in self.blockchain_repos if any(c['project_name'] == r['name'] for c in all_contributors)])} repositories")
        logger.info(f"   👥 Total unique contributors: {len(all_contributors)}")
        logger.info(f"   📁 Results saved to: {output_file}")
        
        return output_file

    def run_blockchain_extraction_with_top_repos(self, max_contributors_per_repo: int = 3, output_file: str = None) -> str:
        """Run the extraction process for blockchain organizations with their top repositories"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"blockchain_contributors_{timestamp}.csv"
        
        logger.info("🌟 Starting blockchain contributors extraction with top repositories")
        logger.info(f"📋 Processing {len(self.blockchain_repos)} blockchain organizations")
        logger.info(f"👥 Getting top {max_contributors_per_repo} contributors per repository")
        logger.info(f"🔍 Getting top 5 repositories per organization")
        
        all_contributors = []
        seen_usernames = set()  # Track unique usernames to avoid duplicates
        successful_orgs = 0
        failed_orgs = 0
        
        for i, blockchain_info in enumerate(self.blockchain_repos, 1):
            owner = blockchain_info['owner']
            repo = blockchain_info['repo']
            project_name = blockchain_info['name']
            
            logger.info(f"\n📁 [{i}/{len(self.blockchain_repos)}] Processing: {project_name} ({owner})")
            logger.info("=" * 60)
            
            try:
                # Get top 5 repositories for this blockchain organization
                top_repos = self.get_top_repositories_for_blockchain(owner, repo, limit=5)
                
                if not top_repos:
                    logger.warning(f"⚠️  No repositories found for {owner}")
                    failed_orgs += 1
                    continue
                
                # Process each repository
                for repo_info in top_repos:
                    logger.info(f"🔍 Processing repository: {repo_info['name']}")
                    repo_contributors = self.extract_contributors_data(repo_info, max_contributors_per_repo)
                    
                    # Add blockchain metadata to each contributor
                    for contributor in repo_contributors:
                        contributor['blockchain_name'] = project_name
                        contributor['blockchain_layer_type'] = blockchain_info.get('layer_type', '')
                        contributor['blockchain_category'] = blockchain_info.get('category', '')
                        contributor['blockchain_purpose'] = blockchain_info.get('purpose', '')
                        contributor['blockchain_description'] = blockchain_info.get('description', '')
                        contributor['repo_stars'] = repo_info.get('stars', 0)
                        contributor['repo_description'] = repo_info.get('description', '')
                    
                    # Add only new contributors (avoid duplicates)
                    new_contributors = []
                    for contributor in repo_contributors:
                        username = contributor['contributor_username']
                        if username not in seen_usernames:
                            seen_usernames.add(username)
                            new_contributors.append(contributor)
                        else:
                            logger.info(f"⚠️  Skipping duplicate contributor: @{username}")
                    
                    all_contributors.extend(new_contributors)
                    logger.info(f"✅ Added {len(new_contributors)} new contributors from {repo_info['name']}")
                
                successful_orgs += 1
                logger.info(f"📈 Total unique contributors so far: {len(all_contributors)}")
                
                # Save progress after each organization
                self.save_to_csv(all_contributors, output_file)
                
                # Sleep between organizations to avoid rate limits
                if i < len(self.blockchain_repos):
                    logger.info(f"⏳ Sleeping 3 seconds before next organization...")
                    time.sleep(3)
                
            except Exception as e:
                failed_orgs += 1
                logger.error(f"❌ Error processing {project_name}: {e}")
                continue
        
        logger.info(f"\n📊 Final Statistics:")
        logger.info(f"   ✅ Successfully processed: {successful_orgs} organizations")
        logger.info(f"   ❌ Failed to process: {failed_orgs} organizations")
        logger.info(f"   👥 Total unique contributors: {len(all_contributors)}")
        logger.info(f"   📁 Results saved to: {output_file}")
        
        return output_file

def main():
    """Main function"""
    print("🚀 Starting GitHub Blockchain Contributors Extraction")
    print("=" * 60)
    
    # Check for GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("⚠️  No GITHUB_TOKEN found in environment variables.")
        print("   Using unauthenticated requests (limited to 60 requests/hour)")
        print("   For better results, set: export GITHUB_TOKEN=your_token")
        print()
    
    # Create extractor with blockchain CSV data
    extractor = SimpleGitHubExtractor(token, blockchain_csv_path='evm_blockchains.csv')
    
    # Run extraction with blockchain organizations and their top repositories
    print("📊 Extracting contributors from blockchain organizations with top repositories...")
    output_file = extractor.run_blockchain_extraction_with_top_repos(
        max_contributors_per_repo=3  # Get top 3 contributors per repo
        # output_file will be auto-generated with timestamp
    )
    
    print(f"\n✅ Extraction completed!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📈 Total blockchain organizations processed: {len(extractor.blockchain_repos)}")
    print(f"🔍 Each organization's top 5 repositories analyzed")
    print(f"👥 Top 3 contributors per repository extracted")

if __name__ == "__main__":
    main()