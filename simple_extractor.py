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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleGitHubExtractor:
    def __init__(self, token: Optional[str] = None):
        """Initialize the extractor with optional GitHub token"""
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
        
        # Filtered blockchain repositories (EVM-compatible, max 3 per owner)
        self.blockchain_repos = [
            {'owner': '0xProject', 'repo': '0x-monorepo', 'name': '0x Protocol'},
            {'owner': '0xProject', 'repo': '0x-protocol', 'name': '0x Protocol'},
            {'owner': 'Microsoft', 'repo': 'eEVM', 'name': 'Microsoft eEVM'},
            {'owner': 'OpenZeppelin', 'repo': 'openzeppelin-contracts', 'name': 'OpenZeppelin Contracts'},
            {'owner': 'OpenZeppelin', 'repo': 'openzeppelin-sdk', 'name': 'OpenZeppelin SDK'},
            {'owner': 'ProjectOpenSea', 'repo': 'opensea-js', 'name': 'OpenSea JS'},
            {'owner': 'a16z', 'repo': 'erc721a', 'name': 'ERC721A'},
            {'owner': 'aave', 'repo': 'aave-v3-core', 'name': 'Aave V3'},
            {'owner': 'aave', 'repo': 'aave-protocol', 'name': 'Aave Protocol'},
            {'owner': 'aave', 'repo': 'aave-v2-core', 'name': 'Aave V2 Core'},
            {'owner': 'arbitrum', 'repo': 'nitro', 'name': 'Arbitrum Nitro'},
            {'owner': 'arbitrum', 'repo': 'arbitrum', 'name': 'Arbitrum One'},
            {'owner': 'avalanche-foundation', 'repo': 'avalanchego', 'name': 'Avalanche Go'},
            {'owner': 'avalanche-foundation', 'repo': 'subnet-evm', 'name': 'Avalanche Subnet EVM'},
            {'owner': 'bnb-chain', 'repo': 'bsc', 'name': 'BNB Smart Chain'},
            {'owner': 'bnb-chain', 'repo': 'bsc-genesis-contract', 'name': 'BNB Smart Chain Genesis'},
            {'owner': 'brownie-mix', 'repo': 'brownie', 'name': 'Brownie'},
            {'owner': 'chainlink', 'repo': 'chainlink', 'name': 'Chainlink'},
            {'owner': 'compound-finance', 'repo': 'compound-protocol', 'name': 'Compound'},
            {'owner': 'compound-finance', 'repo': 'compound-money-market', 'name': 'Compound Money Market'},
            {'owner': 'consensys', 'repo': 'goquorum', 'name': 'ConsenSys Quorum'},
            {'owner': 'consensys', 'repo': 'teku', 'name': 'ConsenSys Teku'},
            {'owner': 'curvefi', 'repo': 'curve-contracts', 'name': 'Curve Finance'},
            {'owner': 'curvefi', 'repo': 'curve-dao-contracts', 'name': 'Curve DAO Contracts'},
            {'owner': 'ethereum', 'repo': 'go-ethereum', 'name': 'Ethereum (Geth)'},
            {'owner': 'ethereum', 'repo': 'py-evm', 'name': 'Python EVM'},
            {'owner': 'ethereum', 'repo': 'EIPs', 'name': 'Ethereum Improvement Proposals'},
            {'owner': 'ethereum-optimism', 'repo': 'optimism', 'name': 'Optimism'},
            {'owner': 'ethereumjs', 'repo': 'ethereumjs-monorepo', 'name': 'EthereumJS'},
            {'owner': 'ethers-io', 'repo': 'ethers.js', 'name': 'Ethers.js'},
            {'owner': 'foundry-rs', 'repo': 'foundry', 'name': 'Foundry'},
            {'owner': 'foundry-rs', 'repo': 'foundry-up', 'name': 'Foundry Up'},
            {'owner': 'graphprotocol', 'repo': 'graph-node', 'name': 'The Graph'},
            {'owner': 'graphprotocol', 'repo': 'graph-client', 'name': 'The Graph Client'},
            {'owner': 'hardhat', 'repo': 'hardhat', 'name': 'Hardhat'},
            {'owner': 'hardhat', 'repo': 'hardhat-deploy', 'name': 'Hardhat Deploy'},
            {'owner': 'horizontalsystems', 'repo': 'ethereum-kit-android', 'name': 'Ethereum Kit Android'},
            {'owner': 'makerdao', 'repo': 'dss', 'name': 'MakerDAO'},
            {'owner': 'makerdao', 'repo': 'multicall', 'name': 'MakerDAO Multicall'},
            {'owner': 'maticnetwork', 'repo': 'polygon-sdk', 'name': 'Polygon SDK'},
            {'owner': 'maticnetwork', 'repo': 'bor', 'name': 'Polygon Bor'},
            {'owner': 'maticnetwork', 'repo': 'heimdall', 'name': 'Polygon Heimdall'},
            {'owner': 'metamask', 'repo': 'metamask-extension', 'name': 'MetaMask'},
            {'owner': 'metamask', 'repo': 'metamask-mobile', 'name': 'MetaMask Mobile'},
            {'owner': 'nomiclabs', 'repo': 'hardhat-waffle', 'name': 'Hardhat Waffle'},
            {'owner': 'paritytech', 'repo': 'substrate', 'name': 'Substrate'},
            {'owner': 'paritytech', 'repo': 'polkadot', 'name': 'Polkadot'},
            {'owner': 'remix-project', 'repo': 'remix-ide', 'name': 'Remix IDE'},
            {'owner': 'remix-project', 'repo': 'remix-desktop', 'name': 'Remix Desktop'},
            {'owner': 'sushiswap', 'repo': 'sushiswap', 'name': 'SushiSwap'},
            {'owner': 'sushiswap', 'repo': 'sushiswap-interface', 'name': 'SushiSwap Interface'},
            {'owner': 'trufflesuite', 'repo': 'truffle', 'name': 'Truffle'},
            {'owner': 'trufflesuite', 'repo': 'ganache', 'name': 'Ganache'},
            {'owner': 'uniswap', 'repo': 'uniswap-v3-core', 'name': 'Uniswap V3'},
            {'owner': 'uniswap', 'repo': 'v2-core', 'name': 'Uniswap V2'},
            {'owner': 'uniswap', 'repo': 'v2-periphery', 'name': 'Uniswap V2 Periphery'},
            {'owner': 'vyperlang', 'repo': 'vyper', 'name': 'Vyper'},
            {'owner': 'walletconnect', 'repo': 'walletconnect-monorepo', 'name': 'WalletConnect'},
            {'owner': 'walletconnect', 'repo': 'walletconnect-web3-provider', 'name': 'WalletConnect Provider'},
            {'owner': 'web3', 'repo': 'web3.js', 'name': 'Web3.js'},
            {'owner': 'web3j', 'repo': 'web3j', 'name': 'Web3j'},
            {'owner': 'web3j', 'repo': 'web3j-gradle-plugin', 'name': 'Web3j Gradle Plugin'},
            {'owner': 'yearn', 'repo': 'yearn-vaults', 'name': 'Yearn Finance'},
            {'owner': 'yearn', 'repo': 'yearn-strategy', 'name': 'Yearn Strategy'},
        ]

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
        
        fieldnames = [
            'project_name', 'project_url', 'contributor_username', 'contributor_url',
            'contributor_name', 'contributor_email', 'contributions', 'twitter',
            'website', 'location', 'company', 'followers', 'following',
            'public_repos', 'account_created', 'last_updated'
        ]
        
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
    
    # Create extractor
    extractor = SimpleGitHubExtractor(token)
    
    # Run extraction with top 3 contributors per repo
    print("📊 Extracting top 3 contributors from EVM-compatible blockchain repositories...")
    output_file = extractor.run_extraction(
        max_contributors_per_repo=3,  # Get top 3 contributors per repo
        output_file='blockchain_contributors_simple.csv'
    )
    
    print(f"\n✅ Extraction completed!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📈 Total repositories processed: {len(extractor.blockchain_repos)}")
    print(f"🔥 EVM-compatible repositories only (max 3 per owner)")

if __name__ == "__main__":
    main()