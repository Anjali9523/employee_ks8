#!/bin/bash

set -e

# Variables
APP_IMAGE="anjalikfti24/employee-api:1.2"
OPERATOR_IMAGE="anjalikfti24/employee-operator:1.2"
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
