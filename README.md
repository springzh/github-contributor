# GitHub Blockchain Contributors Extractor

A Python script that extracts contributor information from major blockchain GitHub repositories and saves the data to CSV or Excel files.

## Features

- Extracts contributor data from 100+ major blockchain repositories
- Collects detailed contributor information including:
  - Profile URL, name, email
  - Twitter, LinkedIn, website links
  - Location, company, bio
  - Contribution statistics
  - Account creation and update dates
- Supports both CSV and Excel export formats
- Includes rate limiting and error handling for GitHub API
- Comprehensive repository list covering major blockchain projects

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
python blockchain_contributors_extractor.py
```

### Custom Output
```python
from blockchain_contributors_extractor import GitHubContributorExtractor

# Create extractor with token
extractor = GitHubContributorExtractor(token="your_github_token")

# Extract contributors to CSV
output_file = extractor.extract_all_contributors(
    output_format='csv',
    output_filename='custom_blockchain_contributors.csv'
)

print(f"Data saved to: {output_file}")
```

### Available Options
- `output_format`: 'csv' or 'excel'
- `output_filename`: Custom output file name

## Output Data

The script generates a comprehensive dataset with the following columns:

- **Project Information**: `project_name`, `project_url`
- **Contributor Profile**: `contributor_username`, `contributor_url`, `contributor_name`, `contributor_email`
- **Social Media**: `twitter`, `linkedin`, `website`, `blog`
- **Professional Info**: `location`, `company`, `bio`
- **GitHub Stats**: `contributions`, `followers`, `following`, `public_repos`
- **Account Info**: `account_created`, `last_updated`

## Rate Limiting

The script includes automatic rate limiting:
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour
- Automatic pause when approaching limits
- Respectful delays between requests

## Included Repositories

The script includes 100+ major blockchain repositories covering:

- **Core Blockchains**: Bitcoin, Ethereum, Solana, Cardano, Polkadot, etc.
- **Layer 2 Solutions**: Arbitrum, Optimism, Polygon, Avalanche, etc.
- **DeFi Protocols**: Uniswap, Aave, Compound, Curve, Yearn, etc.
- **Infrastructure**: Chainlink, The Graph, Filecoin, etc.
- **Development Tools**: OpenZeppelin, Hardhat, Foundry, Truffle, etc.
- **Wallets**: MetaMask, WalletConnect, etc.

## Error Handling

- Graceful handling of API errors
- Automatic retries for failed requests
- Comprehensive logging
- Repository-specific error isolation

## Notes

- Without a GitHub token, you'll be limited to 60 requests/hour
- The script may take several hours to complete due to API rate limits
- Some repositories may have thousands of contributors
- Data is automatically deduplicated based on username and project

## Requirements

- Python 3.7+
- requests
- pandas (for Excel export)
- openpyxl (for Excel export)