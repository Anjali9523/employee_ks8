##!/bin/bash

# Exit script on any error
#set -e

# Define variables
#IMAGE_NAME="anjalikfti24/employee:latest"
#OPERATOR_IMAGE="anjalikfti24/edge-operator:latest"
#NAMESPACE="employee"

# Build and push the image
#echo "🚀 Building image..."
#podman build -t $IMAGE_NAME .

#echo "📤 Pushing operator image..."
#podman push $OPERATOR_IMAGE

# Apply deployment configuration
#echo "🛠️ Applying Kubernetes manifests..."
#oc apply -f deployment.yaml
#oc apply -f service.yaml
#oc apply -f route.yaml

# Expose the service
#echo "🌐 Exposing service..."
#oc expose service employee-api -n $NAMESPACE

#echo "✅ Deployment complete."

#!/bin/bash

set -e

# Variables
APP_IMAGE="anjalikfti24/employee-api:1.1"
OPERATOR_IMAGE="anjalikfti24/employee-operator:1.1"
NAMESPACE="employee"

#podman tag $APP_IMAGE $OPERATOR_IMAGE

echo "🚀 Building application image..."
podman build -t $APP_IMAGE .

echo "📤 Pushing application image..."
podman push $APP_IMAGE

echo "🚀 Building operator image..."
podman build -f Dockerfile.operator -t $OPERATOR_IMAGE .

echo "📤 Pushing operator image..."
podman push $OPERATOR_IMAGE

echo "🛠️ Creating namespace (if not exists)..."
oc get namespace $NAMESPACE || oc create namespace $NAMESPACE

echo "🛠️ Applying CRD..."
oc apply -f crd.yaml

echo "🛠️ Deploying operator..."
oc apply -f operator-deployment.yaml -n $NAMESPACE

echo "🛠️ Deploying application..."
oc apply -f deployment.yaml -n $NAMESPACE

echo "🌐 Exposing service..."
oc expose service employee-api -n $NAMESPACE

echo "✅ Deployment complete."
