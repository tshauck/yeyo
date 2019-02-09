workflow "New workflow" {
  on = "push"
  resolves = [
    "Build Image",
    "Run Tests",
    "Filters for GitHub Actions",
    "Docker Tag",
  ]
}


action "Filters for GitHub Actions" {
  uses = "actions/bin/filter@9d4ef995a71b0771f438dd7438851858f4a55d0c"
  args = "branch *.*.*"
}

action "Build Image" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "build -t thauck/yeyo-tester ."
  needs = ["Filters for GitHub Actions"]
}

action "Run Tests" {
  uses = "actions/docker/cli@c08a5fc9e0286844156fefff2c141072048141f6"
  args = "run --rm -w=/yeyo --entrypoint=pytest -t thauck/yeyo-tester"
  needs = ["Build Image"]
}

action "Docker Tag" {
  uses = "actions/docker/tag@aea64bb1b97c42fa69b90523667fef56b90d7cff"
  needs = ["Run Tests"]
  args = ["base", "thauck/yeyo"]
}
