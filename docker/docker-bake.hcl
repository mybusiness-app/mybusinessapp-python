variable "REGISTRY" {
    default = "ghcr.io"
}

variable "GITHUB_SHA" {
    default = "latest"
}

group "default" {
    targets = ["chainlit", "mcp-server"]
}

target "chainlit" {
    context = "./apps/chainlit"
    dockerfile = "../../docker/chainlit/Dockerfile"
    tags = ["${REGISTRY}/mypetparlor/chainlit:${GITHUB_SHA}"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "mcp-server" {
    context = "./common/mcp"
    dockerfile = "../../docker/mcp-server/Dockerfile"
    tags = ["${REGISTRY}/mypetparlor/mcp-server:${GITHUB_SHA}"]
    platforms = ["linux/amd64", "linux/arm64"]
}