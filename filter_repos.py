#!/usr/bin/env python3
"""
Script to filter blockchain repositories for the simple extractor
Keeps max 3 repos per owner and filters for EVM-compatible chains
"""

# Complete repository list from comprehensive extractor
all_repos = [
    {'owner': 'ethereum', 'repo': 'go-ethereum', 'name': 'Ethereum (Geth)'},
    {'owner': 'ethereumjs', 'repo': 'ethereumjs-monorepo', 'name': 'EthereumJS'},
    {'owner': 'ethereum', 'repo': 'py-evm', 'name': 'Python EVM'},
    {'owner': 'ethereum-optimism', 'repo': 'optimism', 'name': 'Optimism'},
    {'owner': 'Microsoft', 'repo': 'eEVM', 'name': 'Microsoft eEVM'},
    {'owner': 'horizontalsystems', 'repo': 'ethereum-kit-android', 'name': 'Ethereum Kit Android'},
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

# Non-EVM compatible chains to remove
non_evm_chains = {
    'bitcoin', 'solana', 'cardano', 'polkadot', 'near', 'cosmos', 'algorand', 
    'ripple', 'stellar', 'tezos', 'filecoin', 'chainalysis', 'hyperledger'
}

# Filter repositories: keep EVM-compatible and limit to 3 per owner
filtered_repos = {}
owner_counts = {}

for repo in all_repos:
    owner = repo['owner']
    
    # Skip non-EVM chains
    if any(non_evm in owner.lower() for non_evm in non_evm_chains):
        continue
    
    # Remove duplicates (same owner/repo combination)
    repo_key = f"{owner}/{repo['repo']}"
    
    # Limit to 3 repos per owner
    if owner not in owner_counts:
        owner_counts[owner] = 0
        filtered_repos[owner] = []
    
    if owner_counts[owner] < 3:
        # Check if this exact repo already exists for this owner
        if not any(r['repo'] == repo['repo'] for r in filtered_repos[owner]):
            filtered_repos[owner].append(repo)
            owner_counts[owner] += 1

# Generate the filtered repository list
final_repos = []
for owner in sorted(filtered_repos.keys()):
    for repo in filtered_repos[owner]:
        final_repos.append(repo)

print(f"Filtered from {len(all_repos)} to {len(final_repos)} repositories")
print(f"Owners: {len(filtered_repos)}")
print("\nFiltered repository list:")
print("self.blockchain_repos = [")
for repo in final_repos:
    print(f"    {{'owner': '{repo['owner']}', 'repo': '{repo['repo']}', 'name': '{repo['name']}'}},")
print("]")