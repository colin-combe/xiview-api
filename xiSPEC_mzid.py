import pyteomics.mzid as py_mzid
import pyteomics.mgf as py_mgf
import pymzml
import re
import ntpath
import json
import sys
import xiSPEC_sqlite as db


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_ion_types_mzid(sid_item, logger):
    try:
        ion_names_list = [i['name'] for i in sid_item['IonType']]
        ion_names_list = list(set(ion_names_list))
    except KeyError:
        return []

    # ion_types = ["P"]
    ion_types = []
    for ion_name in ion_names_list:
        try:
            ion = re.search('frag: ([a-z]) ion', ion_name).groups()[0]
            ion_types.append(ion)
        except (IndexError, AttributeError) as e:
            logger.info(e, ion_name)
            continue

    return ion_types


def get_ion_types_mzid(sid_item, logger):
    try:
        ion_names_list = [i['name'] for i in sid_item['IonType']]
        ion_names_list = list(set(ion_names_list))
    except KeyError:
        return []

    # ion_types = ["P"]
    ion_types = []
    for ion_name in ion_names_list:
        try:
            ion = re.search('frag: ([a-z]) ion', ion_name).groups()[0]
            ion_types.append(ion)
        except (IndexError, AttributeError) as e:
            logger.info(e, ion_name)
            continue

    return ion_types


def get_ion_types_mzml(mzml_scan):
    frag_methods = {
        'beam-type collision-induced dissociation': ["b", "y"],
        'collision-induced dissociation': ["b", "y"],
        'electron transfer dissociation': ["c", "z"],
    }
    # get fragMethod and translate that to Ion Types
    ion_types = []
    for key in mzml_scan.keys():
        if key in frag_methods.keys():
            ion_types += frag_methods[key]
    return ion_types


def map_spectra_data_to_protocol(mzid_reader):
    """
    extract and map spectrumIdentificationProtocol which includes annotation data like fragment tolerance
    only fragment tolerance is extracted for now
    # ToDo: improve error handling
    #       extract modifications, cl mod mass, ...

    Parameters:
    ------------------------
    mzid_reader: pyteomics mzid_reader
    """

    spectra_data_protocol_map = {
        'errors': [],
    }

    for analysisCollection in mzid_reader.iterfind('AnalysisCollection'):
        for spectrumIdentification in analysisCollection['SpectrumIdentification']:
            sid_protocol_ref = spectrumIdentification['spectrumIdentificationProtocol_ref']
            sid_protocol = mzid_reader.get_by_id(sid_protocol_ref, detailed=True)
            frag_tol = sid_protocol['FragmentTolerance']
            try:
                frag_tol_plus = frag_tol['search tolerance plus value']
                frag_tol_value = re.sub('[^0-9,.]', '', str(frag_tol_plus['value']))
                if frag_tol_plus['unit'].lower() == 'parts per million':
                    frag_tol_unit = 'ppm'
                elif frag_tol_plus['unit'].lower() == 'dalton':
                    frag_tol_unit = 'Da'
                else:
                    frag_tol_unit = frag_tol_plus['unit']

            except KeyError:
                frag_tol_value = '10'
                frag_tol_unit = 'ppm'
                spectra_data_protocol_map['errors'].append(
                    {"type": "mzidParseError",
                     "message": "could not parse ms2tolerance. Falling back to default values."})

            if not all([
                frag_tol['search tolerance plus value']['value'] == frag_tol['search tolerance minus value']['value'],
                frag_tol['search tolerance plus value']['unit'] == frag_tol['search tolerance minus value']['unit']
            ]):
                spectra_data_protocol_map['errors'].append(
                    {"type": "mzidParseError",
                     "message": "search tolerance plus value doesn't match minus value. Using plus value!"})

            for inputSpectra in spectrumIdentification['InputSpectra']:
                spectra_data_ref = inputSpectra['spectraData_ref']

                spectra_data_protocol_map[spectra_data_ref] = {
                    'protocol_ref': sid_protocol_ref,
                    'fragmentTolerance': ' '.join([frag_tol_value, frag_tol_unit])
                }

    mzid_reader.reset()

    return spectra_data_protocol_map


# def parse(id_file, peak_list_reader, peak_list_type, logger):
#
#     idReader = py_mzid.MzIdentML(id_file)
#
#     logger.info('generating spectraData_ProtocolMap - start')
#     spectraData_ProtocolMap = map_spectra_data_to_protocol(idReader)
#     returnJSON['errors'] += spectraData_ProtocolMap['errors']
#     # ToDo: save FragmentTolerance to annotationsTable
#     logger.info('generating spectraData_ProtocolMap - done')


