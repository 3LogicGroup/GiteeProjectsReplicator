# Gitee Projects Replicator

**Gitee Projects Replicator**, **GPReplicator** or **GPR** is the simple Python API containing transport and methods to be used for replication & synchronization projects from Gitee.ru or Gitee.com services. Also, a mirrored project contains most important project artifacts: description, issues, milestones, releases and documentation.

Replication and synchronization worked through API.v5 of Gitee service.

Also, GPReplicator can be used as a CLI manager to work with Gitee projects in the console (it has a rich keys and commands), which is convenient for integration when used in CI/CD processes, or you can use it as a Python module with `python import gpreplicator`.

If you work with GPReplicator as a class, each method returns an object (usually of type list or dict) containing all the data available through the Gitee API. You can read more about the methods of the GPReplicator class here:
- ⚙ [Documentation on GPReplicator class methods (for Python developers)](https://3logicgroup.github.io/GiteeProjectsReplicator/docs/gpreplicator/GPReplicator.html)

## Quick start and examples

Here are simple CLI examples available after GPReplicator was installed. For all examples, you will need to use the [Gitee OAuth token](https://gitee.com/api/v5/oauth_doc). Without an authorization token, most commands will be available, but no more than 60 requests from one IP address.

- Get and show project tree files recursively (also replace API gateway for Chinese service):
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "your_token" -go "project_group_owner" -gp "repository_name" --gitee-recursive --files`
  
  Example:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go tim55667757 -gp PriceGenerator --files`
  
- Get and show project releases:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go "owner" -gp "repository" --releases`
  
- Get and show project issues:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go "owner" -gp "repository" --issues`

To enable all debug information, such as net request and response headers in all methods use `--more` or `--more-debug` keys.

Help about available console keys and commands: `python3 GPReplicator.py --help`