variable "REGISTRY" {
    default = "ghcr.io"
}

variable "GITHUB_SHA" {
    default = "latest"
}

group "default" {
    targets = ["frontend", "backend", "mcp-server"]
}

target "frontend" {
    context = "./apps/frontend"
    dockerfile = "../../docker/frontend/Dockerfile"
    tags = ["${REGISTRY}/mypetparlor/frontend:${GITHUB_SHA}"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "backend" {
    context = "./apps/backend"
    dockerfile = "../../docker/backend/Dockerfile"
    tags = ["${REGISTRY}/mypetparlor/backend:${GITHUB_SHA}"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "mcp-server" {
    context = "./common/mcp"
    dockerfile = "../../docker/mcp-server/Dockerfile"
    tags = ["${REGISTRY}/mypetparlor/mcp-server:${GITHUB_SHA}"]
    platforms = ["linux/amd64", "linux/arm64"]
}