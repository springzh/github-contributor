# Simple GitHub Blockchain Contributors Extractor

A streamlined Python script that extracts contributor information from major EVM-compatible blockchain GitHub repositories and saves the data to CSV files.

## Features

- **EVM-Compatible Focus**: Only extracts from EVM-compatible blockchain projects
- **Comprehensive Coverage**: 64 repositories from 36 different owners (max 3 per owner)
- **Top Contributors**: Extracts top 3 contributors per repository
- **Deduplication**: Automatically removes duplicate contributors across repositories
- **CSV-Safe**: Excludes bio field to prevent CSV formatting issues
- **Rate Limit Protection**: Built-in delays to avoid GitHub API rate limits
- **Progress Tracking**: Real-time logging of extraction progress
- **Detailed Information**: Collects profile URLs, emails, social media, and contribution stats

## Data Collected

For each contributor, the script extracts:
- **Profile Information**: Username, name, email, profile URL
- **Social Media**: Twitter handle, website/blog links
- **Professional Details**: Location, company
- **GitHub Statistics**: Contributions, followers, following, public repositories
- **Account Information**: Account creation and last update dates
- **Project Association**: Which repository they contributed to

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get GitHub API token (recommended):**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with `public_repo` scope
   - Set as environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

## Usage

### Basic Usage
```bash
python simple_extractor.py
```

### Custom Usage
```python
from simple_extractor import SimpleGitHubExtractor

# Create extractor with token
extractor = SimpleGitHubExtractor(token="your_github_token")

# Extract contributors to CSV
output_file = extractor.run_extraction(
    max_contributors_per_repo=3,
    output_file='custom_blockchain_contributors.csv'
)

print(f"Data saved to: {output_file}")
```

### Available Options
- `max_contributors_per_repo`: Number of top contributors to extract per repository (default: 3)
- `output_file`: Custom output file name

## Output Data

The script generates a CSV file with the following columns:

- **Project Information**: `project_name`, `project_url`
- **Contributor Profile**: `contributor_username`, `contributor_url`, `contributor_name`, `contributor_email`
- **Social Media**: `twitter`, `website`
- **Professional Info**: `location`, `company`
- **GitHub Stats**: `contributions`, `followers`, `following`, `public_repos`
- **Account Info**: `account_created`, `last_updated`

## Included Repositories

The script includes **64 EVM-compatible repositories** from **36 different owners**, covering:

### Core EVM Blockchains
- **Ethereum**: go-ethereum, py-evm, EIPs
- **Layer 2**: Optimism, Arbitrum, Polygon, Avalanche, BNB Smart Chain
- **Enterprise**: ConsenSys Quorum, Microsoft eEVM

### DeFi Protocols
- **DEXs**: Uniswap (V2, V3), SushiSwap, 0x Protocol, Curve Finance
- **Lending**: Aave (V2, V3), Compound, MakerDAO
- **Yield**: Yearn Finance

### Infrastructure
- **Oracles**: Chainlink
- **Indexing**: The Graph
- **Standards**: OpenZeppelin Contracts
- **Development**: ERC721A (a16z)

### Development Tools
- **Frameworks**: Hardhat, Foundry, Truffle, Brownie
- **Languages**: Solidity, Vyper
- **Libraries**: Web3.js, Ethers.js, Web3j
- **IDEs**: Remix IDE
- **Testing**: Ganache, Hardhat Waffle

### Wallets & Connectivity
- **Wallets**: MetaMask
- **Connections**: WalletConnect

### Mobile & SDKs
- **Mobile**: Ethereum Kit Android, MetaMask Mobile
- **SDKs**: Polygon SDK, Avalanche Subnet EVM

**Key Statistics:**
- **Total Repositories**: 64
- **Unique Owners**: 36 (limited to max 3 per owner)
- **Max Contributors**: ~192 (3 per repository)
- **Non-EVM Chains Removed**: Bitcoin, Solana, Cardano, Polkadot, Cosmos, Algorand, Ripple, Stellar, Tezos, Filecoin, etc.

## Rate Limiting & Performance

The script includes comprehensive rate limiting:
- **Request Delays**: 2-second minimum delay between API requests
- **User Profile Delays**: 1-second delay between user profile requests
- **Repository Delays**: 2-second delay between repositories
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour
- **Estimated Runtime**: ~15-20 minutes with authentication

## Progress Tracking

The script provides detailed progress information:
- Repository processing status
- Contributors found per repository
- Real-time sample contributor data display
- Duplicate contributor warnings
- Cumulative progress statistics
- Final extraction summary

## Error Handling

- **SSL Error Protection**: Automatic retry with exponential backoff
- **Connection Error Recovery**: Handles network interruptions gracefully
- **Rate Limit Detection**: Pauses when approaching API limits
- **Repository Isolation**: Failed repositories don't stop entire extraction
- **Duplicate Prevention**: Skips contributors already processed

## Deduplication

The script automatically handles duplicate contributors:
- **Username Tracking**: Maintains set of processed usernames
- **Cross-Repository Deduplication**: Same contributor appears only once
- **Duplicate Warnings**: Logs when duplicates are skipped
- **Unique Contributor Count**: Reports final unique contributor total

## Notes

- **GitHub Token Recommended**: Without token, limited to 60 requests/hour
- **CSV Format**: Bio field excluded to prevent CSV formatting issues
- **EVM Focus**: Non-EVM chains intentionally excluded for relevance
- **Repository Limit**: Maximum 3 repositories per owner to ensure diversity
- **Data Quality**: Only includes actual user accounts (excludes bots)

## Requirements

- Python 3.7+
- requests >= 2.28.0
- pandas >= 1.5.0 (optional, for Excel export)
- openpyxl >= 3.0.0 (optional, for Excel export)

## Files

- `simple_extractor.py` - Main extraction script
- `requirements.txt` - Python dependencies
- `filter_repos.py` - Repository filtering script (for reference)
- `blockchain_contributors_simple.csv` - Default output file