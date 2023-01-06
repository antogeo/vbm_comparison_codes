import nibabel as nib
import numpy as np


def make_nii(atlas_path, reg_values, rm_zeros=None):
    atlas_img = nib.load(atlas_path)
    # Flatten
    atlas_flat = np.round(atlas_img.get_fdata().reshape(-1)).astype(np.int)
    all_values = np.unique(atlas_flat)
    if rm_zeros is None:
        values = [s for s in all_values if s != 0]
    else:
        values = all_values
    # initialize mem
    mat1D = np.zeros(len(atlas_flat), dtype=np.float)
    for cntr, value in enumerate(values):
        # print(value, cntr)
        mat1D[atlas_flat == value] = reg_values[cntr]
    mat3D = mat1D.reshape(atlas_img.dataobj.shape)
    affine = atlas_img.affine
    empty_header = nib.Nifti1Header()
    stat_map_vol = nib.Nifti1Image(mat3D, affine, empty_header)
    return(stat_map_vol)
