{ time python3 test_basic_requirements.py "$SERVER_HOST"; } >"./benchmark-test_basic_requirements-$(date -d now +"%Y-%m-%dT%H%M%S").log" 2>&1

conn_count=10
while [ $conn_count -lt 100 ]; do
  if ! python3 test_stress.py "$SERVER_HOST" 9889 $conn_count >"./benchmark-test_stress-$conn_count-$(date -d now +"%Y-%m-%dT%H%M%S").log" 2>&1
  then
    echo "benchmark couldn't handle $conn_count connections"
    exit 1
  fi
  conn_count=$((conn_count + 10))
done
