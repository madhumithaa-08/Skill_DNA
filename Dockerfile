# SKILL DNA — Amazon Bedrock AgentCore Runtime Container
# AgentCore requires: /invocations POST + /ping GET on port 8080
# Build: docker build -t skill-dna .
# Test: docker run -p 8080:8080 --env-file .env skill-dna

FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full application
COPY agents/ ./agents/
COPY models/ ./models/
COPY tools/ ./tools/
COPY utils/ ./utils/
COPY data/ ./data/
COPY agentcore_handler.py .

# AgentCore Runtime uses port 8080
EXPOSE 8080

# Health check for AgentCore
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s CMD curl -f http://localhost:8080/ping || exit 1

CMD ["python", "-m", "uvicorn", "agentcore_handler:app", "--host", "0.0.0.0", "--port", "8080"]
