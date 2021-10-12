{ time python3 test_basic_requirements.py "$SERVER_HOST"; } >"./benchmark-test_basic_requirements-$(date -d now +"%Y-%m-%dT%H%M%S").log" 2>&1
