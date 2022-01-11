import ntpath
import zipfile
import re
import gzip
import os
from pyteomics import mgf, mzml, ms2
from abc import ABC, abstractmethod
import numpy as np
import io
import tarfile
import mmap
from lxml.etree import XMLSyntaxError


class PeakListParseError(Exception):
    pass


class SpectrumIdFormatError(Exception):
    pass


class ScanNotFoundException(Exception):
    pass


class Spectrum:
    def __init__(self, precursor, mz_array, int_array, scan_id, rt=np.nan, file_name='',
                 source_path='', run_name='', scan_number=-1, scan_index=-1, title=''):
        """
        Initialise a Spectrum object.

        :param precursor: (dict) Spectrum precursor information as dict.  e.g. {'mz':
            102.234, 'charge': 2, 'intensity': 12654.35}
        :param mz_array: (ndarray, dtype: float64) m/z values of the spectrum peaks
        :param int_array: (ndarray, dtype: float64) intensity values of the spectrum peaks
        :param scan_id: (str) Unique scan identifier
        :param rt: (str) Retention time in seconds (can be a range, e.g 60-62)
        :param file_name: (str) Name of the peaklist file
        :param source_path: (str) Path to the peaklist source
        :param run_name: (str) Name of the MS run
        :param scan_number: (int) Scan number of the spectrum
        :param scan_index: (int) Index of the spectrum in the file
        """
        self.precursor = precursor
        self.scan_id = scan_id
        self.scan_number = scan_number
        self.scan_index = scan_index
        self.rt = rt
        self.file_name = file_name
        self.source_path = source_path
        self.run_name = run_name
        self.title = title
        mz_array = np.asarray(mz_array, dtype=np.float64)
        int_array = np.asarray(int_array, dtype=np.float64)
        # make sure that the m/z values are sorted asc
        sorted_indices = np.argsort(mz_array)
        # convert to list because psycopg2 can't handle numpy arrays
        self.mz_values = mz_array[sorted_indices].tolist()
        self.int_values = int_array[sorted_indices].tolist()
        self._precursor_mass = None


    # @property
    # def precursor_charge(self):
    #     """Get the precursor charge state."""
    #     return self.precursor['charge']
    #
    # @property
    # def precursor_mz(self):
    #     """Get the precursor m/z."""
    #     return self.precursor['mz']
    #
    # @precursor_mz.setter
    # def precursor_mz(self, mz):
    #     self._precursor_mass = None
    #     self.precursor['mz'] = mz
    #
    # @property
    # def precursor_int(self):
    #     """Get the precursor intensity."""
    #     return self.precursor['intensity']
    #
    # @property
    # def precursor_mass(self):
    #     """Return the neutral mass of the precursor."""
    #     if self._precursor_mass is None:
    #         self._precursor_mass = (self.precursor['mz'] - const.proton_mass) *\
    #             self.precursor['charge']
    #     return self._precursor_mass


