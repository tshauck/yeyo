workflow "New workflow" {
  on = "push"
  resolves = ["Build Image", "Run Image"]
}

action "Build Image" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "build -t thauck/yeyo ."
}

action "Run Image" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "run --rm -w=/yeyo --entrypoint=pytest -t thauck/yeyo"
  needs = ["Build Image"]
}
