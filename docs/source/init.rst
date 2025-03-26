=======================
Inicialização Terraform
=======================

Requirements
------------

No requirements.

Providers
---------

======================= =======
Name                    Version
======================= =======
                        n/a
`aws <#provider_aws>`__ 
======================= =======

Modules
-------

No modules.

Resources
---------

+----------------------------------------------------------+----------+
| Name                                                     | Type     |
+==========================================================+==========+
| `aws_dynamodb_tabl                                       | resource |
| e.terraform_lock <https://registry.terraform.io/provider |          |
| s/hashicorp/aws/latest/docs/resources/dynamodb_table>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_openid_connect_provider.git                     | resource |
| hub <https://registry.terraform.io/providers/hashicorp/a |          |
| ws/latest/docs/resources/iam_openid_connect_provider>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_policy.g                                        | resource |
| ithub_actions_policy <https://registry.terraform.io/prov |          |
| iders/hashicorp/aws/latest/docs/resources/iam_policy>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_policy.github_act                               | resource |
| ions_policy_dynamodb <https://registry.terraform.io/prov |          |
| iders/hashicorp/aws/latest/docs/resources/iam_policy>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_ro                                              | resource |
| le.github_actions_role <https://registry.terraform.io/pr |          |
| oviders/hashicorp/aws/latest/docs/resources/iam_role>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_role_policy_attachment.attach_po                | resource |
| licy <https://registry.terraform.io/providers/hashicorp/ |          |
| aws/latest/docs/resources/iam_role_policy_attachment>`__ |          |
+----------------------------------------------------------+----------+
| `aws_iam_role_policy_attachment.attach_policy_dy         | resource |
| namo <https://registry.terraform.io/providers/hashicorp/ |          |
| aws/latest/docs/resources/iam_role_policy_attachment>`__ |          |
+----------------------------------------------------------+----------+
| `aws                                                     | resource |
| _s3_bucket.s3_buckets <https://registry.terraform.io/pro |          |
| viders/hashicorp/aws/latest/docs/resources/s3_bucket>`__ |          |
+----------------------------------------------------------+----------+

Inputs
------

+-----------------+-----------------+------------+---------+----------+
| Name            | Description     | Type       | Default | Required |
+=================+=================+============+=========+==========+
|                 | Nome do         | ``string`` | n/a     | yes      |
| `TagEnv <#i     | ambiente        |            |         |          |
| nput_TagEnv>`__ |                 |            |         |          |
+-----------------+-----------------+------------+---------+----------+
|                 | Nome do projeto | ``string`` | n/a     | yes      |
| `Tag            |                 |            |         |          |
| Project <#input |                 |            |         |          |
| _TagProject>`__ |                 |            |         |          |
+-----------------+-----------------+------------+---------+----------+
|                 | Regiao AWS      | ``string`` | n/a     | yes      |
| `aws            |                 |            |         |          |
| _region <#input |                 |            |         |          |
| _aws_region>`__ |                 |            |         |          |
+-----------------+-----------------+------------+---------+----------+
|                 | Use             | ``string`` | n/a     | yes      |
| `git            | r/Organizations |            |         |          |
| hub_acc <#input | GitHub          |            |         |          |
| _github_acc>`__ |                 |            |         |          |
+-----------------+-----------------+------------+---------+----------+

Outputs
-------

No outputs.