class PeakListWrapper:
    def __init__(self, pl_path, file_format_accession, spectrum_id_format_accession):
        self.file_format_accession = file_format_accession
        self.spectrum_id_format_accession = spectrum_id_format_accession
        self.peak_list_path = pl_path
        self.peak_list_file_name = os.path.split(pl_path)[1]

        try:
            # create the reader
            if self.is_mzml():
                self.reader = MZMLReader(spectrum_id_format_accession)
            elif self.is_mgf():
                self.reader = MGFReader(spectrum_id_format_accession)
            elif self.is_ms2():
                self.reader = MS2Reader(spectrum_id_format_accession)
            # load the file
            self.reader.load(pl_path)
        except Exception as e:
            message = "Error reading peak list file {0}: {1} - Arguments:\n{2!r}".format(
                self.peak_list_file_name, type(e).__name__, e.args)
            raise PeakListParseError(message)

    def __getitem__(self, spec_id):
        """Return the spectrum depending on the FileFormat and SpectrumIdFormat."""
        return self.reader[spec_id]

    def is_mgf(self):
        return self.file_format_accession == 'MS:1001062'

    def is_mzml(self):
        return self.file_format_accession == 'MS:1000584'

    def is_ms2(self):
        return self.file_format_accession == 'MS:1001466'

    @staticmethod
    def extract_gz(in_file):
        if in_file.endswith('.gz'):
            in_f = gzip.open(in_file, 'rb')
            in_file = in_file.replace(".gz", "")
            out_f = open(in_file, 'wb')
            out_f.write(in_f.read())
            in_f.close()
            out_f.close()

            return in_file

        else:
            raise Exception(f"unsupported file extension for: {in_file}")

    @staticmethod
    def unzip_peak_lists(zip_file, out_path='.'):
        """
        Unzip and return resulting folder.

        :param zip_file: path to archive to unzip
        :param out_path: where to extract the files
        :return: resulting folder
        """
        if zip_file.endswith(".zip"):
            zip_ref = zipfile.ZipFile(zip_file, 'r')
            unzip_path = os.path.join(str(out_path), ntpath.basename(zip_file + '_unzip'))
            zip_ref.extractall(unzip_path)
            zip_ref.close()

            return unzip_path

        else:
            raise Exception(f"unsupported file extension for: {zip_file}")

    @staticmethod
    def get_ion_types_mzml(scan):
        frag_methods = {
            'beam-type collision-induced dissociation': ["b", "y"],
            'collision-induced dissociation': ["b", "y"],
            'electron transfer dissociation': ["c", "z"],
        }
        # get fragMethod and translate that to Ion Types
        ion_types = []
        for key in scan.keys():
            if key in frag_methods.keys():
                ion_types += frag_methods[key]
        return ion_types


class SpectraReader(ABC):
    """Abstract Base Class for all SpectraReader."""

    def __init__(self, spectrum_id_format_accession):
        """
        Initialize the SpectraReader.
        """
        self._reader = None
        self.spectrum_id_format_accession = spectrum_id_format_accession
        self._source = None
        self.file_name = None
        self.source_path = None

    @abstractmethod
    def load(self, source, file_name=None, source_path=None):
        """
        Load the spectrum file.

        :param source: Spectra file source
        :param file_name: (str) filename
        :param source_path: (str) path to the source file (peak list file or archive)
        """
        self._source = source
        if source_path is None:
            if type(source) == str:
                self.source_path = source
            elif issubclass(type(source), io.TextIOBase) or \
                    issubclass(type(source), tarfile.ExFileObject):
                self.source_path = source.name
        else:
            self.source_path = source_path

        if file_name is None:
            self.file_name = ntpath.basename(self.source_path)
        else:
            self.file_name = file_name

    @abstractmethod
    def __getitem__(self, spec_id):
        """
        Return the spectrum depending on the SpectrumIdFormat.

        """
        ...

    @abstractmethod
    def _convert_spectrum(self, spec_id, spec):
        """Convert the spectrum from the reader to a Spectrum object."""
        ...

    # @abstractmethod
    # def count_spectra(self):
    #     """
    #     Count the number of spectra.
    #
    #     :return (int) Number of spectra in the file
    #     """
    #     ...


