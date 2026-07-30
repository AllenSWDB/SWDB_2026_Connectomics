# SWDB_2026_Connectomics

Tutorials on using Allen Institute connectomics data.

## Local development instructions

For locally copying the data asset:

```
uvx --from awscli aws s3 cp --recursive --no-sign-request \
  "s3://aind-open-data/v1dd-analysis-1196-1_2025-08-14_16-38-00/" \
  "data/v1dd_1196"
```

For setting the data dir for local runs: 

```
export SWDB_DATA_ROOT="{correct path for your machine}/SWDB_2026_Connectomics/data"
```

Or put into a .env file
```
SWDB_DATA_ROOT={correct path for your machine}/SWDB_2026_Connectomics/data
```

You may need to add a `.vscode/settings.json` with the following to have that picked up 
automatically
```
{
    "python.terminal.useEnvFile": true
}
```