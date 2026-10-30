# VBM comparison codes

Code accompanying the publication:

> Antonopoulos, G., More, S., Raimondo, F., Eickhoff, S. B., Hoffstaedter, F., & Patil, K. R. (2023).
> A systematic comparison of VBM pipelines and their application to age prediction.
> *NeuroImage*. https://doi.org/10.1016/j.neuroimage.2023.120292

This repository contains the preprocessing pipelines, feature extraction,
analysis and brain-age prediction code used to compare voxel-based
morphometry (VBM) pipelines on structural T1-weighted MRI.

## Overview

The same participants were preprocessed with 10 VBM pipeline variants,
built from different tools for segmentation and normalization, each using
either the default (standard) template or a study-specific template:

| Pipeline              | Default template      | Study-specific template |
|-----------------------|-----------------------|-------------------------|
| CAT12.8               | `cat12.8`             | `cat12.8_data`          |
| FSLVBM                | `fslvbm13`            | `fslvbm`                |
| fMRIPrep + FSLVBM     | `fmriprep1_3`         | `fmriprep1_23`          |
| ANTs + FSLVBM         | `ants_fslvbm3`        | `ants_fslvbm23`         |
| ANTs (Nipype)         | `ants_icbm` (ICBM)    | `ants_data`             |

Datasets: CamCAN, eNKI and IXI.

Gray matter volume was summarized into regional features using the
Schaefer 1000-parcel (17 networks), Tian subcortical (S1) and FSL cerebellum
atlases, as well as a 1073-parcel (BSF) atlas.

## Repository structure

- `pipelines/`: VBM preprocessing pipelines and quality control
  - `ants_pipeline/`: ANTs pipeline in Nipype (N4 bias correction, brain
    extraction, Atropos segmentation, affine + B-spline SyN registration to
    MNI, Jacobian modulation)
  - `ants_fslvbm/`: ANTs segmentation followed by FSLVBM template creation,
    normalization and modulation
  - `fmriprep_FSL/`: fMRIPrep anatomical preprocessing followed by FSLVBM
  - `fslvbm_sub/`: FSLVBM
  - `qc_mask.py`, `qc_wrapper.sh`: quality control
- `features/`: extraction of regional gray matter features per dataset
- `analysis/`: comparison of pipelines
  - `01_pipeline_classif.py`: classification of which pipeline produced the data
  - `02_idiff_pplns.py`: participant identifiability across pipelines
  - `03_ppln_corr_niftis.py`: voxel-wise correlation between pipelines
  - `anova_age_r_all_data.py`: region-age correlations across pipelines
  - plotting scripts for the figures
- `age_pred/`: brain-age prediction within and across datasets
  (e.g. RVR, Gaussian process regression, kernel ridge, LASSO, elastic net)
  using `julearn`

## Usage

File paths are hard-coded for our compute environment. Edit them to match
your set-up before running.

All preprocessing except CAT12.8 was run on an HTCondor cluster, and the
`.submit` and wrapper scripts are written for HTCondor.

## Requirements

- CAT12.8 (SPM12), FSL, fMRIPrep, ANTs
- Python: `nipype`, `nibabel`, `nilearn`, `numpy`, `pandas`, `scikit-learn`,
  `julearn`, `sklearn-rvm`, `glmnet`, `matplotlib`, `seaborn`

## Citation

If you use this code, please cite:

```bibtex
@article{antonopoulos2023vbm,
  title   = {A systematic comparison of VBM pipelines and their application to age prediction},
  author  = {Antonopoulos, Georgios and More, Shammi and Raimondo, Federico and
             Eickhoff, Simon B. and Hoffstaedter, Felix and Patil, Kaustubh R.},
  journal = {NeuroImage},
  year    = {2023},
  doi     = {10.1016/j.neuroimage.2023.120292}
}
```