class MGFReader(SpectraReader):
    """SpectraReader for MGF files."""

    def __getitem__(self, spec_id):
        """
        Return the spectrum depending on the SpectrumIdFormat.

        """
        # MS:1000774 multiple peak list nativeID format - zero based
        # index=xsd:nonNegativeInteger
        if self.spectrum_id_format_accession == 'MS:1000774':
            try:
                matches = re.match("index=([0-9]+)", spec_id).groups()
                spec_id = int(matches[0])

            # try to cast spec_id to int if re doesn't match -> PXD006767 has this format
            # ToDo: do we want to be stricter?
            except (TypeError, AttributeError, IndexError):
                try:
                    spec_id = int(spec_id)
                except ValueError:
                    raise PeakListParseError("invalid spectrum ID format!")
            spec = self._reader[spec_id]

        # MS:1000775 single peak list nativeID format
        # The nativeID must be the same as the source file ID.
        # Used for referencing peak list files with one spectrum per file,
        # typically in a folder of PKL or DTAs, where each sourceFileRef is different.
        elif self.spectrum_id_format_accession == 'MS:1000775':
            spec = self._reader[0]

        # # MS:1000768 Thermo nativeID format: ToDo: not supported for now.
        # # controllerType=xsd:nonNegativeInt controllerNumber=xsd:positiveInt scan=xsd:positiveInt
        # if self.spectrum_id_format_accession == 'MS:1000768':
        #     raise SpectrumIdFormatError(
        #         "Combination of spectrumIdFormat and FileFormat not supported.")

        else:
            raise SpectrumIdFormatError(
                    "Combination of spectrumIdFormat and FileFormat not supported.")

        return self._convert_spectrum(spec_id, spec)

    def load(self, source, file_name=None, source_path=None):
        """
        Load MGF file.

        :param source: file source, path or stream
        :param file_name: (str) MGF filename
        :param source_path: (str) path to the source file (MGF or archive)
        """
        self._reader = mgf.read(source, use_index=True)
        super().load(source, file_name, source_path)

    def count_spectra(self):
        """
        Count the number of spectra.

        :return (int) Number of spectra in the file.
        """
        if issubclass(type(self._source), io.TextIOBase):
            text = self._source.read()
            result = len(list(re.findall('BEGIN IONS', text)))
            self._source.seek(0)
        else:
            with open(self._source, 'r+') as f:
                text = mmap.mmap(f.fileno(), 0)
                result = len(list(re.findall(b'BEGIN IONS', text)))
                text.close()
        return result

    def _convert_spectrum(self, scan_index, spec):
        """Convert the spectrum from the reader to a Spectrum object."""
        precursor = {
            'mz': spec['params']['pepmass'][0],
            'charge': spec['params']['charge'][0],
            'intensity': spec['params']['pepmass'][1]
        }

        # # parse retention time, default to NaN
        # rt = mgf_spec['params'].get('rtinseconds', np.nan)
        #
        # # try to parse scan number and run_name from title
        # title = mgf_spec['params'].get('title', '')
        # run_name_match = re.search(self._re_run_name, title)
        # try:
        #     run_name = run_name_match.group(1)
        # except AttributeError:
        #     run_name = self.default_run_name
        #
        # scan_number_match = re.search(self._re_scan_number, title)
        # try:
        #     scan_number = int(scan_number_match.group(1))
        # except (AttributeError, ValueError):
        #     scan_number = -1

        return Spectrum(precursor, spec['m/z array'], spec['intensity array'], scan_index)


