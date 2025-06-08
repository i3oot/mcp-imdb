# Use slim image for smaller size
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Disable writing .pyc files and enable stdout flushing
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies first for better cache utilization
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastmcp fastapi Cinemagoer

# Copy application code
COPY src ./src
COPY script ./script

# Install the package
RUN pip install --no-cache-dir .

# Expose default HTTP port
EXPOSE 8000

# Run the server using HTTP transport for quick startup
ENV MCP_TRANSPORT=HTTP \
    PORT=8000

CMD ["mcp-imdb"]
