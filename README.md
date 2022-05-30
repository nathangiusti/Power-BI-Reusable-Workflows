# Power BI Reusable Workflows

This repository contains reusable workflows in order to set up DevOps for Power BI

For a quickstart/example of the use of these workflows check out [Power-BI-Sample-VC-Repo](https://github.com/nathangiusti/Power-BI-Sample-VC-Repo). 

# Available Workflows:

## [Deserialize PBIX](.github/workflows/deserialize-pbix.yml)

Unzips PBIX files into their report JSON's for version control and peer review. 

Example workflow:

```yaml
name: Reformat Power BI Assets
on: [pull_request]
jobs:
  Deserialize-PBIX-Files:
    uses: nathan-giusti/Power-BI-Reusable-Workflows/.github/workflows/deserialize-pbix.yml@main
    with:
      commit_message: "Deserialize PBIX files"
```

|Input|type| required |default|description|
|:---------------------------------:|:----------------------:|:--------:|:---------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| commit_message | `string` | `false` | `"Deserialize PBIX Files"` | Commit message to be used when writing JSON files to repository. |
| separator | `string` | `false` | `","` | Character used to separate file names. Ensure that a character is selected that is never used in file/folder names. |

## [Workspace PBIX Deploy](.github/workflows/workspace-deploy.yml)

Deploys a PBIX file to a workspace.

Place PBIX files in one folder per workspace. Use the config file to map the folder names to workspace ids. 

Example workflow:

```yaml
name: Deploy to workspace
on: [pull_request]
jobs:
  Deserialize-PBIX-Files:
    uses: nathan-giusti/Power-BI-Reusable-Workflows/.github/workflows/workspace-deploy.yml@main
    with:
      tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      config_file: .github/config/deploy_config.yaml
    secrets:
      client_id: ${{ secrets.CLIENT_ID }}
      client_secret: ${{ secrets.CLIENT_SECRET }} 
```

Example config:

```yaml
Workspace_1:
  workspace_id: 'f2424abd-e0d6-4305-bcae-2caa80db8639'
Workspace_2:
  workspace_id: '1a19ec23-2ba0-450b-9935-def6ea465d1d'
Workspace_3:
  workspace_id: 'b5151f96-3b01-4b17-bc95-cce8630832ac'
```


|Input|type| required |default|description|
|:---------------------------------:|:----------------------:|:--------:|:---------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| client_id | `string` | `true` | | Client id for Azure service princple. |
| client_secret | `string` | `true` | | Client secret for Azure service princple. |
| tenant_id | `string` | `true` | | Tenant id of your instance. |
| config_file | `string` | `true` | | Location of config file. |
| separator | `string` | `false` | `","` | Character used to separate file names. Ensure that a character is selected that is never used in file/folder names. |

## [Pipeline PBIX Deploy](.github/workflows/pipeline-deploy.yml)

Deploys a PBIX file via a pipeline.

Place PBIX files in one folder per pipeline. Use the config file to map the folder names to pipeline ids. 

Example workflow:

```yaml
name: Deploy via pipeline
on:
  push:
    branches:
      - main
jobs:
  pipeline-deploy:
    uses: nathan-giusti/Power-BI-Reusable-Workflows/.github/workflows/pipeline-deploy.yml@main
    with:
      tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      config_file: .github/config/deploy_config.yaml
      source_stage_order: 1
    secrets:
      client_id: ${{ secrets.CLIENT_ID }}
      client_secret: ${{ secrets.CLIENT_SECRET }} 

```

Example config:

```yaml
Workspace_1:
  pipeline_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
Workspace_2:
  pipeline_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
Workspace_3:
  pipeline_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
```


|Input|type| required |default|description|
|:---------------------------------:|:----------------------:|:--------:|:---------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| client_id | `string` | `true` | | Client id for Azure service princple. |
| client_secret | `string` | `true` | | Client secret for Azure service princple. |
| tenant_id | `string` | `true` | | Tenant id of your instance. |
| config_file | `string` | `true` | | Location of config file. |
| source_stage_order | `number` | `true` | | 0 to deploy dev to test, 1 to deploy test to prod |
| update_app_in_target_workspace | `boolean` | `false` | `false` | True to update the app on deploy |
| allow_purge_data | `boolean` | `false` | `false` | Should not be needed because this is for reports but fail safe |
| separator | `string` | `false` | `","` | Character used to separate file names. Ensure that a character is selected that is never used in file/folder names. |

### Note for Pipeline and Workspace Deploy

Config files can be combined with an entry for workspace_id and pipeline_id for each folder.

Example config:

```yaml
Hero_Analytics:
  pipeline_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
  workspace_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
Supply_Chain_Analytics:
  pipeline_id:  'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
  workspace_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
BI360:
  pipeline_id:  'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
  workspace_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
```


## [Tabular Editor Datamodel Deploy](.github/workflows/te-deploy.yml)

Deploys a dataset saved in Tabular Editor folder format to a workspace.

If all datasets are to be deployed to the same URL, you can provide that workspace URL and leave out config file.
If datasets need to be deployed to multiple workspaces, you can provide a config file mapping the folders to the workspace URLs.
You must provide either `config_file` or `db_url`.

If a config file is set, the folder structure for datasets is assumed to be

./<workspace_name>/<dataset_name>

If no config file is sett, the folder structure for datasets is assumed to be

.<dataset_name>

Datasets cannot be in the same folder as any other json files, including deserialized pbix files. To place datasets in a separate folder for reports we suggest

./reports/<workspace_name>/<report_pbix>
./datasets/<workspace_name>/<report_pbix>

To accomplish this you can set the file option to datasets or to whatever path leads to your dataset folder. 

Example workflow:

```yaml
name: Deploy to dataset
on: [pull_request]
jobs:
  deploy_to_test:
    uses: nathan-giusti/Power-BI-Reusable-Workflows/.github/workflows/te-deploy.yml@main
    with:
      tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      config_file: .github/config/test.yaml
      deploy_roles: true
      deploy_partitions: true
    secrets:
      client_id: ${{ secrets.CLIENT_ID }}
      client_secret: ${{ secrets.CLIENT_SECRET }}
```

Example config: 

```yaml
"Workspace1": "powerbi://api.powerbi.com/v1.0/myorg/Workspace1"
"Workspace2": "powerbi://api.powerbi.com/v1.0/myorg/Workspace2"
```

|Input|type| required |default|description|
|:---------------------------------:|:----------------------:|:--------:|:---------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| client_id | `string` | `true` | | Client id for Azure service princple. |
| client_secret | `string` | `true` | | Client secret for Azure service princple. |
| tenant_id | `string` | `true` | | Tenant id of your instance. |
| db_url | `string` | `false` | | Workspace to deploy to |
| te_url | `string` | `false` | | URL to download TE from. Pulls from most recent by default |
| folder | `boolean` | `false` | | The folder containing the datasets |
| deploy_roles | `boolean` | `false` | `false` | True to deploy roles |
| deploy_partitions | `boolean` | `false` | `false` | True to deploy partitions |
| separator | `string` | `false` | `","` | Character used to separate file names. Ensure that a character is selected that is never used in file/folder names. |
| since_last_remote_commit | `boolean` | `false` | `true` |  Use the last commit on the remote branch as the base_sha |

### Known Issues

All changes files are passed to the command line. If there are too many changed files, the program will crash. This can be fixed by setting since_last_remote_commit to true, but can cause issues if multiple datasets are being modified in the same pull request. 
