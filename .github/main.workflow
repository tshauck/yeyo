workflow "New workflow" {
  on = "push"
  resolves = ["Build Image", "Run Tests", "Docker Tag"]
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

action "Docker Tag" {
  uses = "actions/docker/tag@aea64bb1b97c42fa69b90523667fef56b90d7cff"
  needs = ["Run Tests"]
}
