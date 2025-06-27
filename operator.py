import kopf
import kubernetes

@kopf.on.create('mydomain.com', 'v1', 'employeeapis')
def create_fn(spec, **kwargs):
    name = spec.get('name', 'employee-api')
    # Here you can use the Kubernetes API to create deployments, services, etc.
    print(f"Creating Employee API: {name}")
    # Example: create a deployment using kubernetes.client.AppsV1Api
