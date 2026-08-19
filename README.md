# SWDB 2026 - Connectomics Workshop


Produced for: https://github.com/AllenInstitute/swdb_2026_student/wiki

The function of the nervous system arises out of a combination of the properties of individual neurons and of how they are connected into a larger network. The central goal of connectomics is to produce complete maps of the connectivity of the nervous system with synaptic resolution and analyze them to better understand the organization, development, and function of the nervous system.

**Electron Microscopy (EM) data enables morphological reconstruction of neurons and resolution of their synaptic connectivity.** The V1DD dataset is one of the largest volume EM datasets currently available, and spans all layers of mouse visual cortex. We will be using this dataset to query the connectivity between neurons in the visual cortex.

Module 1 - `code\workshops\Module_1.ipynb` will:  

* introduce the basics of how synaptic connectivity is measured in EM connectomics  
* examine reconstructions of individual neurons and their connectivity  
* discuss how morphological features and connectivity suggest cell types  
* explore how connectivity changes as function of target and distance  

Module 2 - `code\workshops\Module_2.ipynb` will:  

* introduce concepts of network connectivity  
* investigate the role of cell type in the structure of networks  
* consider connection probability as a function of distance  
* incorporate ophys recordings and map the correlation of structure to function  

CodeOcean Capsule: https://codeocean.allenneuraldynamics.org/capsule/0103497/tree

Github Repository: https://github.com/AllenSWDB/SWDB_2026_Connectomics



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