class MZMLReader(SpectraReader):
    """SpectraReader for mzML files."""

    def __init__(self, spectrum_id_format_accession):
        super().__init__(spectrum_id_format_accession)
        self.default_run_name = None

    def __getitem__(self, spec_id):
        """
        Return the spectrum depending on the SpectrumIdFormat.

        """
        # MS:1001530 mzML unique identifier:
        # Used for referencing mzML. The value of the spectrum ID attribute is referenced directly.
        if self.spectrum_id_format_accession == 'MS:1001530':
            spec = self._reader.get_by_id(spec_id)

        # ToDo: not supported for now.
        # # MS:1000768 Thermo nativeID format:
        # # controllerType=xsd:nonNegativeInt controllerNumber=xsd:positiveInt scan=xsd:positiveInt
        # elif self.spectrum_id_format_accession == 'MS:1000768':
        #     raise SpectrumIdFormatError(
        #         "Combination of spectrumIdFormat and FileFormat not supported.")
        #
        # # MS:1000774 multiple peak list nativeID format - zero based
        # elif self.spectrum_id_format_accession == 'MS:1000774':
        #     raise SpectrumIdFormatError(
        #         "Combination of spectrumIdFormat and FileFormat not supported.")
        #
        # # MS:1000775 single peak list nativeID format
        # # The nativeID must be the same as the source file ID.
        # # Used for referencing peak list files with one spectrum per file,
        # # typically in a folder of PKL or DTAs, where each sourceFileRef is different.
        # elif self.spectrum_id_format_accession == 'MS:1000775':
        #     raise SpectrumIdFormatError(
        #         "Combination of spectrumIdFormat and FileFormat not supported.")

        else:
            raise SpectrumIdFormatError(
                "Combination of spectrumIdFormat and FileFormat not supported.")

        return self._convert_spectrum(spec_id, spec)

    def load(self, source, file_name=None, source_path=None):
        """
        Read in spectra from an mzML file and stores them as Spectrum objects.

        :param source: file source, path or stream
        :param file_name: (str) mzML filename
        :param source_path: (str) path to the source file (mzML or archive)
        """
        self._reader = mzml.read(source)
        if self._reader.index is None:
            self._reader = mzml.read(source, use_index=True)
        super().load(source, file_name, source_path)

        # get the default run name
        if issubclass(type(self._source), tarfile.ExFileObject) or \
                issubclass(type(self._source), zipfile.ZipExtFile):
            text = self._source.read()
            result = re.finditer(b'defaultSourceFileRef="(.*)"', text)
            try:
                result = result.__next__().groups()
            except StopIteration:
                result = None
            self._source.seek(0)
        else:
            with open(self._source, 'r+') as f:
                text = mmap.mmap(f.fileno(), 0)
                result = re.finditer(b'defaultSourceFileRef="(.*)"', text)
                try:
                    result = result.__next__().groups()
                except StopIteration:
                    result = None
                text.close()
        if result is not None:
            self.default_run_name = self._reader.get_by_id(result[0].decode('ascii'))['name']
        else:
            # try to get the default run name from sourceFileList:
            try:
                source_files = list(self._reader.iterfind('//sourceFileList'))[0]
                # if there is more than one entry we can't determine the default
                if source_files['count'] != 1:
                    self.default_run_name = file_name
                else:
                    self.default_run_name = source_files['sourceFile'][0]['name']
            except XMLSyntaxError:
                self.default_run_name = file_name
            self.reset()

    def reset(self):
        """Reset the reader."""
        if issubclass(type(self._source), tarfile.ExFileObject) or \
                issubclass(type(self._source), zipfile.ZipExtFile):
            self._source.seek(0)
            self._reader = mzml.read(self._source)
        else:
            self._reader.reset()

    def count_spectra(self):
        """
        Count the number of spectra.
        :return (int) Number of spectra in the file.
        """
        return len(self._reader)

    def _convert_spectrum(self, spec_id, spec):

        # check for single scan per spectrum
        if spec['scanList']['count'] != 1:
            raise ValueError(
                "xiSEARCH2 currently only supports a single scan per spectrum.")
        scan = spec['scanList']['scan'][0]

        # check for single precursor per spectrum
        if spec['precursorList']['count'] != 1 or \
                spec['precursorList']['precursor'][0]['selectedIonList']['count'] != 1:
            raise ValueError(
                "xiSEARCH2 currently only supports a single precursor per spectrum.")
        p = spec['precursorList']['precursor'][0]['selectedIonList']['selectedIon'][0]

        # create precursor dict
        precursor = {
            'mz': p['selected ion m/z'],
            'charge': p.get('charge state', np.nan),
            'intensity': p.get('peak intensity', np.nan)
        }

        # id is required in mzML so set this as scan_id
        scan_id = spec['id']

        # index is also required in mzML so just use this
        scan_index = spec['index']

        # parse retention time, default to NaN
        rt = scan.get('scan start time', np.nan)
        rt = rt * 60

        # sourceFileRef can optionally reference the 'id' of the appropriate sourceFile.
        if hasattr(spec, 'sourceFileRef'):
            run_name = self._reader.get_element_by_id(spec['sourceFileRef'])['name']
        else:
            run_name = self.default_run_name

        # # try to parse scan number from scan_id
        # scan_number_match = re.search(self._re_scan_number, scan_id)
        # try:
        #     scan_number = int(scan_number_match.group(1))
        # except (AttributeError, ValueError):
        #     scan_number = None

        return Spectrum(precursor, spec['m/z array'], spec['intensity array'], scan_id,
                        rt, self.file_name, self.source_path, run_name, scan_index=scan_index)


