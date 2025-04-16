FROM vllm/vllm-openai:latest

ARG model_id

ENV VLLM_DO_NOT_TRACK=1 VLLM_NO_USAGE_STATS=1

ENV HF_HOME=/vllm-workspace

WORKDIR ${HF_HOME}

RUN huggingface-cli download ${model_id}

ENV HF_HUB_OFFLINE=1

CMD ["--model=${model_id}", "--download-dir=${HF_HOME}"]