def get_cross_link_identifier(sid_item):
    # For reporting the evidence associated with the identification, within a given <SpectrumIdentificationResult>,
    # a pair of cross-linked peptides MUST be reported as two instances of <SpectrumIdentificationItem> through having
    # a shared local unique identifier as the value for the CV term "cross-link spectrum identification item" MS:1002511
    # The two instances of <SpectrumIdentificationItem> MUST also share the same value for the rank attribute.
    #
    # If a cross-linked pair of peptides has been identified, there MUST be two
    # <SpectrumIdentificationItem> elements with the same rank value. Both MUST have the
    # "cross-link spectrum identification item" cvParam, and the value acts as a local identifier
    # within the <SpectrumIdentificationResult> to group these two elements together. The
    # experimentalMassToCharge, calculateMassToCharge and chargeState MUST be identical
    # over both SII elements, indicating the overall values for the pair.

    # cl_id_item = str(int(sid_item['cross-link spectrum identification item']))
    # rank = str(sid_item['rank'])

    return sid_item['cross-link spectrum identification item']
    # return '_'.join([cl_id_item, rank])


def add_to_modlist(mod, modlist):
    # modlist_test = [
    #     {'name': "bs3nh2", 'monoisotopicMassDelta': 123, 'residues': ["A"]}
    # ]
    # mod1_test = {'name': "unknown_modification", 'monoisotopicMassDelta': 123, 'residues': ["B"]}
    # mod2_test = {'name': "bs3nh2", 'monoisotopicMassDelta': 1232, 'residues': ["B"]}
    # mod3_test = {'name': "bs3nh2", 'monoisotopicMassDelta': 12323, 'residues': ["A"]}
    # print add_to_modlist(mod1_test, modlist_test)
    # print modlist_test
    # print add_to_modlist(mod2_test, modlist_test)
    # print modlist_test
    # print add_to_modlist(mod3_test, modlist_test)
    # print modlist_test


    # def get_peaklist_from_mzml(scan):
    #     """
    #     Function to extract peaklist in xiAnnotator JSON format dict from mzml
    #
    #     Parameters:
    #     ------------------------
    #     scan, pymzml reader spectrum
    #     id: scanID
    #     """
    #
    #     if "profile spectrum" in scan.keys():
    #         peaks = scan.centroidedPeaks
    #     else:
    #         peaks = scan.centroidedPeaks
    #
    #     return [{"mz": peak[0], "intensity": peak[1]} for peak in peaks if peak[1] > 0]

    if mod['name'] == "unknown_modification":
        mod['name'] = "({0:.2f})".format(mod['monoisotopicMassDelta'])

    mod['monoisotopicMassDelta'] = round(float(mod['monoisotopicMassDelta']), 6)

    if mod['name'] in [m['name'] for m in modlist]:
        old_mod = modlist[[m['name'] for m in modlist].index(mod['name'])]
        # check if modname with different mass exists already
        if mod['monoisotopicMassDelta'] != old_mod['monoisotopicMassDelta']:
            mod['name'] += "*"
            add_to_modlist(mod, modlist)
        else:
            for res in mod['residues']:
                if res not in old_mod['residues']:
                    old_mod['residues'].append(res)
    else:
        modlist.append(mod)

    return mod['name']


