workflow "CI" {
  on = "push"
  resolves = ["Master", "Build Image", "Run Tests", "Docker Tag"]
}

action "Master" {
  needs = "Test"
  uses = "actions/bin/filter@master"
  args = "branch master *\.*\.*"
}

action "Build Image" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "build -t base ."
  needs = ["Master"]
}

action "Run Tests" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "run --rm -w=/yeyo --entrypoint=pytest -t base"
  needs = ["Build Image"]
}

action "Docker Tag" {
  uses = "actions/docker/tag@aea64bb1b97c42fa69b90523667fef56b90d7cff"
  needs = ["Run Tests"]
  args = ["base", "thauck/yeyo"]
}
