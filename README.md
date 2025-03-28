# vllm-granite
Artifacts to build and deploy a container with vLLM and granite, exposed via REST APIs

##  vLLM container with IBM Granite

The following command builds a vLLM container image which pulls Granite models from HuggingFace. It uses the official vLLM image as base.

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
