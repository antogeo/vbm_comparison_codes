#!/home/antogeo/.venvs/age_pred/bin/python
"""
Preprocessing-pipeline based on ANTs registration toolbox.

Requirements
------------
- Installed ANTs & Nipype
- Atlas & Probability mask for brain extraction
- Input Data in BIDS or BIDS-like structure
- Inputs can be specified in command line interface (s.b.)

Analysis-steps
--------------
1. `N4BiasFieldCorrection`
   corrects for low frequency bias
2. `BrainExtraction`
   using brain template to extract brain
   (e.g. ICBM 2009a Nonlinear Asymmetric Atlas)
   Needed inputs:
   - brain_probability_mask = probability mask of intracranial tissues
     (GM, WM, CSF)
   - template_tmp = template image
    Note: Reslice Mask to make sure it s similar to brain nifti
3. `Atropos` segmentation
   finite mixture modeling (FMM) segmentation approach to identify 4 different
   tissue classes (GM)
4. `Registration` to MNI space, resampling and smoothing
   Linear transformations:
   - Translation (3 parameter)
   - Rigid: Only rotation and translation (6 parameter)
   - Affine: Rigid + scaling (9 (12?) parameter)
   Non-linear transformation:
   - BSplineSyN: diffeomorphic image registration
5. Jacobian: `CreateJacobianDeterminantImage`
6. Multiply Jacobian with MNI_GM

Note: extensive explanation can be found in the Nipype documentation, use
      `help('Function')`.
"""
import os
import os.path as op
from lib.leap.logging import (configure_logging, finish_logging,
                              logger)
import shutil
import traceback
import sys
import time
import argparse
from pathlib import Path

import nipype.interfaces.io as nio
import nipype.pipeline.engine as pe  # pypeline engine
from nipype.interfaces.ants import (N4BiasFieldCorrection, BrainExtraction,
                                    Registration, Atropos, ImageMath,
                                    CreateJacobianDeterminantImage,
                                    ApplyTransforms)
# from nipype.utils.filemanip import loadpkl
# res = loadpkl('path/to/pklz')


# functions to select specific instance from a multiple-output node
def get_first(in_file):
    return in_file[0]


def get_sec(in_file):
    return in_file[1]


def get_third(in_file):
    return in_file[2]


def get_forth(in_file):
    return in_file[3]


# set default paths for files (juseless)
db_path = '/data/project/age_prediction/extras/mni_icbm152_nlin_asym_09a'
def_templ = op.join(db_path, 'mni_icbm152_t1_tal_nlin_asym_09a.nii')
def_tpm = op.join(db_path, 'tpm_ICBM.nii')
def_tpm_gm = op.join(db_path, 'tpm_ICBM_01.nii.gz')
def_brainmask = op.join(db_path,
                        'mni_icbm152_t1_tal_nlin_asym_09a_mask.nii')
def_tpm_brain = op.join(db_path, 'intraTPM_sumICBM.nii')
def_tmp = '/tmp'
# db_path = '/data/project/age_prediction/datasets'
# template = op.join('/data/project/age_prediction/', 'extras',
#                    'mni_icbm152_nlin_asym_09a',
#                    'mni_icbm152_t1_tal_nlin_asym_09a.nii')
# tpm_gm = op.join('/data/project/age_prediction/', 'extras',
#                  'mni_icbm152_nlin_asym_09a',
#                  'tpm_ICBM_01.nii')
# subj_path = ''


# templ_folder = op.join('/data/project/age_prediction/',
#                        'extras', 'mni_icbm152_nlin_asym_09a')
# def_tpm_gm = op.join(templ_folder,
#                      'tpm_ICBM_01.nii.gz')
# def_templ = op.join(templ_folder,
#                     'mni_icbm152_t1_tal_nlin_asym_09a.nii')
# def_tpm = op.join(templ_folder,
#                   'tpm_ICBM.ni')
# def_tpm_brain = op.join(templ_folder,
#                         'mni_icbm152_t1_tal_nlin_asym_09a_mask.nii')