def get_peptide_info(sid_items, mzid_reader, unimod_masses, logger):

    return_dict = {
        'peptides': [],
        'linkSites': [],
        'annotation': {'modifications': []},
        'cross-linker modMass': 0
    }

    all_mods = []  # Modifications list
    mod_aliases = {
        "amidated_bs3": "bs3nh2",
        "carbamidomethyl": "cm",
        "hydrolyzed_bs3": "bs3oh",
        "oxidation": "ox"
    }

    pep_index = 0
    target_decoy = []
    for sid_item in sid_items:  # len = 1 for linear

        # Target-Decoy
        peptide_evidences = [mzid_reader.get_by_id(s['peptideEvidence_ref']) for s in sid_item['PeptideEvidenceRef']]
        # ToDo: isDecoy might not be defined. How to handle? (could make use of pyteomics.mzid.is_decoy())
        try:
            decoy = peptide_evidences[0]['isDecoy']
        except KeyError:
            decoy = None
        target_decoy.append({"peptideId": pep_index, 'isDecoy': decoy})  # TODO: multiple PeptideEvidenceRefs TD?

        # proteins
        proteins = [mzid_reader.get_by_id(p['dBSequence_ref']) for p in peptide_evidences]
        protein_accessions = [p['accession'] for p in proteins]

        # convert pepsequence to dict
        pepId = sid_item['peptide_ref']
        peptide = mzid_reader.get_by_id(pepId, detailed=True)

        pep_seq_dict = []
        for aa in peptide['PeptideSequence']:
            pep_seq_dict.append({"Modification": "", "aminoAcid": aa})

        # add in modifications
        if 'Modification' in peptide.keys():
            for mod in peptide['Modification']:

                if 'monoisotopicMassDelta' not in mod.keys():
                    try:
                        mod['monoisotopicMassDelta'] = unimod_masses[mod['accession']]

                    except KeyError:
                        # ToDo: reimplement ouput error
                        # returnJSON['errors'].append({"type": "mzidParseError",
                        #                              "message": "could not get modification mass for modification {}" % mod})
                        continue

                link_index = 0  # TODO: multilink support

                if mod['location'] == 0:
                    mod_location = 0
                    n_terminal_mod = True
                elif mod['location'] == len(peptide['PeptideSequence']) + 1:
                    mod_location = mod['location'] - 2
                    c_terminal_mod = True
                else:
                    mod_location = mod['location'] - 1
                    n_terminal_mod = False
                    c_terminal_mod = False
                if 'residues' not in mod:
                    mod['residues'] = peptide['PeptideSequence'][mod_location]

                if 'name' in mod.keys():
                    # fix mod names
                    mod['name'] = mod['name'].lower()
                    mod['name'] = mod['name'].replace(" ", "_")
                    if mod['name'] in mod_aliases.keys():
                        mod['name'] = mod_aliases[mod['name']]
                    if 'cross-link donor' not in mod.keys() and 'cross-link acceptor' not in mod.keys():
                        mod['name'] = add_to_modlist(mod, all_mods)  # save to all mods list and get back new_name

                        if pep_seq_dict[mod_location]['Modification'] == '':
                            pep_seq_dict[mod_location]['Modification'] = mod['name']
                        else:
                            logger.error('double modification on aa')
                            logger.error(mod)
                            logger.error(pep_seq_dict[mod_location])

                # error handling for mod without name
                else:
                    # cross-link acceptor doesn't have a name
                    if 'cross-link acceptor' not in mod.keys():
                        logger.error('modification without name!')
                        logger.error(mod)

                # add CL locations
                if 'cross-link donor' in mod.keys() or 'cross-link acceptor' in mod.keys():
                    return_dict['linkSites'].append(mod_location - 1)
                    # return_dict['linkSites'].append(
                    #     {"id": link_index, "peptideId": pep_index, "linkSite": mod_location - 1})
                if 'cross-link donor' in mod.keys():
                    return_dict["cross-linker modMass"] = round(mod['monoisotopicMassDelta'], 6)

        pep_index += 1

        peptide_seq_with_mods = ''.join([''.join([x['aminoAcid'], x['Modification']]) for x in pep_seq_dict])
        return_dict['peptides'].append(peptide_seq_with_mods)

        # other parameters - should be the same for each paired sid
        return_dict['precursorCharge'] = sid_item['chargeState']
        return_dict['isDecoy'] = target_decoy
        return_dict['proteins'] = protein_accessions
        return_dict['passThreshold'] = sid_item['passThreshold']
        return_dict['scores'] = {k: v for k, v in sid_item.iteritems()
                   if 'score' in k.lower() or 'pvalue' in k.lower() or 'evalue' in k.lower()}
        for mod in all_mods:
            return_dict['annotation']['modifications'].append({
                'aminoAcids': mod['residues'],
                'id': mod['name'],
                'mass': mod['monoisotopicMassDelta']
            })

    return return_dict


def get_unimod_masses(unimod_path):
    masses = {}

    with open(unimod_path) as f:
        for line in f:
            if line.startswith('id: '):
                id = ''.join(line.replace('id: ', '').split())

            elif line.startswith('xref: delta_mono_mass '):
                mass = float(line.replace('xref: delta_mono_mass ', '').replace('"', ''))
                masses[id] = mass

    return masses


