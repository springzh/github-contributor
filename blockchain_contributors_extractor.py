#!/usr/bin/env python3
"""
GitHub Blockchain Contributors Extractor
Extracts contributor information from major blockchain GitHub repositories
"""

import requests
import csv
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import ssl
import socket
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubContributorExtractor:
    def __init__(self, token: Optional[str] = None, blockchain_csv_path: str = 'evm_blockchains.csv'):
        """
        Initialize the GitHub contributor extractor
        
        Args:
            token: GitHub personal access token for API authentication
            blockchain_csv_path: Path to CSV file containing blockchain data
        """
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Blockchain-Contributors-Extractor'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
        
        self.base_url = 'https://api.github.com'
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
        
        # Load blockchain data from CSV file
        self.blockchain_repos = self._load_blockchain_data(blockchain_csv_path)

    def check_rate_limit(self):
        """Check and respect GitHub API rate limits"""
        if self.rate_limit_remaining <= 1:
            wait_time = max(0, self.rate_limit_reset - int(time.time()))
            if wait_time > 0:
                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        
        # Make a request to check current rate limit
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.rate_limit_remaining = data['rate']['remaining']
                self.rate_limit_reset = data['rate']['reset']
                logger.info(f"Rate limit remaining: {self.rate_limit_remaining}")
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")

    def make_request(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Make a GitHub API request with error handling, rate limiting, and retry logic"""
        self.check_rate_limit()
        
        for attempt in range(max_retries):
            try:
                # Configure session with better SSL settings
                session = requests.Session()
                session.headers.update(self.headers)
                
                # SSL configuration for better compatibility
                session.verify = True
                session.timeout = 30
                
                response = session.get(url)
                
                if response.status_code == 403:
                    logger.error("Rate limit exceeded or access forbidden")
                    return None
                elif response.status_code == 404:
                    logger.error(f"Resource not found: {url}")
                    return None
                elif response.status_code != 200:
                    logger.error(f"Request failed: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                
                self.rate_limit_remaining -= 1
                return response.json()
                
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("Max retries reached for SSL error")
                return None
                
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("Max retries reached for connection error")
                return None
                
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("Max retries reached for timeout error")
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("Max retries reached for request error")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("Max retries reached for unexpected error")
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

    def get_repo_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get top 10 contributors for a specific repository"""
        logger.info(f"🔍 Fetching top 10 contributors from {owner}/{repo}...")
        
        # Get first page with 10 contributors only
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors?per_page=10"
        data = self.make_request(url)
        
        if not data:
            logger.warning(f"⚠️  No contributors found for {owner}/{repo}")
            return []
        
        if isinstance(data, list):
            # Filter for users only and take top 10
            contributors = [c for c in data if c.get('type') == 'User'][:10]
            logger.info(f"✅ Found {len(contributors)} top contributors")
            
            # Show all top contributors
            if contributors:
                top_users = [c['login'] for c in contributors]
                logger.info(f"👥 Top contributors: {', '.join(top_users)}")
            
            return contributors
        else:
            logger.error(f"❌ Unexpected data format received")
            return []

    def get_user_details(self, username: str) -> Optional[Dict]:
        """Get detailed information about a user"""
        url = f"{self.base_url}/users/{username}"
        return self.make_request(url)

    def extract_social_links(self, user_data: Dict) -> Dict[str, str]:
        """Extract social media links from user data"""
        social_links = {
            'twitter': '',
            'linkedin': '',
            'website': '',
            'blog': '',
            'location': '',
            'company': '',
            'bio': ''
        }
        
        if user_data:
            social_links['twitter'] = user_data.get('twitter_username', '')
            social_links['linkedin'] = user_data.get('blog', '') if 'linkedin.com' in user_data.get('blog', '') else ''
            social_links['website'] = user_data.get('blog', '') if 'linkedin.com' not in user_data.get('blog', '') else ''
            social_links['blog'] = user_data.get('blog', '')
            social_links['location'] = user_data.get('location', '')
            social_links['company'] = user_data.get('company', '')
            social_links['bio'] = user_data.get('bio', '')
        
        return social_links

    def process_repository(self, repo_info: Dict) -> List[Dict]:
        """Process a single repository and extract contributor information"""
        owner = repo_info['owner']
        repo = repo_info['repo']
        project_name = repo_info['name']
        
        logger.info(f"🚀 Processing {project_name} ({owner}/{repo})")
        
        contributors_data = self.get_repo_contributors(owner, repo)
        
        if not contributors_data:
            logger.warning(f"⚠️  No contributors found for {project_name}")
            return []
        
        logger.info(f"📊 Found {len(contributors_data)} top contributors. Fetching detailed profiles...")
        
        results = []
        
        for i, contributor in enumerate(contributors_data, 1):
            username = contributor['login']
            logger.info(f"⏳ [{i}/{len(contributors_data)}] Fetching profile for @{username}")
            
            user_details = self.get_user_details(username)
            
            if user_details:
                social_links = self.extract_social_links(user_details)
                
                contributor_info = {
                    'project_name': project_name,
                    'project_url': f"https://github.com/{owner}/{repo}",
                    'contributor_username': username,
                    'contributor_url': user_details.get('html_url', ''),
                    'contributor_name': user_details.get('name', ''),
                    'contributor_email': user_details.get('email', ''),
                    'contributions': contributor.get('contributions', 0),
                    'twitter': social_links['twitter'],
                    'linkedin': social_links['linkedin'],
                    'website': social_links['website'],
                    'blog': social_links['blog'],
                    'location': social_links['location'],
                    'company': social_links['company'],
                    'bio': social_links['bio'],
                    'followers': user_details.get('followers', 0),
                    'following': user_details.get('following', 0),
                    'public_repos': user_details.get('public_repos', 0),
                    'account_created': user_details.get('created_at', ''),
                    'last_updated': user_details.get('updated_at', '')
                }
                
                results.append(contributor_info)
                
                # Show sample data for each contributor
                self._show_sample_contributor(contributor_info)
                
                # Small delay to be respectful to the API
                time.sleep(0.1)
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
        
        logger.info(f"👤 Sample: {name} (@{username}) - {contributions} contributions")
        if email != 'N/A':
            logger.info(f"   📧 Email: {email}")
        if twitter != 'N/A':
            logger.info(f"   🐦 Twitter: @{twitter}")

    def save_to_csv(self, data: List[Dict], filename: str):
        """Save contributor data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
        
        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Data saved to {filename}")

    def save_to_excel(self, data: List[Dict], filename: str):
        """Save contributor data to Excel file"""
        try:
            import pandas as pd
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except ImportError:
            logger.error("pandas and openpyxl required for Excel export. Install with: pip install pandas openpyxl")
            # Fallback to CSV
            self.save_to_csv(data, filename.replace('.xlsx', '.csv'))

    def extract_blockchain_contributors_with_top_repos(self, output_format: str = 'csv', output_filename: str = None) -> str:
        """Extract contributors from blockchain organizations with their top repositories"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"blockchain_contributors_{timestamp}.{output_format}"
        
        logger.info("🌟 Starting blockchain contributors extraction with top repositories")
        logger.info(f"📋 Processing {len(self.blockchain_repos)} blockchain organizations")
        logger.info(f"💾 Output will be saved to: {output_filename}")
        
        all_contributors = []
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
                    repo_contributors = self.process_repository(repo_info)
                    
                    # Add blockchain metadata to each contributor
                    for contributor in repo_contributors:
                        contributor['blockchain_name'] = project_name
                        contributor['blockchain_layer_type'] = blockchain_info.get('layer_type', '')
                        contributor['blockchain_category'] = blockchain_info.get('category', '')
                        contributor['blockchain_purpose'] = blockchain_info.get('purpose', '')
                        contributor['blockchain_description'] = blockchain_info.get('description', '')
                        contributor['repo_stars'] = repo_info.get('stars', 0)
                        contributor['repo_description'] = repo_info.get('description', '')
                    
                    all_contributors.extend(repo_contributors)
                
                successful_orgs += 1
                
                # Show cumulative progress
                logger.info(f"📈 Cumulative progress: {len(all_contributors)} contributors from {successful_orgs} organizations")
                
                # Save intermediate progress every 3 organizations
                if successful_orgs % 3 == 0:
                    self.save_to_csv(all_contributors, f"intermediate_{output_filename}")
                    logger.info(f"💾 Intermediate progress saved to intermediate_{output_filename}")
                
            except Exception as e:
                failed_orgs += 1
                logger.error(f"❌ Error processing {project_name}: {e}")
                continue
        
        # Remove duplicates based on contributor username and project
        logger.info(f"\n🔍 Removing duplicates...")
        unique_contributors = []
        seen = set()
        
        for contributor in all_contributors:
            key = (contributor['contributor_username'], contributor['project_name'])
            if key not in seen:
                seen.add(key)
                unique_contributors.append(contributor)
        
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   ✅ Successfully processed: {successful_orgs} organizations")
        logger.info(f"   ❌ Failed to process: {failed_orgs} organizations")
        logger.info(f"   👥 Total contributors found: {len(all_contributors)}")
        logger.info(f"   🎯 Unique contributors: {len(unique_contributors)}")
        
        # Save to file
        logger.info(f"\n💾 Saving final results to {output_filename}...")
        if output_format.lower() == 'excel':
            self.save_to_excel(unique_contributors, output_filename)
        else:
            self.save_to_csv(unique_contributors, output_filename)
        
        logger.info(f"🎉 Extraction completed successfully!")
        logger.info(f"📁 Final file: {output_filename}")
        
        return output_filename

    def extract_all_contributors(self, output_format: str = 'csv', output_filename: str = None) -> str:
        """Extract contributors from all blockchain repositories (legacy method)"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"blockchain_contributors_{timestamp}.{output_format}"
        
        logger.info("🌟 Starting comprehensive blockchain contributors extraction")
        logger.info(f"📋 Processing {len(self.blockchain_repos)} repositories")
        logger.info(f"💾 Output will be saved to: {output_filename}")
        
        all_contributors = []
        successful_repos = 0
        failed_repos = 0
        
        for i, repo_info in enumerate(self.blockchain_repos, 1):
            repo_name = repo_info['name']
            logger.info(f"\n📁 [{i}/{len(self.blockchain_repos)}] Processing: {repo_name}")
            logger.info("=" * 60)
            
            try:
                repo_contributors = self.process_repository(repo_info)
                all_contributors.extend(repo_contributors)
                successful_repos += 1
                
                # Show cumulative progress
                logger.info(f"📈 Cumulative progress: {len(all_contributors)} contributors from {successful_repos} repositories")
                
                # Save intermediate progress every 5 repositories
                if successful_repos % 5 == 0:
                    self.save_to_csv(all_contributors, f"intermediate_{output_filename}")
                    logger.info(f"💾 Intermediate progress saved to intermediate_{output_filename}")
                
            except Exception as e:
                failed_repos += 1
                logger.error(f"❌ Error processing {repo_info['name']}: {e}")
                continue
        
        # Remove duplicates based on contributor username and project
        logger.info(f"\n🔍 Removing duplicates...")
        unique_contributors = []
        seen = set()
        
        for contributor in all_contributors:
            key = (contributor['contributor_username'], contributor['project_name'])
            if key not in seen:
                seen.add(key)
                unique_contributors.append(contributor)
        
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   ✅ Successfully processed: {successful_repos} repositories")
        logger.info(f"   ❌ Failed to process: {failed_repos} repositories")
        logger.info(f"   👥 Total contributors found: {len(all_contributors)}")
        logger.info(f"   🎯 Unique contributors: {len(unique_contributors)}")
        
        # Save to file
        logger.info(f"\n💾 Saving final results to {output_filename}...")
        if output_format.lower() == 'excel':
            self.save_to_excel(unique_contributors, output_filename)
        else:
            self.save_to_csv(unique_contributors, output_filename)
        
        logger.info(f"🎉 Extraction completed successfully!")
        logger.info(f"📁 Final file: {output_filename}")
        
        return output_filename

def main():
    """Main function to run the contributor extraction"""
    # Check for GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        logger.warning("No GITHUB_TOKEN found in environment variables. Using unauthenticated requests (lower rate limits)")
    
    # Create extractor instance with blockchain CSV data
    extractor = GitHubContributorExtractor(token, blockchain_csv_path='evm_blockchains.csv')
    
    # Extract contributors using the new method with top repositories
    logger.info("🚀 Starting blockchain contributors extraction with top repositories...")
    output_file = extractor.extract_blockchain_contributors_with_top_repos(
        output_format='csv'
        # output_filename will be auto-generated with timestamp
    )
    
    print(f"🎉 Blockchain contributors extraction completed!")
    print(f"📁 Output file: {output_file}")
    print(f"📊 Processed {len(extractor.blockchain_repos)} blockchain organizations")
    print(f"💡 Each organization's top 5 repositories were analyzed for contributors")

if __name__ == "__main__":
    main()