class MS2Reader(SpectraReader):
    """SpectraReader for MS2 files."""

    def __getitem__(self, spec_id):
        """Return the spectrum depending on the SpectrumIdFormat."""
        # MS:1000774 multiple peak list nativeID format - zero based
        if self.spectrum_id_format_accession == 'MS:1000774':
            try:
                matches = re.match("index=([0-9]+)", spec_id).groups()
                spec_id = int(matches[0])

            # try to cast spec_id to int if re doesn't match -> PXD006767 has this format
            # ToDo: do we want to be stricter?
            except (AttributeError, IndexError):
                try:
                    spec_id = int(spec_id)
                except ValueError:
                    raise PeakListParseError("invalid spectrum ID format!")
            spec = self._reader[spec_id]

        # MS:1000775 single peak list nativeID format
        # The nativeID must be the same as the source file ID.
        # Used for referencing peak list files with one spectrum per file,
        # typically in a folder of PKL or DTAs, where each sourceFileRef is different.
        elif self.spectrum_id_format_accession == 'MS:1000775':
            spec = self._reader[0]

        # ToDo: not supported for now.
        # # MS:1000768 Thermo nativeID format:
        # # controllerType=xsd:nonNegativeInt controllerNumber=xsd:positiveInt scan=xsd:positiveInt
        # if self.spectrum_id_format_accession == 'MS:1000768':
        #     raise SpectrumIdFormatError(
        #         "Combination of spectrumIdFormat and FileFormat not supported.")

        else:
            raise SpectrumIdFormatError(
                "Combination of spectrumIdFormat and FileFormat not supported.")
        return self._convert_spectrum(spec_id, spec)

    def load(self, source, file_name=None, source_path=None):
        """
        Load MS2 file.

        :param source: file source, path or stream
        :param file_name: (str) MS2 filename
        :param source_path: (str) path to the source file (MS2 or archive)
        """
        self._reader = ms2.read(source, use_index=True)
        super().load(source, file_name, source_path)

    def count_spectra(self):
        """
        Count the number of spectra.

        :return (int) Number of spectra in the file.
        """
        raise NotImplemented()
        # if issubclass(type(self._source), io.TextIOBase):
        #     text = self._source.read()
        #     result = len(list(re.findall('BEGIN IONS', text)))
        #     self._source.seek(0)
        # else:
        #     with open(self._source, 'r+') as f:
        #         text = mmap.mmap(f.fileno(), 0)
        #         result = len(list(re.findall(b'BEGIN IONS', text)))
        #         text.close()
        # return result

    def _convert_spectrum(self, scan_index, spec):
        precursor = {
            'mz': spec['params']['pepmass'][0],
            'charge': spec['params']['charge'][0],
            'intensity': spec['params']['pepmass'][1]
        }

        # # parse retention time, default to NaN
        # rt = mgf_spec['params'].get('rtinseconds', np.nan)
        #
        # # try to parse scan number and run_name from title
        # title = mgf_spec['params'].get('title', '')
        # run_name_match = re.search(self._re_run_name, title)
        # try:
        #     run_name = run_name_match.group(1)
        # except AttributeError:
        #     run_name = self.default_run_name
        #
        # scan_number_match = re.search(self._re_scan_number, title)
        # try:
        #     scan_number = int(scan_number_match.group(1))
        # except (AttributeError, ValueError):
        #     scan_number = -1

        return Spectrum(precursor, spec['m/z array'], spec['intensity array'], scan_index)
