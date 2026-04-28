import json

bad_json = """
{
  "test": "line 1
line 2"
}
"""

try:
    print(json.loads(bad_json, strict=False))
except Exception as e:
    print(f"Error strict=False: {e}")

