#!/usr/bin/env python3
"""
Test script for extracting contributors from a single repository
"""

from blockchain_contributors_extractor import GitHubContributorExtractor
import logging

# Set logging to see more details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_single_repo():
    """Test extracting contributors from a single repository"""
    print("Testing single repository contributor extraction...")
    
    # Create extractor
    extractor = GitHubContributorExtractor()
    
    # Test with a smaller repository first
    test_repo = {
        'owner': 'ethereum',
        'repo': 'py-evm',
        'name': 'Python EVM'
    }
    
    print(f"Testing with repository: {test_repo['name']}")
    
    try:
        contributors = extractor.process_repository(test_repo)
        print(f"✅ Successfully extracted {len(contributors)} contributors")
        
        if contributors:
            print("\nSample contributor data:")
            sample = contributors[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
        # Save test results
        extractor.save_to_csv(contributors, 'test_contributors.csv')
        print(f"✅ Test results saved to test_contributors.csv")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_single_repo()
    if success:
        print("\n🎉 Test passed! The extractor is working correctly.")
    else:
        print("\n⚠️  Test failed. Check the error messages above.")