def parse(mzid_file, peak_list_file, unimod_path, cur, con, logger):
    logger.info('reading mzid - start')
    # schema: https://raw.githubusercontent.com/HUPO-PSI/mzIdentML/master/schema/mzIdentML1.2.0.xsd
    mzid_reader = py_mzid.MzIdentML(mzid_file)
    logger.info('reading mzid - done')

    unimod_masses = get_unimod_masses(unimod_path)

    return_json = {
        "response": "",
        "modifications": [],
        "errors": []
    }

    logger.info('generating spectra data protocol map - start')
    spectra_data_protocol_map = map_spectra_data_to_protocol(mzid_reader)
    return_json['errors'] += spectra_data_protocol_map['errors']
    # ToDo: save FragmentTolerance to annotationsTable
    logger.info('generating spectraData_ProtocolMap - done')

    mzid_item_index = 0
    spec_id_item_index = 0
    multiple_inj_list_identifications = []
    multiple_inj_list_peak_lists = []
    modifications = []

    # peakList file
    logger.info('reading peakList file - start')
    peak_list_file_name = ntpath.basename(peak_list_file).lower()
    if peak_list_file_name.endswith('.mzml'):
        peak_list_file_type = 'mzml'
        # premzml = mzml.PreIndexedMzML(mzml_file)
        # mzmlReader = py_mzml.read(peakList_file)
        pymzml_reader = pymzml.run.Reader(peak_list_file)

    elif peak_list_file_name.endswith('.mgf'):
        peak_list_file_type = 'mgf'
        mgf_reader = py_mgf.read(peak_list_file)
        peak_list_arr = [pl for pl in mgf_reader]
    logger.info('reading peakList file - done')

    # main loop
    logger.info('entering main loop')

    for mzid_item in mzid_reader:  # mzid_item = mzid_reader.next()

        # make_spec_id_pairs(mzid_item['SpectrumIdentificationItem'])
        spec_id_set = set()
        linear_index = -1  # negative index values for linear peptides

        for specIdItem in mzid_item['SpectrumIdentificationItem']:
            if 'cross-link spectrum identification item' in specIdItem.keys():
                spec_id_set.add(get_cross_link_identifier(specIdItem))
            else:  # assuming linear
                # misusing 'cross-link spectrum identification item' for linear peptides with negative index
                specIdItem['cross-link spectrum identification item'] = linear_index
                spec_id_set.add(get_cross_link_identifier(specIdItem))
                linear_index -= 1

        # extract scanID
        try:
            scan_id = int(mzid_item['peak list scans'])
        except KeyError:
            # ToDo: this might not work for all mzids. ProteomeDiscoverer 2.2 format 'scan=xx file=xx'
            matches = re.findall("scan=([0-9]+)", mzid_item["spectrumID"])
            if len(matches) > 0:

                # ToDo: handle multiple scans? Is this standard compliant?
                # found in https://github.com/HUPO-PSI/mzIdentML/blob/master/examples/1_2examples/crosslinking/OpenxQuest_example_added_annotations.mzid
                scan_ids = [int(m) for m in matches]
                if len(scan_ids) > 1:
                    return_json['errors'].append(
                        {"type": "mzidParseError",
                         "message": "More than one scan found for SpectrumIdentificationItem: %s" % mzid_item["spectrumID"],
                         'id': mzid_item['id']
                        })
                    continue
                else:
                    scan_id = scan_ids[0]
            else:
                return_json['errors'].append(
                    {"type": "mzidParseError", "message": "Error parsing scanID from mzidentml!"}
                )
                continue

        # peakList
        if peak_list_file_type == 'mzml':
            try:
                scan = pymzml_reader[scan_id]
            except KeyError:
                return_json['errors'].append({
                    "type": "mzmlParseError",
                    "message": "requested scanID %i not found in peakList file" % scan_id,
                    'id': mzid_item['id']
                })
                continue
            if scan['ms level'] == 1:
                return_json['errors'].append({
                    "type": "mzmlParseError",
                    "message": "requested scanID %i is not a MSn scan" % scan_id,
                    'id': mzid_item['id']
                })
                continue

            peak_list = "\n".join(["%s %s" % (mz, i) for mz, i in scan.peaks if i > 0])
            # peak_list = get_peaklist_from_mzml(scan)

        elif peak_list_file_type == 'mgf':
            try:
                scan = peak_list_arr[scan_id]
            except IndexError:
                return_json['errors'].append({
                    "type": "mzmlParseError",
                    "message": "requested scanID %i not found in peakList file" % scan_id,
                    'id': mzid_item['id']
                })
                continue
            peaks = zip(scan['m/z array'], scan['intensity array'])
            peak_list = "\n".join(["%s %s" % (mz, i) for mz, i in peaks if i > 0])

        multiple_inj_list_peak_lists.append([mzid_item_index, peak_list])

        ms2_tol = spectra_data_protocol_map[mzid_item['spectraData_ref']]['fragmentTolerance']

        # alternatives = []
        for SpecId in spec_id_set:
            paired_spec_id_items = [sid_item for sid_item in mzid_item['SpectrumIdentificationItem'] if
                                    sid_item['cross-link spectrum identification item'] == SpecId]

            # if len(paired_specIdItems) > 2:
            #     returnJSON['errors'].append({
            #         "type": "PeptideParseError",
            #         "message": "more than 2 peptides with the same cross-link id found",
            #         'id': mzidItem['id']
            #     })
            #     continue

            pep_info = get_peptide_info(paired_spec_id_items, mzid_reader, unimod_masses, logger)

            # fragmentation ions
            pep_info['ions'] = get_ion_types_mzid(paired_spec_id_items[0], logger)
            # if no ion types are specified in the id file check the mzML file
            if len(pep_info['ions']) == 0 and peak_list_file_type == 'mzml':
                pep_info['ions'] = get_ion_types_mzml(scan)

            pep_info['ions'] = list(set(pep_info['ions']))

            if len(pep_info['ions']) == 0:
                pep_info['ions'] = ['peptide', 'b', 'y']
                return_json['errors'].append(
                    {"type": "IonParsing", "message": "could not parse fragment ions assuming precursor-, b- and y-ion", 'id': mzid_item['id']})

            pep_info['ions'] = ';'.join(pep_info['ions'])

                # extract other useful info to display
            rank = paired_spec_id_items[0]['rank']

            # ToDo: handling for mzid that don't include isDecoy
            isDecoy = any([pep['isDecoy'] for pep in pep_info['isDecoy']])
            accessions = ";".join(pep_info['proteins'])

            # raw file name
            try:
                raw_file_name = mzid_item['spectraData_ref']
            except KeyError:
                return_json['errors'].append(
                    {"type": "mzidParseError", "message": "no spectraData_ref specified", 'id': mzid_item['id']})
                raw_file_name = ""

            try:
                raw_file_name = path_leaf(mzid_reader.get_by_id(raw_file_name)['location'])
            except KeyError:
                pass

            # passThreshold
            if pep_info['passThreshold']:
                pass_threshold = 1
            else:
                pass_threshold = 0

            # peps and linkpos
            pep1 = pep_info['peptides'][0]

            if len(pep_info['peptides']) > 1:
                linkpos1 = pep_info['linkSites'][0]
                pep2 = pep_info['peptides'][1]
                linkpos2 = pep_info['linkSites'][1]

            else:
                pep2 = ""
                linkpos1 = -1
                linkpos2 = -1

            multiple_inj_list_identifications.append(
                [spec_id_item_index,
                 mzid_item['id'],
                 pep1,
                 pep2,
                 linkpos1,
                 linkpos2,
                 pep_info['precursorCharge'],
                 pass_threshold,
                 ms2_tol,
                 pep_info['ions'],
                 pep_info["cross-linker modMass"],
                 rank,
                 json.dumps(pep_info['scores']),
                 isDecoy,
                 accessions,
                 raw_file_name,
                 scan_id,
                 mzid_item_index]
            )

            # add mods to global modList
            for mod in pep_info['annotation']['modifications']:
                if mod['id'] not in [m['id'] for m in modifications]:
                    modifications.append(mod)
                else:
                    old_mod = modifications[[m['id'] for m in modifications].index(mod['id'])]
                    # check if modname with different mass exists already
                    for res in mod['aminoAcids']:
                        if res not in old_mod['aminoAcids']:
                            old_mod['aminoAcids'].append(res)

            spec_id_item_index += 1

        mzid_item_index += 1

        if spec_id_item_index % 500 == 0:
            logger.info('writing 500 entries to DB')
            try:
                multiple_inj_list_identifications = db.write_identifications(multiple_inj_list_identifications, cur, con)
                multiple_inj_list_peak_lists = db.write_peaklists(multiple_inj_list_peak_lists, cur, con)

            except db.DBException as e:
                return_json['errors'].append(
                    {"type": "dbError",
                     "message": e.args[0],
                     'id': spec_id_item_index
                     })
                sys.exit(1)

            # commit changes
            con.commit()

    # once loop is done write remaining data to DB
    logger.info('writing remaining entries to DB')
    try:
        db.write_identifications(multiple_inj_list_identifications, cur, con)
        db.write_peaklists(multiple_inj_list_peak_lists, cur, con)

        # modifications
        mod_index = 0
        multiple_inj_list_modifications = []
        for mod in modifications:
            multiple_inj_list_modifications.append([mod_index, mod['id'], mod['mass'], ''.join(mod['aminoAcids'])])
            mod_index += 1
        db.write_modifications(multiple_inj_list_modifications, cur, con)

    except db.DBException as e:
        return_json['errors'].append(
            {"type": "dbError",
             "message": e.args[0],
             'id': spec_id_item_index
             })
        sys.exit(1)

    return return_json