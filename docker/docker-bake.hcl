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