start_time = time.time()
start_point = time.ctime()

# Arguments provided in command line interface
parser = argparse.ArgumentParser()
parser.add_argument("-data_dir", help="path directory with subjects' folders",
                    required=True,
                    default=None)
parser.add_argument("-subj", help="subject's name", required=True,
                    default=None)
parser.add_argument("-out_dir", help="dir to save results",
                    default='')
parser.add_argument("-work_dir", help="working directory & temporary files",
                    default=def_tmp)
parser.add_argument("-tpm_gm", help="path to GM probability mask",
                    default=def_tpm_gm)
parser.add_argument("-template", help="path to template image",
                    default=def_templ)
parser.add_argument("-tpm", help="path to template image",
                    default=def_tpm)
parser.add_argument("-mask_brain", help="path to brain mask",
                    default=def_brainmask)
parser.add_argument("-tpm_brain", help="path to probability mask",
                    default=def_tpm_brain)
parser.add_argument('-debug', metavar='debug', type=bool,
                    help='Saves results of each step',
                    default=False)

args = parser.parse_args()
subj = args.subj
data_dir = args.data_dir
out_dir = Path(args.out_dir)
tpm_gm = Path(args.tpm_gm)
template = Path(args.template)
tpm = Path(args.tpm)
tpm_brain = Path(args.tpm_brain)
mask_brain = Path(args.mask_brain)
work_dir = Path(args.work_dir)
debug = args.debug

# Work in the SSD to speedup. Remove file subject's name if exists in tmp and
# create new. That way we are sure is empty.
# work_dir = work_dir / subj
# if work_dir.exists():
#     shutil.rmtree(work_dir)
#
# work_dir.mkdir(parents=True)

if tpm_gm == '':
    tpm_gm = def_tpm_gm
# logger preparation. For the moment I am not using extra log

log_path = Path(op.join(work_dir, 'log_failed_sbjs.log'))

configure_logging(log_path)

"""
Entry point: Nipype starts here.
If debug == True : saves outputs of each steps 2,3,4
"""

dim = 3
# If I am running it in laptop I can use more CPU to speed up. Useful for debug
if os.uname().nodename == 'bnbnb37':
    threads = 6
else:
    threads = 1

