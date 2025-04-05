FROM python:3.12-slim

WORKDIR /app

# Copy requirements, readme and source code
COPY pyproject.toml README.md ./
COPY src/ /app/src/

# Install dependencies
RUN pip install --no-cache-dir pip-tools uv && \
    pip install -e .

# Run the application
CMD ["python", "-m", "amazon_copilot.data_loader"]
