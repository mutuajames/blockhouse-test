# Trading API

A simple trading order management API built with FastAPI, PostgreSQL, Docker, and deployed on AWS EC2 with CI/CD via GitHub Actions.

## Features

- REST API for creating and retrieving trading orders
- WebSocket support for real-time order status updates
- PostgreSQL database for data persistence
- Docker containerization
- CI/CD pipeline using GitHub Actions
- Deployed on AWS EC2

## API Endpoints

### REST API

- `POST /orders` - Create a new order
- `GET /orders` - Get all orders
- `GET /orders/{order_id}` - Get a specific order by ID
- `PATCH /orders/{order_id}` - Update order status

### WebSocket API

- `ws://host:port/ws/orders` - Connect to receive real-time order updates(No trailing slash)

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (or use the dockerized version)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/trading-api.git
   cd trading-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API at http://localhost:8000 and the Swagger UI at http://localhost:8000/docs

### Running with Docker Compose

```bash
docker-compose up -d
```

This will start both the API and PostgreSQL database.

## Deployment to AWS EC2

### Manual Deployment

1. Launch an EC2 instance with Ubuntu
2. Install Docker and Docker Compose:
   ```bash
   sudo apt update
   sudo apt install -y docker.io
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   sudo usermod -aG docker $USER
   ```
   Log out and log back in for the group changes to take effect.

3. Clone the repository and start the application:
   ```bash
   git clone https://github.com/yourusername/trading-api.git
   cd trading-api
   docker-compose up -d
   ```

### CI/CD with GitHub Actions

The repository includes a GitHub Actions workflow that:
1. Runs tests on all PRs
2. Builds and deploys the application to EC2 on merges to main

To use this workflow, you need to set up the following GitHub secrets:
- `EC2_HOST`: Your EC2 instance public IP or DNS
- `EC2_USERNAME`: SSH username (usually `ubuntu` for Ubuntu instances)
- `EC2_SSH_KEY`: Private SSH key to connect to your EC2 instance

## Testing

Run tests with pytest:

```bash
pytest
```

## WebSocket Usage

Connect to the WebSocket endpoint and send a JSON message to subscribe to specific symbols:

```json
{
  "action": "subscribe",
  "symbols": ["AAPL", "MSFT", "GOOGLE"]
}
```

To unsubscribe:

```json
{
  "action": "unsubscribe",
  "symbols": ["AAPL"]
}
```

You'll receive real-time updates when orders are created or their status changes.