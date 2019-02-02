workflow "New workflow" {
  on = "push"
  resolves = ["Build Image", "Run Tests"]
}

action "Build Image" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "build -t thauck/yeyo-tester ."
}

action "Run Tests" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "run --rm -w=/yeyo --entrypoint=pytest -t thauck/yeyo-tester"
  needs = ["Build Image"]
}
