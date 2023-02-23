from kubernetes import client, config
import requests
import time

# Load the Kubernetes configuration
config.load_kube_config()

# Set the namespace and pod name for the WordPress site
namespace = "mwanawevhu-2023"
pod_name = "mwanawevhu-wordpress-56cd7bcff8-f7fht	"

# Create a Kubernetes API client
api = client.CoreV1Api()

# Get the pod object for the WordPress site
pod = api.read_namespaced_pod(pod_name, namespace)

# Get the container object for the WordPress site
container = pod.spec.containers[0]

# Get the CPU and memory usage metrics for the WordPress container
metrics_url = f"http://localhost:8001/apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods/{pod_name}"
metrics_data = requests.get(metrics_url).json()
cpu_usage = metrics_data["containers"][0]["usage"]["cpu"]
memory_usage = metrics_data["containers"][0]["usage"]["memory"]

# Output the CPU and memory usage data
print(f"CPU usage for {container.name}: {cpu_usage}")
print(f"Memory usage for {container.name}: {memory_usage}")

# Send the metrics data to Prometheus or Grafana
prometheus_url = "http://prometheus-server:9090/metrics/job/wordpress"
grafana_url = "http://grafana-server:3000/api/datasources/proxy/1/api/v1/write?db=wordpress"

while True:
    # Get the current timestamp
    current_time = int(time.time())

    # Get the latest CPU and memory usage data
    metrics_data = requests.get(metrics_url).json()
    cpu_usage = metrics_data["containers"][0]["usage"]["cpu"]
    memory_usage = metrics_data["containers"][0]["usage"]["memory"]

    # Send the metrics data to Prometheus or Grafana
    prometheus_data = f"wordpress_cpu_usage{{pod=\"{pod_name}\"}} {cpu_usage} {current_time}"
    requests.post(prometheus_url, data=prometheus_data.encode())
    grafana_data = f"wordpress_cpu_usage,pod={pod_name} value={cpu_usage} {current_time}"
    requests.post(grafana_url, data=grafana_data.encode())

    # Wait for the specified interval before fetching the metrics data again
    time.sleep(60)
