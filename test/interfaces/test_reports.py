import os
import shutil
import tempfile
import unittest

from nipype.pipeline import engine as pe
from niworkflows.data.getters import get_mni_template_ras

from fmriprep.interfaces.reports import BETRPT, FLIRTRPT, RegistrationRPT
from test.utils.tempdir import in_temporary_directory

MNI_DIR = get_mni_template_ras()

class TestFLIRTRPT(unittest.TestCase):
    def setUp(self):
        self.out_file = "test_flirt.nii.gz"

    @in_temporary_directory
    def test_known_file_out(self):
        flirt_rpt = pe.Node(
            FLIRTRPT(generate_report=True),
            name='TestFLIRTRPT'
        )
        flirt_rpt.inputs.reference = os.path.join(MNI_DIR,
                                                  'MNI152_T1_1mm.nii.gz')
        flirt_rpt.inputs.in_file = os.path.join(MNI_DIR,
                                                'MNI152_T1_1mm.nii.gz')
        flirt_rpt.inputs.out_file = self.out_file
        flirt_rpt.run()
        html_report = flirt_rpt.outputs.html_report
        self.assertTrue(os.path.isfile(html_report), 'HTML report exists at {}'
                        .format(html_report))

class TestBETRPT(unittest.TestCase):
    ''' tests it using mni as in_file '''

    def test_generate_report(self):
        ''' test of BET's report under basic (output binary mask) conditions '''
        self._smoke(BETRPT(in_file=os.path.join(MNI_DIR, 'MNI152_T1_2mm.nii.gz'),
                           generate_report=True, mask=True))

    def test_cannot_generate_report(self):
        ''' Can't generate a report if there are no nifti outputs. '''
        with self.assertRaises(Warning):
            self._smoke(BETRPT(in_file=os.path.join(MNI_DIR, 'MNI152_T1_2mm.nii.gz'),
                               generate_report=True, outline=False, mask=False, no_output=True))

    def test_generate_report_from_4d(self):
        ''' if the in_file was 4d, it should be able to produce the same report
        anyway (using arbitrary volume) '''
        pass

    @in_temporary_directory
    def _smoke(self, bet_interface):
        bet_interface.run()

        html_report = bet_interface.aggregate_outputs().html_report
        self.assertTrue(os.path.isfile(html_report), 'HTML report exists at {}'
                        .format(html_report))
