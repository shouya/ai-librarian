FROM docker.io/library/node:14 as frontend-builder
WORKDIR /app/web

COPY ./web .
RUN npm run build

FROM docker.io/library/python:3.9
WORKDIR /app

# Install the Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the project files to the working directory
COPY . .

# Copy the generated frontend files from the previous stage
COPY --from=frontend-builder /app/web/dist /app/web/dist

# Set environment variables
ENV HOST 0.0.0.0
ENV PORT 8000
ENV DATA_DIR /data

# Expose the specified port
#
# Note: This is only valid for default port. If you change the port via runtime environment variable, you may want to expose/publish it manually.
EXPOSE 8000

# Run the command to start the web application
# CMD ["ai-librarian", "web"]
CMD ["sh" "-c" "gunicorn --bind {HOST}:${PORT} ai_librarian:web"]
