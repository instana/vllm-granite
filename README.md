# vllm-granite
Artifacts to build and deploy a container with vLLM and granite, exposed via REST APIs

##  vLLM container with IBM Granite

The following command builds a vLLM container image which pulls Granite models from HuggingFace. It uses the official vLLM image as base.

```
docker buildx build --tag vllm_with_model -f Dockerfile.model --build-arg model_id=ibm-granite/granite-3.1-8b-instruct .
```
