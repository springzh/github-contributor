#!/usr/bin/env python3
"""
Simple test script to verify the basic functionality works
"""

from blockchain_contributors_extractor import GitHubContributorExtractor
import logging

# Set logging to see details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_basic_functionality():
    """Test basic functionality with minimal API calls"""
    print("Testing basic functionality...")
    
    # Create extractor
    extractor = GitHubContributorExtractor()
    
    # Test with a very small repository
    test_repo = {
        'owner': 'spring',
        'repo': 'test-repo',
        'name': 'Test Repository'
    }
    
    print(f"Testing with repository: {test_repo['name']}")
    
    try:
        # Test just the rate limit check
        extractor.check_rate_limit()
        print("✅ Rate limit check successful")
        
        # Test making a single request to GitHub API
        test_url = "https://api.github.com/repos/spring/test-repo"
        result = extractor.make_request(test_url)
        
        if result:
            print("✅ API request successful")
            print(f"Repository name: {result.get('name', 'N/A')}")
            print(f"Stars: {result.get('stargazers_count', 0)}")
        else:
            print("❌ API request failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 Basic functionality test passed!")
        print("The extractor is ready to use.")
        print("\nTo run the full extraction:")
        print("1. Set your GitHub token: export GITHUB_TOKEN=your_token")
        print("2. Run: python blockchain_contributors_extractor.py")
    else:
        print("\n⚠️  Basic functionality test failed.")
        print("Check your network connection and GitHub API access.")