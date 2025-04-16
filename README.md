# vllm-granite
Artifacts to build and deploy a container with vLLM and granite, exposed via REST APIs

##  <a id="vllm-with-granite">vLLM container with IBM Granite</a>

The following command builds a vLLM container image which pulls Granite models from HuggingFace. It uses the [official vLLM image](https://hub.docker.com/r/vllm/vllm-openai/tags) as base.  

Please note: the `Dockerfile` uses the `latest` tag, which points to the most up-to-date tag available.  Internally we have tested with version `v0.8.3`.

```
docker buildx build --tag vllm_with_model -f Dockerfile.model --build-arg model_id=ibm-granite/granite-3.1-8b-instruct .
```

## OpenAI-Compatible Server with vLLM
vLLM provides an HTTP server that implements OpenAI’s Completions API, Chat API, and more!

- You can start the server by running the image (Reference: https://docs.vllm.ai/en/latest/deployment/docker.html#deployment-docker):
```
docker run --runtime nvidia --gpus all \
-p 8000:8000 \
--ipc=host \
vllm_with_model:latest
```

- Once the server is started, you can check the Swagger API Documentation page hosted on `http://[hostname]:8000/docs`, or 
reference Supported API endpoints listed here: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#supported-apis, for example:
  - Chat Completions API (/v1/chat/completions)
  - Completions API (/v1/completions)
  - Embeddings API (/v1/embeddings)

-----
# OCP Cluster for Self-Hosting LLM with vLLM

## 1. Cluster Setup

### 1.1. Prerequisites

To use the OCP Cluster with NVIDIA GPUs, you need to have GPU resources attached to your cluster. Confirm that you have attached GPUs to some worker node(s) in your cluster. 

### 1.2. Installing Operators

For the cluster to identify and use the NVIDIA GPUs, you need to install a few operators onto the cluster. 

1. [Node Discovery Feature Operator](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/specialized_hardware_and_driver_enablement/psap-node-feature-discovery-operator#creating-nfd-cr-web-console_psap-node-feature-discovery-operator)
2. [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/install-gpu-ocp.html)
3. Confirm that the NDF and NVIDIA Operators are installed and configured correctly.
   - You can view this either via web console or CLI.
   - Check that each worker node with GPUs has the following labels:
     - `nvidia.com/gpu.present=true`
     - `nvidia.com/gpu.product=<NVIDIA_GPU_Model>`
   - Take note of all NVIDIA GPU model names. You will need them later.
  
### 1.3. Setting up Cluster Storage

1. Install the cert manager.
     ```
     oc apply -f https://github.com/jetstack/cert-manager/releases/download/v1.11.1/cert-manager.yaml
     ```
2. Clone the `rook-ceps` repository and change directory into the `/examples` directory.
     ```
     git clone --single-branch --branch v1.11.4 https://github.com/rook/rook.git
     cd rook/deploy/examples
     ```
3. Run each line. (Or copy this into a script with `#!/bin/bash` as the first line, and run it.)
     ```
     oc create -f common.yaml
     oc create -f crds.yaml
     oc create -f operator-openshift.yaml
     oc -n rook-ceph get pod
     oc create -f cluster.yaml
     oc create -f csi/rbd/storageclass.yaml
     oc patch storageclass rook-ceph-block -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
     oc create -f filesystem.yaml
     oc create -f csi/cephfs/storageclass.yaml
     ```

## 2. vLLM Setup

1. Login to your cluster via a terminal.
   - Either get a login token command from the web console.
      - Click on the user in the top right to show the user menu.
      - Click on `Copy login command` (opens a new tab)
      - Click on `Display Token` and use the provided login command. (You can also get the cluster api url here)
   - Or log in with the cluster credentials
      ```
      oc login <cluster_api_url_and_port> -u <username> -p <password>
      ```
2. Update and apply the pre-packaged sample YAML file.
   - **NOTE:** For AirGap or OnPrem environments:
     - If you are planning to use vLLM images shipped with previously downloaded models, follow these [instructions](#vllm-with-granite).
     - Then follow Step 6 in these [additional instructions](#build-image-in-ocp).
   - Make sure to update any values to match your own specifications and requirements. There are a few `<fields>` that require your custom input.
   - To apply a YAML file:
     ```
     oc apply -f <yaml_file>
     ```
3. Switch the the new namespace defined in the YAML.
   ```
   oc project <namespace>
   ```
5. Add pod privilege to the service account defined in the YAML.
   ```
   oc adm policy add-scc-to-user privileged -z <service_account>
   ```
   - Check that there are pods running in the deployment. If there are none, restart/reapply the deployment.
     ```
     oc get pods
     ```
6. Expose the vLLM for external access.
     ```
     # Get the service name
     oc get svc
     
     # Expose the service
     oc expose svc <service_name>
     ```
   - For viewing, you can get the host URL with
     ```
     # Get the host url
     oc get route | grep <service_name> 
     ```
7. To make any changes to the deployment, just modify the YAML and re-apply.

## 3. Using the vLLM service

### Simple method to send prompts to the service

1. Get the service name and port.
     ```
     oc get svc
     ```
2. Get the pod name.
     ```
     oc get pods
     ```
3. Run a sample prompt.
     ```
     oc exec -it <pod-name> \
             -- curl -X POST "http://<service_name>:<service_port>/v1/completions" \
             -H "Content-Type: application/json" \
             -d '{"model": "<model_name>", "prompt": "<sample_prompt>", "max_tokens": <token_count>}'
     ```

## 4. Grafana Dashboard for vLLM metrics

[Setup instructions](#grafana-prometheus).

1. Visit the Grafana URL and login. Get the credentials from the setup.
   - You can find the URL in the web console.
     - Navigate from the left-hand menu to `Networking` -> `Routes`, switch to `All Projects`, and search for Grafana.
     - The host URL is under the `Location` column.
3. Goto Dashboards, and either view an existing one, or create a new one.
    - For persistent dashboards, create one via the Grafana Operator in OCP.
4. (Optional) Get a new access token
    - When viewing the dashboards, if the UI is giving "Unauthorized" type error, your access token may have expired. 
    - Go through the setup instructions to set a new access token.

-----
## <a id="appendix">Appendix</a>

### <a id="build-image-in-ocp">A. Building the vLLM Docker image within OCP</a>

If you already have an available image, skip over to Step 6.

1. Change directory to the `Dockerfile` via the terminal.
    ```
    cd /path/to/Dockerfile
    ```
2. Create a build config.
    ```
    oc new-build --name=<config_name> --binary --strategy=docker 
    ```
3. Start the build.
    ```
    oc start-build <config_name> --from-dir=.
    ```
4. (Optional) Verify that the build image has been pushed.
    ```
    # Check that the build exists
    oc get builds | grep <config_name>
  
    # Get the pod name of the build - should be named in the format: "<config_name-#>-build"
    oc get pods | grep <config_name>
    
    # Check the logs for the message "Push successful"
    oc logs <pod_name> -f
    
    # Check for the pushed image
    oc get istag <config_name>:latest
    ```
5. Get the image url and version.
    ```
    # Image name should be in the format: "image-registry.openshift-image-registry.svc:5000/<namespace>/<config_name>"
    oc get imagestreams | grep <config_name>
    ```
6. In the sample YAML, under the the `spec: template: spec:` section, update the image pointer to your image url 
    ```
    # YAML snippet. In the `spec: template: spec:`, add the following:
    containers:
      - name: some_name
        image: image-registry.openshift-image-registry.svc:5000/<namespace>/<config_name>:latest
    ```

### <a id="grafana-prometheus">B. Grafana-Prometheus Setup</a>

#### B.1. Prometheus / Thanos Querier URL

**NOTE:** This section may be different, depending on your setup. 

1. Apply the `enable_monitoring.yaml` file.
   ```
   oc apply -f enable_monitoring.yaml
   ```
2. Get the Thanos Querier route URL:
   ```
   oc get route thanos-querier -n openshift-monitoring
   ```
3. Copy/save this URL. You will need it later.

#### B.2. Grafana Dashboard Setup

1. In the cluster web console, install the Grafana Operator from the operator hub.
2. From the Grafana Operator
   - Create a Grafana instance in `openshift-operators` namespace. Make note of the login credentials and label(s).
   - This will create a `ServiceAccount` in the same namespace, with the default name `<grafana_instance_name>-sa`.
3. Modify the `ServiceAccount`.
   -  Add the policy to the new ServiceAccount.
       ```
       oc policy add-role-to-user cluster-monitoring-view -z <service_account> -n openshift-operators
       ```
   - Generate an access token for the ServiceAccount.
       ```
       # Expires in 10 years
       oc create token <service-account-name> -n openshift-operators --duration=87600h
       ```
   - Copy/save this token. You will need it later.
4. From the Grafana Operator
   - Create a Grafana Datasource instance (easier setup with YAML view).
     - Add/update the following parts, and paste the `thanos-querier` url and the access token from earlier.
       ```
       metadata:
        labels:
          grafana_datasource: "true"
       spec:
         datasource:
           editable: true
           url: 'https://<thanos_querier_url>
           jsonData:
              httpHeaderName1: Authorization
              timeInterval: 5s
              tlsSkipVerify: true
           secureJsonData:
             httpHeaderValue1: Bearer <access_token>
         instanceSelector:
            matchLabels:
              dashboards: <grafana_instance_label>
       ```
5. Create a route for Grafana
    ```
    oc create route edge grafana-route --service=<grafana_instance_name>-service --port=3000 --insecure-policy=Redirect -n openshift-operators
    ```

### C. Miscellaneous Commands
```
# Checks the requests and limits of resources. Look for "nvidia.com/gpu" in the output for GPU resources.
oc describe node <worker-node-with-gpu> | grep -A10 Allocated

# Shows the pods that have requested GPUs
oc get pods -A -o custom-columns="NAMESPACE:.metadata.namespace,NAME:.metadata.name,GPUs:.spec.containers[*].resources.limits.nvidia\.com/gpu" | grep -v "<none>"
```

-----
## <a id="references">References</a>

vLLM
- [Repository](https://github.com/vllm-project/vllm)
- [Documentation](https://docs.vllm.ai/en/latest/)
