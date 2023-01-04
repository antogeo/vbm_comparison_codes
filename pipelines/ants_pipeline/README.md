# ANTs_pipeline
Preprocessing pipeline based on ANTs registration toolbox, implemented in Nipype.
Can be run on server (juseless) or laptop (e.g. SSD).

## Pipeline steps
1. Bias field N4BiasFieldCorrection
2. Brain extraction (reslice Mask to make sure it s similar to brain nifti)
3. GM -> Atropos segmentation
4. Registration to MNI (affine + BsplineSyN)
5. Calculate Jacobian
6. Multiply Jacobian with MNI_GM

More extensive information about the steps can be found in the [nipype docs](https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.ants.html)
   and in the [ANTsDoc](http://stnava.github.io/ANTsDoc/).

## Files
* `ants_wrapper.sh`
    * HTCondor submit file
* `segm_ppln.py`
    * Nipype based pipeline
    * **Before use**: set paths

## Requirements
* [ANTS](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
* python `nipype`
  (eventually add requirements.txt)