# ShowMeYourGit

**showmeyourgit** (or smyg) is a project for calculating git metrics: added lines, deleted lines, commits count, changed files, code changes ratio, code churn ratio.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install smyg.

```bash
pip install --user smyg
```

## Usage

Clone [example project](https://github.com/nmix/example-project)
```bash
git clone https://github.com/nmix/example-project.git
cd example-project
```

### commit

 Show commit info

```bash
# --- show command help
$ smyg commit --help

# --- show last commit info for current branch
$ smyg commit
cdcb7c6ac0b92b1e16cfdd6f1e6abf0ed8f73e48 | update README
2023-02-20 16:42:41+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:       26
Deleted lines:      0
Changed files:      1

# --- show last commit info in json format
$ smyg commit --output json | jq
{
  "hash": "cdcb7c6ac0b92b1e16cfdd6f1e6abf0ed8f73e48",
  "msg": "update README",
  "author_name": "Nikolay Mikhaylichenko",
  "author_email": "nn.mikh@yandex.ru",
  "author_date": "2023-02-20 16:42:41+03:00",
  "committer_name": "Nikolay Mikhaylichenko",
  "committer_email": "nn.mikh@yandex.ru",
  "committer_date": "2023-02-20 16:42:41+03:00",
  "project_name": "example-project",
  "added": 26,
  "deleted": 0,
  "changed_files": 1,
  "branches": [
    "main"
  ]
}

# --- show info about arbitary commit
$ smyg commit 07cb19ceba138f1d7e4a1d48f024e520f3657a1d
07cb19ceba138f1d7e4a1d48f024e520f3657a1d | commit 2-1
2023-02-20 16:26:48+03:00 | Nikolay Mikhaylichenko
['branch-2']
Added lines:        6
Deleted lines:      0
Changed files:      1
```

### branch-commits

Show changes for bundle of commits in branch.

If we know last commit of previous bundle then we take all commits after that. In Gitlab CI previous commit SHA may be in `CI_COMMIT_BEFORE_SHA` environment variable (see [Predefined variables reference](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)).

If we dont have previous commit then we take only commits for *single* branch. *Signle* branch means that commit belongs only one branch. **Here it is mandatory to have a complete local copy of the repository with all branches.**

```bash
# --- show command help
$ smyg branch-commits --help

# --- if you just clone the example repository, the entire commit list will be displayed (from Initial commit)
#     this is because only one branch is locally received and all commits belongs to it
$ smyg branch-commits

cdcb7c6ac0b92b1e16cfdd6f1e6abf0ed8f73e48 | update README
2023-02-20 16:42:41+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:       26
Deleted lines:      0
Changed files:      1

7febdeea7b4f82d15f7fa0765c12f10928af7a1a | lorem ipsum in main
2023-02-20 16:33:58+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:        6
Deleted lines:      0
Changed files:      1

# ... skip remaining commits

# --- checkout branch-3 and repeat the command
#     we get only 3 commits for the branch
$ git checkout branch-3
Switched to a new branch 'branch-3'
$ smyg branch-commits

414d13a92998f9de86dd60d41f05f092e64350f3 | commit 3-3
2023-02-20 16:32:42+03:00 | Nikolay Mikhaylichenko
['branch-3']
Added lines:        2
Deleted lines:      0
Changed files:      1

776206b033b8a149c4ee491ec9bee23273f98afc | commit 3-2
2023-02-20 16:32:13+03:00 | Nikolay Mikhaylichenko
['branch-3']
Added lines:        2
Deleted lines:      0
Changed files:      1

aa4f97ed8366b8d72a0be2c1c114aa503b531190 | commit 3-1
2023-02-20 16:31:54+03:00 | Nikolay Mikhaylichenko
['branch-3']
Added lines:        4
Deleted lines:      0
Changed files:      1

# --- branch commits with previous SHA
$ git checkout main
smyg branch-commits 5317cd6080033ae5a9ce3166095745e862a52c9d

cdcb7c6ac0b92b1e16cfdd6f1e6abf0ed8f73e48 | update README
2023-02-20 16:42:41+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:       26
Deleted lines:      0
Changed files:      1

7febdeea7b4f82d15f7fa0765c12f10928af7a1a | lorem ipsum in main
2023-02-20 16:33:58+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:        6
Deleted lines:      0
Changed files:      1

bbead3ba03de57909ee622fac4b973de180f5e5f | Branch 2 (#2)

commit 2-1  | commit 2-2 | commit 2-3
2023-02-20 16:29:39+03:00 | Nikolay Mikhaylichenko
['branch-3', 'main']
Added lines:        8
Deleted lines:      0
Changed files:      1
```

### codechanges

Show total added and deleted lines count for current ref.

```bash
# --- show command help
$ smyg codechanges --help

# --- changes for current ref
$ smyg codechanges
Ratio (%):         11
Added lines:      107
Deleted lines:     12

# --- code changes between commits
$ smyg codechanges --from-commit 3a085582e8df7c1d622c412eb54eb5ee96e82c48  \
  --to-commit bbead3ba03de57909ee622fac4b973de180f5e5f
Ratio (%):         42
Added lines:       26
Deleted lines:     11
```

### codechurn

Show count of added lines and count of deleted lines from those that were added. Displays the level of work that was not released.

> Ideally, it should coincide with the codechanges for whole project history. For complex branching it may slightly different.

```bash
# --- show command help
$ smyg codechurn --help

# --- churn for current ref (equal with codechanges, it is expected)
smyg codechurn
Ratio (%):         11
Added lines:      107
Deleted lines:     12

# --- churn from specified commit (not equal with codechanges, it is expected)
$ smyg codechurn --from-commit 44c6334f38fe796f38c39e1d11a8d19925684926 \
    --to-commit fccfa86625353409018ccd467f0050b57152656e
Ratio (%):         23
Added lines:       26
Deleted lines:      6
```

## Prometheus Metrics

You can push metrics to Prometheus PushGateway. 
Recommended to use Aggregation Gateway like https://github.com/zapier/prom-aggregation-gateway.

`commit` and `branch_commits` is a *Counter* type, `codechanges` and `codechurn` - *Gauge*. 

You must specify environment variables `PUSHGATEWAY_URL` and `PROJECT_NAME` and command option `--push-metrics` to send metrics. For basic auth access specify `PUSHGATEWAY_USERNAME` and `PUSHGATEWAY_PASSWORD`.

```bash
$ git checkout main

$ docker run --rm -p 8080:80 ghcr.io/zapier/prom-aggregation-gateway:v0.7.0

$ PUSHGATEWAY_URL=localhost:8080 PROJECT_NAME=example_project \
    smyg commit --push-metrics
cdcb7c6ac0b92b1e16cfdd6f1e6abf0ed8f73e48 | update README
2023-02-20 16:42:41+03:00 | Nikolay Mikhaylichenko
['main']
Added lines:       26
Deleted lines:      0
Changed files:      1

$ curl localhost:8080/metrics
# HELP commit_added_lines_total Number of added lines in commit
# TYPE commit_added_lines_total counter
commit_added_lines_total{author_email="nn.mikh@yandex.ru",author_name="Nikolay Mikhaylichenko",job="showmeyourgit",project_name="example_project"} 26
# HELP commit_changed_files_total Number of changed files in commit
# TYPE commit_changed_files_total counter
commit_changed_files_total{author_email="nn.mikh@yandex.ru",author_name="Nikolay Mikhaylichenko",job="showmeyourgit",project_name="example_project"} 1
# HELP commit_deleted_lines_total Number of added deleted in commit
# TYPE commit_deleted_lines_total counter
commit_deleted_lines_total{author_email="nn.mikh@yandex.ru",author_name="Nikolay Mikhaylichenko",job="showmeyourgit",project_name="example_project"} 0
# HELP commits_total Number of commits
# TYPE commits_total counter
commits_total{author_email="nn.mikh@yandex.ru",author_name="Nikolay Mikhaylichenko",job="showmeyourgit",project_name="example_project"} 1
```

## Develop & Test

```bash
$ git clone git@github.com:nmix/showmeyourgit.git
$ cd showmeyourgit
$ poetry install
$ poetry shell
$ pytest
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
