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
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub contributor extractor
        
        Args:
            token: GitHub personal access token for API authentication
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
        
        # Blockchain repositories to analyze
        self.blockchain_repos = [
            {'owner': 'ethereum', 'repo': 'go-ethereum', 'name': 'Ethereum (Geth)'},
            {'owner': 'ethereumjs', 'repo': 'ethereumjs-monorepo', 'name': 'EthereumJS'},
            {'owner': 'ethereum', 'repo': 'py-evm', 'name': 'Python EVM'},
            {'owner': 'ethereum-optimism', 'repo': 'optimism', 'name': 'Optimism'},
            {'owner': 'Microsoft', 'repo': 'eEVM', 'name': 'Microsoft eEVM'},
            {'owner': 'horizontalsystems', 'repo': 'ethereum-kit-android', 'name': 'Ethereum Kit Android'},
            # Additional major blockchain projects
            {'owner': 'bitcoin', 'repo': 'bitcoin', 'name': 'Bitcoin Core'},
            {'owner': 'solana-labs', 'repo': 'solana', 'name': 'Solana'},
            {'owner': 'cardano-foundation', 'repo': 'cardano-node', 'name': 'Cardano'},
            {'owner': 'polkadot-fellows', 'repo': 'polkadot-sdk', 'name': 'Polkadot'},
            {'owner': 'chainlink', 'repo': 'chainlink', 'name': 'Chainlink'},
            {'owner': 'uniswap', 'repo': 'uniswap-v3-core', 'name': 'Uniswap V3'},
            {'owner': 'aave', 'repo': 'aave-v3-core', 'name': 'Aave V3'},
            {'owner': 'compound-finance', 'repo': 'compound-protocol', 'name': 'Compound'},
            {'owner': 'makerdao', 'repo': 'dss', 'name': 'MakerDAO'},
            {'owner': 'curvefi', 'repo': 'curve-contracts', 'name': 'Curve Finance'},
            {'owner': 'sushiswap', 'repo': 'sushiswap', 'name': 'SushiSwap'},
            {'owner': 'yearn', 'repo': 'yearn-vaults', 'name': 'Yearn Finance'},
            {'owner': '0xProject', 'repo': '0x-monorepo', 'name': '0x Protocol'},
            {'owner': 'arbitrum', 'repo': 'nitro', 'name': 'Arbitrum Nitro'},
            {'owner': 'maticnetwork', 'repo': 'polygon-sdk', 'name': 'Polygon SDK'},
            {'owner': 'avalanche-foundation', 'repo': 'avalanchego', 'name': 'Avalanche Go'},
            {'owner': 'bnb-chain', 'repo': 'bsc', 'name': 'BNB Smart Chain'},
            {'owner': 'near', 'repo': 'nearcore', 'name': 'NEAR Protocol'},
            {'owner': 'cosmos', 'repo': 'cosmos-sdk', 'name': 'Cosmos SDK'},
            {'owner': 'algorand', 'repo': 'go-algorand', 'name': 'Algorand'},
            {'owner': 'ripple', 'repo': 'rippled', 'name': 'Ripple'},
            {'owner': 'stellar', 'repo': 'stellar-core', 'name': 'Stellar'},
            {'owner': 'tezos', 'repo': 'tezos', 'name': 'Tezos'},
            {'owner': 'filecoin-project', 'repo': 'lotus', 'name': 'Filecoin'},
            {'owner': 'graphprotocol', 'repo': 'graph-node', 'name': 'The Graph'},
            {'owner': 'chainalysis', 'repo': 'chainalysis-api', 'name': 'Chainalysis'},
            {'owner': 'consensys', 'repo': 'goquorum', 'name': 'ConsenSys Quorum'},
            {'owner': 'hyperledger', 'repo': 'fabric', 'name': 'Hyperledger Fabric'},
            {'owner': 'hyperledger', 'repo': 'indy', 'name': 'Hyperledger Indy'},
            {'owner': 'hyperledger', 'repo': 'iroha', 'name': 'Hyperledger Iroha'},
            {'owner': 'hyperledger', 'repo': 'sawtooth', 'name': 'Hyperledger Sawtooth'},
            {'owner': 'paritytech', 'repo': 'substrate', 'name': 'Substrate'},
            {'owner': 'web3j', 'repo': 'web3j', 'name': 'Web3j'},
            {'owner': 'trufflesuite', 'repo': 'truffle', 'name': 'Truffle'},
            {'owner': 'OpenZeppelin', 'repo': 'openzeppelin-contracts', 'name': 'OpenZeppelin Contracts'},
            {'owner': 'hardhat', 'repo': 'hardhat', 'name': 'Hardhat'},
            {'owner': 'foundry-rs', 'repo': 'foundry', 'name': 'Foundry'},
            {'owner': 'remix-project', 'repo': 'remix-ide', 'name': 'Remix IDE'},
            {'owner': 'metamask', 'repo': 'metamask-extension', 'name': 'MetaMask'},
            {'owner': 'walletconnect', 'repo': 'walletconnect-monorepo', 'name': 'WalletConnect'},
            {'owner': 'ethereum', 'repo': 'EIPs', 'name': 'Ethereum Improvement Proposals'},
            {'owner': 'ethereum', 'repo': 'eth2.0-specs', 'name': 'Ethereum 2.0 Specs'},
            {'owner': 'ethereum', 'repo': 'solidity', 'name': 'Solidity'},
            {'owner': 'vyperlang', 'repo': 'vyper', 'name': 'Vyper'},
            {'owner': 'nomiclabs', 'repo': 'hardhat-waffle', 'name': 'Hardhat Waffle'},
            {'owner': 'ethers-io', 'repo': 'ethers.js', 'name': 'Ethers.js'},
            {'owner': 'web3', 'repo': 'web3.js', 'name': 'Web3.js'},
            {'owner': 'brownie-mix', 'repo': 'brownie', 'name': 'Brownie'},
            {'owner': 'a16z', 'repo': 'erc721a', 'name': 'ERC721A'},
            {'owner': 'ProjectOpenSea', 'repo': 'opensea-js', 'name': 'OpenSea JS'},
            {'owner': 'uniswap', 'repo': 'v2-core', 'name': 'Uniswap V2'},
            {'owner': 'uniswap', 'repo': 'v2-periphery', 'name': 'Uniswap V2 Periphery'},
            {'owner': 'uniswap', 'repo': 'v3-periphery', 'name': 'Uniswap V3 Periphery'},
            {'owner': 'uniswap', 'repo': 'universal-router', 'name': 'Uniswap Universal Router'},
            {'owner': 'aave', 'repo': 'aave-protocol', 'name': 'Aave Protocol'},
            {'owner': 'aave', 'repo': 'aave-v2-core', 'name': 'Aave V2 Core'},
            {'owner': 'compound-finance', 'repo': 'compound-protocol', 'name': 'Compound Protocol'},
            {'owner': 'compound-finance', 'repo': 'compound-money-market', 'name': 'Compound Money Market'},
            {'owner': 'makerdao', 'repo': 'dss', 'name': 'MakerDAO DSS'},
            {'owner': 'makerdao', 'repo': 'multicall', 'name': 'MakerDAO Multicall'},
            {'owner': 'curvefi', 'repo': 'curve-contracts', 'name': 'Curve Contracts'},
            {'owner': 'curvefi', 'repo': 'curve-dao-contracts', 'name': 'Curve DAO Contracts'},
            {'owner': 'sushiswap', 'repo': 'sushiswap', 'name': 'SushiSwap'},
            {'owner': 'sushiswap', 'repo': 'sushiswap-interface', 'name': 'SushiSwap Interface'},
            {'owner': 'yearn', 'repo': 'yearn-vaults', 'name': 'Yearn Vaults'},
            {'owner': 'yearn', 'repo': 'yearn-strategy', 'name': 'Yearn Strategy'},
            {'owner': '0xProject', 'repo': '0x-monorepo', 'name': '0x Protocol'},
            {'owner': '0xProject', 'repo': '0x-protocol', 'name': '0x Protocol'},
            {'owner': 'arbitrum', 'repo': 'nitro', 'name': 'Arbitrum Nitro'},
            {'owner': 'arbitrum', 'repo': 'arbitrum', 'name': 'Arbitrum One'},
            {'owner': 'maticnetwork', 'repo': 'polygon-sdk', 'name': 'Polygon SDK'},
            {'owner': 'maticnetwork', 'repo': 'bor', 'name': 'Polygon Bor'},
            {'owner': 'maticnetwork', 'repo': 'heimdall', 'name': 'Polygon Heimdall'},
            {'owner': 'avalanche-foundation', 'repo': 'avalanchego', 'name': 'Avalanche Go'},
            {'owner': 'avalanche-foundation', 'repo': 'subnet-evm', 'name': 'Avalanche Subnet EVM'},
            {'owner': 'bnb-chain', 'repo': 'bsc', 'name': 'BNB Smart Chain'},
            {'owner': 'bnb-chain', 'repo': 'bsc-genesis-contract', 'name': 'BNB Smart Chain Genesis'},
            {'owner': 'near', 'repo': 'nearcore', 'name': 'NEAR Core'},
            {'owner': 'near', 'repo': 'near-sdk-rs', 'name': 'NEAR SDK Rust'},
            {'owner': 'cosmos', 'repo': 'cosmos-sdk', 'name': 'Cosmos SDK'},
            {'owner': 'cosmos', 'repo': 'gaia', 'name': 'Cosmos Gaia'},
            {'owner': 'algorand', 'repo': 'go-algorand', 'name': 'Algorand Go'},
            {'owner': 'algorand', 'repo': 'py-algorand-sdk', 'name': 'Algorand Python SDK'},
            {'owner': 'ripple', 'repo': 'rippled', 'name': 'Ripple'},
            {'owner': 'ripple', 'repo': 'rippled-historical-database', 'name': 'Ripple Historical'},
            {'owner': 'stellar', 'repo': 'stellar-core', 'name': 'Stellar Core'},
            {'owner': 'stellar', 'repo': 'stellar-sdk', 'name': 'Stellar SDK'},
            {'owner': 'tezos', 'repo': 'tezos', 'name': 'Tezos'},
            {'owner': 'tezos', 'repo': 'tezos-sdk', 'name': 'Tezos SDK'},
            {'owner': 'filecoin-project', 'repo': 'lotus', 'name': 'Filecoin Lotus'},
            {'owner': 'filecoin-project', 'repo': 'go-filecoin', 'name': 'Filecoin Go'},
            {'owner': 'graphprotocol', 'repo': 'graph-node', 'name': 'The Graph Node'},
            {'owner': 'graphprotocol', 'repo': 'graph-client', 'name': 'The Graph Client'},
            {'owner': 'chainalysis', 'repo': 'chainalysis-api', 'name': 'Chainalysis API'},
            {'owner': 'consensys', 'repo': 'goquorum', 'name': 'ConsenSys Quorum'},
            {'owner': 'consensys', 'repo': 'teku', 'name': 'ConsenSys Teku'},
            {'owner': 'hyperledger', 'repo': 'fabric', 'name': 'Hyperledger Fabric'},
            {'owner': 'hyperledger', 'repo': 'indy', 'name': 'Hyperledger Indy'},
            {'owner': 'hyperledger', 'repo': 'iroha', 'name': 'Hyperledger Iroha'},
            {'owner': 'hyperledger', 'repo': 'sawtooth', 'name': 'Hyperledger Sawtooth'},
            {'owner': 'paritytech', 'repo': 'substrate', 'name': 'Substrate'},
            {'owner': 'paritytech', 'repo': 'polkadot', 'name': 'Polkadot'},
            {'owner': 'web3j', 'repo': 'web3j', 'name': 'Web3j'},
            {'owner': 'web3j', 'repo': 'web3j-gradle-plugin', 'name': 'Web3j Gradle Plugin'},
            {'owner': 'trufflesuite', 'repo': 'truffle', 'name': 'Truffle'},
            {'owner': 'trufflesuite', 'repo': 'ganache', 'name': 'Ganache'},
            {'owner': 'OpenZeppelin', 'repo': 'openzeppelin-contracts', 'name': 'OpenZeppelin Contracts'},
            {'owner': 'OpenZeppelin', 'repo': 'openzeppelin-sdk', 'name': 'OpenZeppelin SDK'},
            {'owner': 'hardhat', 'repo': 'hardhat', 'name': 'Hardhat'},
            {'owner': 'hardhat', 'repo': 'hardhat-deploy', 'name': 'Hardhat Deploy'},
            {'owner': 'foundry-rs', 'repo': 'foundry', 'name': 'Foundry'},
            {'owner': 'foundry-rs', 'repo': 'foundry-up', 'name': 'Foundry Up'},
            {'owner': 'remix-project', 'repo': 'remix-ide', 'name': 'Remix IDE'},
            {'owner': 'remix-project', 'repo': 'remix-desktop', 'name': 'Remix Desktop'},
            {'owner': 'metamask', 'repo': 'metamask-extension', 'name': 'MetaMask Extension'},
            {'owner': 'metamask', 'repo': 'metamask-mobile', 'name': 'MetaMask Mobile'},
            {'owner': 'walletconnect', 'repo': 'walletconnect-monorepo', 'name': 'WalletConnect'},
            {'owner': 'walletconnect', 'repo': 'walletconnect-web3-provider', 'name': 'WalletConnect Provider'},
        ]

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

    def extract_all_contributors(self, output_format: str = 'csv', output_filename: str = None) -> str:
        """Extract contributors from all blockchain repositories"""
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
    
    # Create extractor instance
    extractor = GitHubContributorExtractor(token)
    
    # Extract contributors
    output_file = extractor.extract_all_contributors(
        output_format='csv',
        output_filename='blockchain_contributors.csv'
    )
    
    print(f"Contributor data saved to: {output_file}")
    print(f"Total contributors extracted: {len(extractor.blockchain_repos)} repositories processed")

if __name__ == "__main__":
    main()