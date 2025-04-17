# Load Testing

Load testing with `locust`

##  Install locust

```
pip install locust
```

## Run Locust with your API Server base URL

```
locust -f llm_load_test.py --host=https://your-server-base-url
```

## Open the Locust web interface 
Web interface usually at http://localhost:8089 and configure:

- Number of users
- Spawn rate
- Click "Start swarming"
