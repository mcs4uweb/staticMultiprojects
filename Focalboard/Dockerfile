# Install Docker & Compose (Ubuntu)
sudo apt update && sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Deploy
mkdir focalboard && cd focalboard
curl -O https://raw.githubusercontent/your-config/docker-compose.yml  # or paste the above
docker-compose up -d