try:
    # create folders for anat & extras in tmp and copy files in
    logger.info('Copying data to temporary folder')
    logger.info('GM template used {}'.format(tpm_gm))
    extras_path = Path(work_dir) / 'extras'
    if extras_path.exists():
        shutil.rmtree(extras_path)
    extras_path.mkdir(parents=True)
    template_tmp = shutil.copy(template, extras_path)
    tpm_brain_tmp = shutil.copy(tpm_brain, extras_path)
    tpm_gm_tmp = shutil.copy(tpm_gm, extras_path)
    mask_brain_tmp = shutil.copy(mask_brain, extras_path)
    # cur_dir = os.getcwd()
    # os.chdir(work_dir)

    # 1. N4 bias field correction
    #
    # Node n4bc:
    # Calls the N4BiasFieldCorrection Routine from Nipype
    # Corrects for low frequency bias
    # Type help(N4BiasFieldCorrection) for detailed information.
    #
    #
    # Input:
    # - Dimension   = Dimension of the image (2, 3, 4; here: 3)
    # - Threads     = Number of threads used for computing (here: 1 or 6)
    # - Subj_vol    = Path or nifti for subject data (here: Pass the path to
    #                 the subject)
    # - bspline_fitting_distance = Spline distance in mm (???) (here: 300)
    #                              Defines the spline grid by setting the
    #                              distance between the control points
    # - shrink_factor = Descripes the shrinking factor of the image to reduce
    #                   computational time (here: 3)
    # - n_iterations = Describes the number of iterations for each step
    #                  (here: 40 40 40 40)
    #
    # Output:
    # - Nifti: 'n4bc_output_image.nii'
    # - output is operated by BrainExtraction (node brain_extr)
    #

    dg = pe.Node(interface=nio.DataGrabber(), name='data_in')
    dg.inputs.template = subj + '/**/*nii*'
    dg.inputs.base_directory = data_dir
    dg.inputs.sort_filelist = True

    n4bc = pe.Node(interface=N4BiasFieldCorrection(), name='n4biascorrection')
    n4bc.inputs.dimension = dim
    n4bc.inputs.num_threads = threads
    # n4bc.inputs.input_image = subj_vol
    # define the spline grid by setting the distance between the control points
    n4bc.inputs.bspline_fitting_distance = 300
    # Defines how much the image should be upsampled before estimating the
    # inhomogeneity field. Increase if you want to reduce the execution time.
    # 1 corresponds to the original resolution. Larger values will
    # significantly reduce the computation time.
    n4bc.inputs.shrink_factor = 3
    # Maximum number of iterations at each level of resolution
    n4bc.inputs.n_iterations = [40, 40, 40, 40]
    # n4bc.inputs.output_image = 'n4bc_output_image.nii'

    #  2. Brain extraction
    #  Reslice mask to make sure it is similar to brain nifti
    #  Input
    #  template_tmp = given by user/directory of path (???) (Template)
    #  tpm_brain_tmp = goiven by user/directory of path (???) (Probabilty Mask)
    brain_extr = pe.Node(interface=BrainExtraction(), name='brainextraction')
    brain_extr.inputs.dimension = dim
    brain_extr._num_threads = threads
    brain_extr.inputs.brain_template = template_tmp
    brain_extr.inputs.brain_probability_mask = tpm_brain_tmp
    brain_extr.inputs.image_suffix = 'nii'

    # 3. Atropos segmentation
    atropos = pe.Node(interface=Atropos(), name='atropos')
    atropos.inputs.dimension = dim
    # To initialize the FMM parameters, one of the following options must be
    # specified. If one does not have prior label or probability images we
    # recommend using kmeans as it is typically faster than otsu and can be
    # used with multivariate initialization. However, since a Euclidean
    # distance on the inter cluster distances is used, one might have
    # to appropriately scale the additional input images. Random
    # initialization is meant purely for intellectual curiosity.
    # The prior weighting (specified in the range [0,1]) is used to modulate
    # the calculation of the posterior probabilities between the
    # likelihood*mrfprior and the likelihood*mrfprior*prior. For specifying
    # many prior probability images for a multi-label segmentation, we offer
    # a minimize usage option (see -m). With that option one can specify a
    # prior probability threshold in which only those pixels exceeding that
    # threshold are stored in memory.
    atropos.inputs.initialization = 'KMeans'
    atropos.inputs.number_of_tissue_classes = 4
    atropos.inputs.prior_probability_threshold = 0.0000001
    atropos.inputs.prior_weighting = 0
    atropos.inputs.likelihood_model = 'Gaussian'
    # Markov random field (MRF) theory provides a general framework for
    # enforcing spatially contextual constraints on the segmentation solution.
    # The default smoothing factor= 0.3 provides a moderate amount of smoothing
    # Increasing this number causes more smoothing and decreasing the number
    # lessens the smoothing. The radius parameter specifies the mrf
    # neighborhood. Different update schemes are possible but only the
    # asynchronous updating has theoretical convergence properties.
    atropos.inputs.mrf_smoothing_factor = 0.1
    atropos.inputs.mrf_radius = [1, 1, 1]
    # atropos.inputs.icm_use_synchronous_update = True
    # atropos.inputs.maximum_number_of_icm_terations = 1
    atropos.inputs.n_iterations = 5
    atropos.inputs.convergence_threshold = 0.000001
    atropos.inputs.posterior_formulation = 'Socrates'
    atropos.inputs.use_mixture_model_proportions = True
    atropos.inputs.save_posteriors = True

    # 4. Registration to MNI (affine + BsplineSyN)
    reg = pe.Node(interface=Registration(), name='registration2')
    reg.inputs.dimension = dim
    reg.inputs.num_threads = threads
    reg.inputs.fixed_image = tpm_gm_tmp
    # reg.inputs.fixed_image_mask = tpm_brain_tmp
    reg.inputs.output_transform_prefix = "MNI_"
    # First apply affine and then BSplineSyN
    reg.inputs.transforms = ['Translation', 'Rigid', 'Affine', 'BSplineSyN']
    # Affine[gradientStep]
    # BSplineSyN[gradientStep,updateFieldMeshSizeAtBaseLevel,
    # <totalFieldMeshSizeAtBaseLevel=0>,<splineOrder=3>]
    reg.inputs.transform_parameters = [(0.1,), (0.1,), (0.1,), (0.1, 26, 0, 3)]
    reg.inputs.number_of_iterations = [[1000, 500, 250, 100]] * 3 + [[
                                        100, 100, 70, 20]]
    # Convergence is determined from the number of iterations per level and is
    # determined by fitting a line to the normalized energy profile of the
    # last N iterations (N is specified by the window size) and determining
    # the slope which is then compared with the convergence threshold.
    reg.inputs.convergence_threshold = [1.e-8] * 3 + [1.e-9]
    reg.inputs.convergence_window_size = [20] * 3 + [15]

    reg.inputs.initialize_transforms_per_stage = False
    # Mattes[fixedImage,movingImage,metricWeight,numberOfBins,
    # <samplingStrategy={None,Regular,Random}>,<samplingPercentage=[0,1]>]
    # Mattes=MI "they are the same - for historical reasons we have 2 names
    # point to the same metric"
    reg.inputs.metric = ['Mattes'] * 3 + [['Mattes', 'CC']]
    reg.inputs.metric_weight = [1] * 3 + [[0.5, 0.5]]  # Default
    reg.inputs.radius_or_number_of_bins = [32] * 3 + [[32, 4]]
    reg.inputs.sampling_strategy = ['Random'] * 3 + [[None, None]]
    reg.inputs.sampling_percentage = [0.5] * 3 + [[None, None]]

    # Specify the sigma of gaussian smoothing at each level in 'vox' or 'mm')
    reg.inputs.smoothing_sigmas = [[3, 2, 1, 0]] * 4
    reg.inputs.sigma_units = ['vox'] * 4
    # Specify the shrink factor for the virtual domain at each level
    reg.inputs.shrink_factors = [[8, 4, 2, 1]] * 3 + [[6, 4, 2, 1]]
    reg.inputs.use_estimate_learning_rate_once = [True] * 4

    # Histogram match the images before registration
    reg.inputs.use_histogram_matching = [False] * 2 + [True] * 2
    reg.inputs.winsorize_lower_quantile = 0.005
    reg.inputs.winsorize_upper_quantile = 0.995
    reg.inputs.args = '--float'  # instead of double
    # save if debug mode is acivated
    reg.inputs.output_inverse_warped_image = False
    reg.inputs.collapse_output_transforms = True
    reg.inputs.output_warped_image = 'reg_warped_image.nii'
    reg.inputs.write_composite_transform = False

    # this resample is necessary because sometimes Brain_extraction outputs
    # have slightly different size
    resample = pe.Node(interface=ApplyTransforms(), name='resample')
    resample.inputs.transforms = 'identity'

    smooth = pe.Node(interface=ImageMath(), name='smooth')
    smooth.iterables = ('op2', ['2', '3', '4'])
    smooth.inputs.operation = 'G'

    at = pe.Node(interface=ApplyTransforms(), name='at')
    at.inputs.dimension = dim
    # at.inputs.input_image = 'POSTERIOR_02.nii.gz'
    at.inputs.reference_image = tpm_gm_tmp
    at.inputs.output_image = 'collapsedWarp.nii.gz'
    at.inputs.print_out_composite_warp_file = True
    # input shoud be 'reg.inputs.reverse_forward_transforms'
    # at.inputs.transforms = ['reg_1Warp.nii.gz', 'reg_0GenericAffine.mat']

    # 5. Calculate Jacobian
    jac = pe.Node(interface=CreateJacobianDeterminantImage(), name='jac')
    # jac.inputs.deformationField = 'reglin_warped_GM.nii'
    jac.inputs.imageDimension = dim
    # "For intensity modulation of GM probability, I think you want the
    # Jacobian determinant and not its log.
    jac.inputs.doLogJacobian = 0
    jac.inputs.outputImage = 'jac_outImage.nii'
    # jac.inputs.outputImage = 'jac_lin_outImage.nii'

    # 6. Multiply images with MNI_GM
    mul = pe.Node(interface=ImageMath(), name='mul')
    mul.inputs.operation = 'm'

    # save outputs
    datasink = pe.Node(nio.DataSink(), name='sinker')
    datasink.inputs.base_directory = work_dir.as_posix()

    segmentation = pe.Workflow(name="segmentation")

    segmentation.connect(dg, 'outfiles', n4bc, 'input_image')

    segmentation.connect(n4bc, 'output_image', brain_extr, 'anatomical_image')

    segmentation.connect(brain_extr, 'BrainExtractionBrain',
                         atropos, 'intensity_images')
    segmentation.connect(brain_extr, 'BrainExtractionMask',
                         resample, 'input_image')
    segmentation.connect(brain_extr, 'BrainExtractionBrain',
                         resample, 'reference_image')
    segmentation.connect(resample, 'output_image',
                         atropos, 'mask_image')
    segmentation.connect(atropos, ('posteriors', get_third),
                         datasink, 'posteriors')
    segmentation.connect(atropos, ('posteriors', get_third),
                         reg, 'moving_image')
    segmentation.connect(atropos, ('posteriors', get_third),
                         at, 'input_image')
    segmentation.connect(reg, 'reverse_forward_transforms',
                         at, 'transforms')
    segmentation.connect(at, 'output_image',
                         jac, 'deformationField')
    # Create preproc output graph
    segmentation.connect([(jac, mul, [('jacobian_image', 'op1')]),
                         (reg, mul, [('warped_image', 'op2')])])
    segmentation.connect(mul, 'output_image',
                         datasink, 'gm_mod')
    segmentation.connect(mul, 'output_image', smooth, 'op1')
    segmentation.connect(reg, 'warped_image',
                         datasink, 'mni')
    segmentation.connect(brain_extr, 'BrainExtractionBrain',
                         datasink, 'brain')
    segmentation.connect(smooth, 'output_image', datasink, 'smooth')

    segmentation.write_graph(graph2use='hierarchical',
                             dotfilename='./graph_hierarchical.dot',
                             format='png', simple_form=True)
    segmentation.run()

except Exception:
    # Create log file
    msg = traceback.format_exc()
    subj_name = os.listdir(op.join(work_dir, subj, 'anat'))[0]
    logger.error(msg + '\nFailed to run ("%s")' % subj_name)
    elapsed_time = time.time() - start_time
    logger.error('Elapsed time {}'.format(
        time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    shutil.copy(log_path, out_dir)
    sys.exit(-1)
finally:
    if out_dir.exists():
        if out_dir.is_dir():
            shutil.rmtree(out_dir)
        else:
            # removes (deletes) the file path
            out_dir.unlink()
    shutil.copytree(work_dir, out_dir)
    logger.info('Cleaning up')
    elapsed_time = time.time() - start_time
    logger.info('Elapsed time {}'.format(
        time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    logger.info('Running pipeline done')
    finish_logging()
    # logging.info('Cleaning up')
    # elapsed_time = time.time() - start_time
    # logging.info('Elapsed time {}'.format(
    #     time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    # logging.shutdown()

    # This is done by HTCondor, but just to be sure...
    # shutil.rmtree(work_dir)
