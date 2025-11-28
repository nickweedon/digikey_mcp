#!/usr/bin/env python3
"""Test MyLists API with 3-legged OAuth."""

import sys
import time

# Add current directory to path
sys.path.insert(0, '/workspace')

def test_mylists_with_oauth():
    """Test MyLists API retrieval with auto OAuth."""
    print("=" * 60)
    print("Testing MyLists API with 3-Legged OAuth")
    print("=" * 60)

    # Import the server module
    print(f"\n1. Importing digikey_mcp_server...")
    try:
        import digikey_mcp_server as server
        print(f"   ✓ Module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import: {e}")
        return False

    # Check if auth code file exists
    print(f"\n2. Checking for saved authorization...")
    if server.AUTH_CODE_FILE.exists():
        print(f"   ✓ Auth code file found: {server.AUTH_CODE_FILE}")
        print(f"   ✓ Will use saved authorization")

        # Try to initialize from file
        if server.initialize_user_token_from_file():
            print(f"   ✓ User token initialized from saved auth code")

            # Now try to call get_all_lists
            print(f"\n3. Calling get_all_lists()...")
            try:
                result = server.get_all_lists()
                print(f"   ✓ Successfully retrieved lists!")
                print(f"\n   Result:")

                # Pretty print the result
                import json
                print(json.dumps(result, indent=2))

                # Count lists
                if isinstance(result, list):
                    print(f"\n   📋 Total lists found: {len(result)}")
                    for i, lst in enumerate(result, 1):
                        list_name = lst.get('ListName', 'Unknown')
                        list_id = lst.get('ListId', 'Unknown')
                        print(f"      {i}. {list_name} (ID: {list_id})")
                elif isinstance(result, dict) and 'Lists' in result:
                    lists = result['Lists']
                    print(f"\n   📋 Total lists found: {len(lists)}")
                    for i, lst in enumerate(lists, 1):
                        list_name = lst.get('ListName', 'Unknown')
                        list_id = lst.get('ListId', 'Unknown')
                        print(f"      {i}. {list_name} (ID: {list_id})")

                return True

            except Exception as e:
                print(f"   ✗ Failed to retrieve lists: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"   ⚠ Failed to initialize token from saved auth code")
            print(f"   This may mean the auth code has expired")
            print(f"   Please delete {server.AUTH_CODE_FILE} and run oauth_start_login()")
            return False
    else:
        print(f"   ⚠ No auth code file found: {server.AUTH_CODE_FILE}")
        print(f"\n   To use MyLists API, you need to complete OAuth authorization:")
        print(f"   1. Run: oauth_start_login()")
        print(f"   2. Browser will open automatically")
        print(f"   3. Log in to DigiKey")
        print(f"   4. Accept the browser security warning (self-signed cert)")
        print(f"   5. Authorization code will be saved automatically")
        print(f"   6. Run this test again")
        return False

if __name__ == "__main__":
    try:
        success = test_mylists_with_oauth()
        print("\n" + "=" * 60)
        if success:
            print("✓ MYLISTS TEST PASSED!")
        else:
            print("⚠ MYLISTS TEST INCOMPLETE")
        print("=" * 60)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
