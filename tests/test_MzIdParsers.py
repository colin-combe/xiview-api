from parser import MzIdParser
from parser.writer import Writer
import os
import logging
from sqlalchemy import create_engine, text
from create_db_schema import create_schema, create_db, drop_db
import pytest
from uuid import uuid4

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def fixture_path(file):
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "fixtures", file)


@pytest.fixture()
def db_info():
    # returns the test database credentials
    return {
        "hostname": "localhost",
        "port": "5432",
        "db": "ximzid_unittests",
        "dbuser": "ximzid_unittests",
        "dbpassword": "ximzid_unittests",
    }


@pytest.fixture()
def engine(db_info):
    # A new SqlAlchemy connection to the test database
    return create_engine(
        f"postgresql://{db_info['dbuser']}"
        f":{db_info['dbpassword']}@{db_info['hostname']}/{db_info['db']}"
    )


@pytest.fixture()
def use_database(db_info):
    # Create a temporary test Postgresql database
    create_db(
        db=db_info["db"], dbuser=db_info["dbuser"], dbpassword=db_info["dbpassword"]
    )
    create_schema(
        db=db_info["db"], dbuser=db_info["dbuser"], dbpassword=db_info["dbpassword"]
    )
    yield
    drop_db(
        db=db_info["db"], dbuser=db_info["dbuser"], dbpassword=db_info["dbpassword"]
    )


def parse_mzid_into_postgresql(mzid_file, peaklist, tmpdir, db_info, use_database, engine):
    # create temp user for user_id
    user_id = uuid4()
    with engine.connect() as conn:
        conn.execute(
            text(
                f"INSERT INTO UserAccount (id, user_name, password, email) VALUES "
                f"('{user_id}', 'testuser', 'testpw', 'testemail')"
            )
        )
    engine.dispose()

    writer = Writer(db_info['hostname'], db_info['port'], db_info['dbuser'], db_info['dbpassword'],
                    db_info['db'], user_id)
    id_parser = MzIdParser.MzIdParser(mzid_file, str(tmpdir), peaklist, writer, logger)
    # parse the mzid file
    id_parser.parse()


def test_db_cleared_each_test(use_database, engine):
    """Check that the database is empty."""
    with engine.connect() as conn:
        rs = conn.execute(text("SELECT * FROM Upload"))
        assert 0 == rs.rowcount
    engine.dispose()


def compare_modifications_dsso_mzid(results):
    assert results[0].id == 0  # id from incrementing count
    assert results[0].mod_name == 'Oxidation'  # name from <SearchModification> cvParam
    assert results[0].mass == 15.99491  # massDelta from <SearchModification>
    assert results[0].residues == 'M'  # residues from <SearchModification>
    assert results[0].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[0].fixed_mod  # fixedMod from <SearchModification>
    assert results[0].accession == 'UNIMOD:35'  # accession from <SearchModification> cvParam

    assert results[1].id == 1  # id from incrementing count
    assert results[1].mod_name == '(175.03)'  # unknown modification -> name from mass
    assert results[1].mass == 175.03032  # massDelta from <SearchModification>
    assert results[1].residues == 'K'  # residues from <SearchModification>
    assert results[1].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[1].fixed_mod  # fixedMod from <SearchModification>
    assert results[1].accession == 'MS:1001460'  # accession from <SearchModification> cvParam

    assert results[2].id == 2  # id from incrementing count
    assert results[2].mod_name == '(176.01)'  # unknown modification -> name from mass
    assert results[2].mass == 176.0143295  # massDelta from <SearchModification>
    assert results[2].residues == 'K'  # residues from <SearchModification>
    assert results[2].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[2].fixed_mod  # fixedMod from <SearchModification>
    assert results[2].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    
    assert results[3].id == 3  # id from incrementing count
    assert results[3].mod_name == '(175.03)'  # unknown modification -> name from mass
    assert results[3].mass == 175.03032  # massDelta from <SearchModification>
    assert results[3].residues == '.'  # residues from <SearchModification>
    assert results[3].specificity_rules == ['MS:1002057']  # parsed from child <SpecificityRules>
    assert not results[3].fixed_mod  # fixedMod from <SearchModification>
    assert results[3].accession == 'MS:1001460'  # accession from <SearchModification> cvParam

    assert results[4].id == 4  # id from incrementing count
    assert results[4].mod_name == '(176.01)'  # unknown modification -> name from mass
    assert results[4].mass == 176.0143295  # massDelta from <SearchModification>
    assert results[4].residues == '.'  # residues from <SearchModification>
    assert results[4].specificity_rules == ['MS:1002057']  # parsed from child <SpecificityRules>
    assert not results[4].fixed_mod  # fixedMod from <SearchModification>
    assert results[4].accession == 'MS:1001460'  # accession from <SearchModification> cvParam

    assert results[5].id == 5  # id from incrementing count
    assert results[5].mod_name == 'Deamidated'  # name from <SearchModification> cvParam
    assert results[5].mass == 0.984016  # massDelta from <SearchModification>
    assert results[5].residues == 'N Q'  # residues from <SearchModification>
    assert results[5].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[5].fixed_mod  # fixedMod from <SearchModification>
    assert results[5].accession == 'UNIMOD:7'  # accession from <SearchModification> cvParam
    
    assert results[6].id == 6  # id from incrementing count
    assert results[6].mod_name == 'Methyl'  # name from <SearchModification> cvParam
    assert results[6].mass == 14.01565  # massDelta from <SearchModification>
    assert results[6].residues == 'D E'  # residues from <SearchModification>
    assert results[6].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[6].fixed_mod  # fixedMod from <SearchModification>
    assert results[6].accession == 'UNIMOD:34'  # accession from <SearchModification> cvParam
    
    assert results[7].id == 7  # id from incrementing count
    assert results[7].mod_name == 'Carbamidomethyl'  # name from <SearchModification> cvParam
    assert results[7].mass == 57.021465  # massDelta from <SearchModification>
    assert results[7].residues == 'C'  # residues from <SearchModification>
    assert results[7].specificity_rules == []  # parsed from child <SpecificityRules>
    assert results[7].fixed_mod  # fixedMod from <SearchModification>
    assert results[7].accession == 'UNIMOD:4'  # accession from <SearchModification> cvParam


def test_mzid_parser_postgres_mgf(tmpdir, db_info, use_database, engine):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, db_info, use_database, engine)

    # test DBSequence (proteins)
    with engine.connect() as conn:

        # DBSequence
        rs = conn.execute(text("SELECT * FROM DBSequence;"))
        assert 12 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == "dbseq_P0C0V0_target"   # id from mzid
        assert results[0].accession == "P0C0V0"  # accession from mzid
        assert results[0].name == (  # name from mzid
            "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
            "OX=83333 GN=degP PE=1 SV=1")
        assert results[0].description == (  # protein description cvParam
            "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
            "OX=83333 GN=degP PE=1 SV=1"
        )
        assert results[0].sequence == (  # <Seq> value from mzid
            "MKKTTLALSALALSLGLALSPLSATAAETSSATTAQQMPSLAPMLEKVMPSVVSINVEGSTTVNTPRMPRNFQQFFGDDSPFCQEG"
            "SPFQSSPFCQGGQGGNGGGQQQKFMALGSGVIIDADKGYVVTNNHVVDNATVIKVQLSDGRKFDAKMVGKDPRSDIALIQIQNPKN"
            "LTAIKMADSDALRVGDYTVAIGNPFGLGETVTSGIVSALGRSGLNAENYENFIQTDAAINRGNSGGALVNLNGELIGINTAILAPD"
            "GGNIGIGFAIPSNMVKNLTSQMVEYGQVKRGELGIMGTELNSELAKAMKVDAQRGAFVSQVLPNSSAAKAGIKAGDVITSLNGKPI"
            "SSFAALRAQVGTMPVGSKLTLGLLRDGKQVNVNLELQQSSQNQVDSSSIFNGIEGAEMSNKGKDQGVVVNNVKTGTPAAQIGLKKG"
            "DVIIGANQQAVKNIAELRKVLDSKPSVLALNIQRGDSTIYLLMQ")
        # ToDo: check more rows?

        # Layout
        rs = conn.execute(text("SELECT * FROM Layout;"))
        assert 0 == rs.rowcount

        # Modification - parsed from <SearchModification>s
        rs = conn.execute(text("SELECT * FROM Modification;"))
        assert 8 == rs.rowcount
        compare_modifications_dsso_mzid(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        rs = conn.execute(text("SELECT * FROM Enzyme;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == "Trypsin_0"  # id from Enzyme element
        assert results[0].protocol_id == "SearchProtocol_1_0"
        assert results[0].c_term_gain == "OH"
        assert results[0].min_distance is None
        assert results[0].missed_cleavages == 2
        assert results[0].n_term_gain == "H"
        assert results[0].name == "Trypsin"
        assert results[0].semi_specific is False
        assert results[0].site_regexp == '(?<=[KR])(?\\!P)'
        assert results[0].accession == "MS:1001251"

        # PeptideEvidence
        rs = conn.execute(text("SELECT * FROM PeptideEvidence;"))
        assert 38 == rs.rowcount
        results = rs.fetchall()
        # peptide_ref from <PeptideEvidence>
        assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
        # dbsequence_ref from <PeptideEvidence>
        assert results[0].dbsequence_ref == 'dbseq_P0C0V0_target'
        assert results[0].pep_start == 148  # start from <PeptideEvidence>
        assert not results[0].is_decoy  # is_decoy from <PeptideEvidence>
        # ToDo: check more rows?

        # ModifiedPeptide
        rs = conn.execute(text("SELECT * FROM ModifiedPeptide;"))
        assert 38 == rs.rowcount
        results = rs.fetchall()
        # id from <Peptide> id
        assert results[0].id == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
        assert results[0].base_sequence == 'KFDAKMVGK'  # value of <PeptideSequence>
        assert results[0].modification_ids == []
        assert results[0].modification_positions == []
        # location of <Modification> with cross-link acceptor/receiver cvParam
        assert results[0].link_site == 5
        # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
        assert results[0].crosslinker_modmass == 0
        # value of cross-link acceptor/receiver cvParam
        assert results[0].crosslinker_pair_id == '1.0'

        # id from <Peptide> id
        assert results[1].id == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p0'
        assert results[1].base_sequence == 'KVLDSKPSVLALNIQR'  # value of <PeptideSequence>
        assert results[1].modification_ids == []
        assert results[1].modification_positions == []
        # location of <Modification> with cross-link acceptor/receiver cvParam
        assert results[1].link_site == 1
        # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
        assert results[1].crosslinker_modmass == 158.0037644600003
        # value of cross-link acceptor/receiver cvParam
        assert results[1].crosslinker_pair_id == '1.0'
        # ToDo: check more rows?

        # Spectrum
        rs = conn.execute(text("SELECT * FROM Spectrum;"))
        assert 22 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == 'index=3'  # spectrumID from <SpectrumIdentificationResult>
        # spectraData_ref from <SpectrumIdentificationResult>
        assert results[0].spectra_data_ref == \
               'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf'
        # assert results[0].scan_id == '3'  # ToDo: keep this?
        assert results[0].peak_list_file_name == (  # ToDo
            'recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf')
        assert results[0].precursor_mz == 945.6773592020113  # PEPMASS[0] from MGF
        assert results[0].precursor_charge == 5  # CHARGE from MGF
        assert results[0].mz == [
            104.05320445551794,
            108.14362094122345,
            108.49991368353048,
            110.07153867014885,
            111.07488808928888,
            111.55443374623124,
            115.08669886566057,
            116.0687164822676,
            116.07081458251673,
            117.07429370167216,
            118.94719582406489,
            119.03468973445412,
            121.81479566457033,
            121.87936327223723,
            127.0867460905739,
            129.10227972990302,
            130.0862733467447,
            138.0662089943007,
            138.09135549728666,
            139.09452941640586,
            141.0657363504715,
            143.1179063941509,
            144.1211871132828,
            147.1127646685096,
            148.11587758762155,
            153.10222157971157,
            155.07648021413962,
            155.0814546147303,
            155.11772471903708,
            155.77392899695627,
            156.08481163387123,
            157.13345675838977,
            159.0763585890944,
            164.081715083442,
            166.14978472900938,
            171.1127522183236,
            172.11606353745913,
            175.1190393940394,
            176.2216548249665,
            181.10834360522324,
            183.1126163432152,
            183.14922214756186,
            184.152319866672,
            185.09204777825744,
            185.1286382826023,
            187.08998801549748,
            187.10764241759384,
            195.0874254651317,
            195.49051701299572,
            196.06058538068694,
            201.10566047975084,
            202.10901749889177,
            207.91703208854884,
            209.10323522940132,
            210.10654654853684,
            211.14406807173455,
            212.14708939083562,
            213.0870767024519,
            215.10262564178282,
            215.138621146057,
            221.98684275923068,
            222.52624102328008,
            223.08265278934968,
            229.10041480391266,
            231.09718014101318,
            232.1403778648849,
            233.12829308219222,
            233.14327718397146,
            235.1188176185517,
            238.1185737747497,
            240.13410751407883,
            242.14965645340976,
            244.09272608413434,
            248.1137532616004,
            251.1499169221215,
            254.1490780782488,
            254.18618738265525,
            256.1289367133418,
            258.1269837505945,
            258.1446839526963,
            258.1518861535515,
            261.123535606412,
            266.12460440025046,
            266.1867381076284,
            268.1115430361842,
            268.16540664258,
            268.2020276469285,
            269.14907985938373,
            272.16024961693694,
            273.10785102945727,
            276.1552756913156,
            277.1586938104637,
            278.1242701251185,
            282.13806450172575,
            282.18127740685696,
            286.12198217478533,
            290.1709939555743,
            291.2694437860068,
            294.11935862441226,
            294.1810041317322,
            295.1839950508297,
            296.1242111624731,
            298.1328784009869,
            298.1759082060963,
            300.1553701411422,
            308.1170409865294,
            308.1600096916316,
            309.14432380851133,
            310.66092558859617,
            311.1624515481485,
            311.171332149203,
            311.1792972501488,
            312.1551578660248,
            312.19177897037326,
            313.1865300884923,
            314.17078310536476,
            315.17478112458184,
            320.1711501178622,
            323.14643117115395,
            325.1869588134509,
            326.12787682517774,
            326.1704794302364,
            327.1319053443984,
            328.12375726217317,
            329.12778568139385,
            337.1616001353475,
            344.14463316452895,
            348.20212874632534,
            349.1616930602663,
            351.1415211953556,
            351.2026174026104,
            352.14353551433715,
            353.21799844192134,
            356.1448786894658,
            360.19886477084555,
            368.19260962004125,
            369.1580333346779,
            369.17005723610566,
            369.2128124411825,
            370.17362795527197,
            370.2170239604249,
            374.1556840281105,
            375.15943784729853,
            376.1815937686717,
            376.6840352283328,
            380.1796105434055,
            383.1919400010964,
            387.1695405734059,
            388.1732027925831,
            389.1813816122966,
            391.1818091498319,
            392.185318768991,
            392.22859267412946,
            394.18367110628,
            397.16505566029645,
            397.2076887653588,
            398.16923677953525,
            399.22337500470604,
            401.2027759397447,
            406.1826349310647,
            409.20839209035006,
            415.2186772040252,
            419.23891088139703,
            424.70756993075827,
            425.2093400903396,
            425.7096757497506,
            426.191731506991,
            426.2713519164453,
            427.18199652457736,
            427.2188007289476,
            443.2135841282051,
            444.2156289471902,
            445.1928934632329,
            446.1962199823702,
            450.24535376317374,
            453.21852911621545,
            453.7202381757896,
            454.1869130312036,
            454.21981103510996,
            455.188530650138,
            457.75084785439344,
            460.19439054454534,
            461.28643177421685,
            462.2199950850703,
            465.81426431186213,
            466.2298221612064,
            466.2663822655477,
            474.18303970558986,
            475.78090979532465,
            484.2394373997098,
            490.2760897165158,
            494.73800434633387,
            495.2371804056072,
            497.22903244212426,
            498.2551555639685,
            499.23965278087,
            503.74239991553657,
            504.2437121750636,
            504.74322403437674,
            505.2427052936863,
            507.2128898276306,
            507.26745523410983,
            510.2923884932973,
            516.2661746026386,
            523.2631847334796,
            524.265626252512,
            525.2239393663042,
            526.2270521854161,
            526.2510390882644,
            527.222230603586,
            527.2538468073402,
            544.2611120268222,
            545.2626990457528,
            557.8078055353877,
            560.2827813292721,
            561.2875422485797,
            563.2675229836873,
            570.314032520406,
            571.3021918377425,
            573.2795480725383,
            578.2926711678081,
            579.293037586594,
            581.3286823283111,
            590.3056730942596,
            593.2900484486313,
            597.3064063255429,
            599.8053691222756,
            600.3068949818279,
            600.808115741344,
            602.2764997157034,
            602.30628491924,
            602.3360700227768,
            603.2875472357574,
            608.8108632916087,
            609.3123282511538,
            609.813304810641,
            610.3133048700121,
            611.3159294890661,
            611.3412590920739,
            612.8195307676073,
            620.2898075546451,
            620.3152591576672,
            621.2921269736629,
            621.3181279767502,
            622.3192877956303,
            626.8376598321522,
            634.3690328264448,
            638.3078150941449,
            639.3114162133148,
            640.3087308317383,
            641.288833448118,
            648.3606116878373,
            653.3511517804254,
            662.3566460497588,
            662.8578668092748,
            663.3590875687909,
            663.8581110280461,
            664.3449885858591,
            664.8460262453535,
            665.347613204913,
            666.3244199209013,
            666.8270444805842,
            667.3247252396799,
            673.2619818446834,
            674.2981757677235,
            678.3430370480197,
            678.8438306074851,
            679.345234467023,
            679.847920126713,
            691.3861294967867,
            697.8953465697061,
            698.3948583290193,
            703.3871685218177,
            704.880943099192,
            711.8912588316131,
            712.3295523836571,
            712.3922964911075,
            712.894860050783,
            713.8776482674815,
            714.3797235270991,
            714.8833245868979,
            718.3880858030614,
            719.3971801228836,
            722.8643436345825,
            723.3651981940551,
            723.3977298979181,
            723.8586674526508,
            727.8777109298813,
            728.3781382893033,
            729.3781994080529,
            733.1395523546845,
            740.401516116987,
            743.1315579411585,
            744.2989775797805,
            747.4093294491109,
            747.6583529786805,
            747.8488437012999,
            747.9115878087503,
            748.4144565684619,
            748.913174827681,
            749.4181187876392,
            750.3613561996412,
            751.3554359176807,
            751.3918128220001,
            752.3581826367491,
            752.3955971411918,
            753.35732825539,
            753.39480385984,
            759.3868089713445,
            763.3952322473139,
            763.8968192068735,
            764.3979178663751,
            766.4037775045556,
            766.8985285633034,
            767.4054256234936,
            767.905486682872,
            775.4029851731423,
            775.9044500326874,
            776.4081732925006,
            776.9122016523501,
            778.3736886258904,
            779.3818064455967,
            786.3999956789527,
            786.8959064378382,
            789.95456160103,
            791.3884606712945,
            791.8900476308542,
            792.3915735904064,
            792.8924281498792,
            796.3804046640495,
            796.8805267234352,
            799.1620821943523,
            799.4105563238568,
            802.8827247361501,
            803.1592750689882,
            803.4077491984926,
            803.9110451582551,
            803.9511452630167,
            804.4131204178727,
            804.4524881225474,
            804.9543802821432,
            812.3652697621294,
            812.4297839697899,
            812.8710071221817,
            812.931004729306,
            819.8994503567553,
            819.938329761372,
            820.4001828162134,
            820.4393064208591,
            820.939001280194,
            821.1684935074445,
            821.4178831370575,
            821.9187376965301,
            822.4296020571915,
            823.4327759763106,
            824.4316164949153,
            828.4170295681524,
            831.4316173261114,
            834.3652723744605,
            835.4168471993269,
            840.8883444490251,
            842.4352807327119,
            848.4086090419987,
            849.1890046346647,
            849.4099519609005,
            849.6894319940866,
            849.9392488237504,
            850.4129427799979,
            851.4141635988852,
            852.4598790230558,
            852.961099782572,
            854.4559730600768,
            854.9574379196218,
            855.4534706785219,
            856.4335122948943,
            859.4137983487802,
            860.4250899688635,
            860.9302169288434,
            861.4660446924688,
            861.9663499518762,
            862.4195360056887,
            862.467509611385,
            862.9710497711766,
            864.4121509422963,
            868.4420587208168,
            869.4331476385009,
            869.9346125980461,
            870.4356502575405,
            870.937481317129,
            871.4389462766742,
            873.4479797152314,
            874.4470032338578,
            876.4062319665012,
            876.9044620256622,
            876.9490787309601,
            877.4103824857362,
            877.4516422906356,
            877.9508488499125,
            878.1958439790038,
            878.4493231091026,
            878.6971868385344,
            878.9517645687636,
            879.1952337976737,
            879.4520087281637,
            879.5201850362591,
            880.4526802469858,
            880.5247017555378,
            883.9206982587862,
            883.9653149640841,
            884.9131299766299,
            885.4191725367185,
            885.9205763962564,
            886.4212478557073,
            886.9214920151074,
            887.4213089744569,
            887.9239946341469,
            888.4035478910902,
            891.3864583452879,
            891.4560384535499,
            892.4258872687121,
            892.9304649286267,
            893.4305870880124,
            893.9278405470574,
            894.0616906629512,
            894.4235681059213,
            896.4564663473124,
            902.2075046302039,
            902.7078097896112,
            903.454330878255,
            904.4763646996137,
            904.7208716286468,
            905.4299781128478,
            906.4324196318801,
            907.4331521507094,
            908.064988225735,
            908.2668925497096,
            908.474412074351,
            908.6688090974341,
            908.8691265212203,
            909.2234355632917,
            909.9896100542691,
            910.4936384141185,
            910.9959577737652,
            911.489976432426,
            911.6542830519362,
            912.0568709997405,
            912.4830795503493,
            912.8603988951531,
            912.9255234028863,
            914.4957750893415,
            916.4377309199339,
            917.4393789388718,
            919.4759392806977,
            919.6722283040056,
            921.8470332622469,
            922.2468136097177,
            923.4780149559134,
            923.7274045855265,
            923.8126706956511,
            923.9848509160963,
            925.8660157394701,
            925.9775879527185,
            926.4801515123941,
            926.9790529716348,
            927.2269167010667,
            927.4810671312451,
            928.2823368263896,
            930.4807012874286,
            930.7298468170127,
            930.9806403467925,
            931.0837897590408,
            931.2309455765143,
            931.4838142065405,
            931.7304573358275,
            933.8785898909017,
            934.0627940127745,
            934.278492238387,
            934.4660533606585,
            934.663502084104,
            934.8673595083105,
            935.0688366322344,
            936.4730115989693,
            937.0692640697697,
            937.2623793927007,
            937.4791152184364,
            937.6747939416717,
            937.8679092646028,
            939.4825334563269,
            940.2715349500148,
            940.874135121569,
            941.8912251423405,
            942.0748188641409,
            942.2772724881808,
            942.4775289119596,
            942.6772970356806,
            942.8772481594232,
            943.0798848834847,
            943.2742209065607,
            943.4786887308396,
            943.6810812548723,
            945.4775902681938,
            945.6790673921178,
            945.8791406158748,
            946.0792139396319,
            946.27971446344,
            946.4803369872624,
            946.6811427111064,
            946.8328761291236,
            946.8820094349578,
            947.0799464584613,
            948.410024716398,
            949.4136259355678,
            950.4166167546653,
            950.556631471291,
            951.2367462520493,
            951.4902862821554,
            951.5496124891998,
            951.741568111993,
            951.9919343417221,
            952.2435822716034,
            952.4889437007382,
            952.5358187063042,
            953.0366732657768,
            955.7415074869551,
            955.9919348166914,
            956.2410193462682,
            956.493033476193,
            956.7455970061831,
            960.1717449130117,
            962.2371137582584,
            962.7354659174338,
            965.4924852448087,
            965.7451097748059,
            965.9958422045785,
            966.1601489240887,
            966.2447436341336,
            966.4852221626885,
            966.5382617689867,
            967.0363697281332,
            967.5404590879899,
            967.9952321419906,
            968.0435719477306,
            968.1748586633199,
            968.5197073042681,
            969.0222097639364,
            969.5071952215247,
            969.9940726793376,
            970.2468193093493,
            970.4982841392089,
            970.7470634687495,
            970.9978569985293,
            971.2479791282294,
            971.4993218580744,
            973.8433163364057,
            974.1780331761507,
            974.5104917156276,
            974.8451474553655,
            975.1752866945669,
            975.514947334899,
            975.8467955743034,
            976.1788268137296,
            979.8476505493743,
            980.1822452891047,
            980.5167180288208,
            980.5772648360104,
            980.8500920684064,
            981.1845647081225,
            981.5176946476791,
            982.5228217670303,
            983.0227607263942,
            983.5270332862726,
            984.4982248015942,
            985.1688791812292,
            985.4981028203221,
            985.8370311605671,
            986.1697948000802,
            986.4968822389193,
            987.4735669548932,
            988.4754591738601,
            990.5062822150048,
            990.8396562545903,
            991.1737016942557,
            991.5078081339283,
            991.8422808736443,
            992.1758380132517,
            994.2545736600856,
            994.5039632896986,
            994.760799320196,
            997.5123865469258,
            1001.4885829190686,
            1004.5416232815936,
            1005.5428444004809,
            1006.4774755114612,
            1007.4800386305078,
            1008.0526096984963,
            1008.2726417246233,
            1008.4812597493951,
            1008.552243757824,
            1008.7711157838132,
            1009.050717817014,
            1009.4807108680723,
            1011.0346660525925,
            1011.5377791123333,
            1017.0569447676918,
            1017.5587758272804,
            1018.0582878865936,
            1018.561094946298,
            1019.4465930514441,
            1020.0194691194688,
            1020.4490351704763,
            1020.5094591776513,
            1020.769347208511,
            1021.4502552893637,
            1023.5526115390023,
            1023.7615965638176,
            1024.0378415966197,
            1024.5383296560487,
            1025.0418697158404,
            1025.54101577511,
            1027.0178219504694,
            1027.2707519805028,
            1027.521118010232,
            1027.7713620399466,
            1028.0231930698496,
            1028.2700190991582,
            1033.0433356659528,
            1033.5441897254254,
            1034.0466317850864,
            1036.5634770839424,
            1037.0632331432848,
            1037.5651862028878,
            1038.554566320369,
            1045.5681171531742,
            1046.0719012129948,
            1046.5739772726126,
            1047.073366331911,
            1052.5471219818774,
            1053.0515170417705,
            1053.5539581014314,
            1054.0504181603824,
            1061.5537150513412,
            1062.0550581108719,
            1062.552372169924,
            1063.0600632302085,
            1071.2106981980337,
            1071.5488332381847,
            1083.3107976348274,
            1083.5604316644694,
            1094.092292915047,
            1097.5682453277898,
            1100.5588466829006,
            1101.5636078022083,
            1102.5638519209795,
            1114.0583602858642,
            1118.5777698225093,
            1119.564341939657,
            1120.5666610586748,
            1121.5619011768517,
            1124.3195915043063,
            1124.8144645630687,
            1126.2404897323981,
            1126.918468812903,
            1131.921521406977,
            1132.2508664460843,
            1132.5279664789878,
            1133.5330935983388,
            1134.531262716864,
            1134.8974737603487,
            1141.6029185565685,
            1142.6015756751513,
            1146.6222061525702,
            1150.5471336186251,
            1151.551894737933,
            1158.6295325783478,
            1159.6161046954958,
            1160.1169587549684,
            1160.6191568146005,
            1161.610366932299,
            1162.1218419930328,
            1164.5821692851778,
            1164.9222573255608,
            1170.256852959003,
            1170.589371998487,
            1170.924822038319,
            1171.2599050781075,
            1171.5938891177657,
            1171.9262861572352,
            1175.6017025936626,
            1176.0979176525846,
            1176.6009697123181,
            1177.1009697716893,
            1178.6682309577893,
            1179.6715270769232,
            1182.599505424598,
            1197.6441852110381,
            1198.1438192703658,
            1198.6040243250116,
            1198.6535843308964,
            1199.5995074432176,
            1205.1156220982139,
            1210.6400367541955,
            1211.6410128730538,
            1213.639915110408,
            1214.130027168605,
            1214.642600229469,
            1215.6427223482258,
            1216.6142804635908,
            1217.6180645827826,
            1218.6191637016555,
            1219.6201398205137,
            1232.3006833262307,
            1234.3000735636429,
            1234.9706056432633,
            1235.3025146826749,
            1235.6430907231158,
            1235.9668217615563,
            1240.3021492763432,
            1240.638086316233,
            1240.9723153559203,
            1241.3061773955637,
            1241.641382435367,
            1245.6141619071038,
            1246.6153820259913,
            1248.671901270187,
            1249.1694603292683,
            1264.6535921678899,
            1265.1527382271595,
            1267.9803755629198,
            1268.3197306032157,
            1268.6491986423373,
            1268.9861126823432,
            1269.3122847210739,
            1273.9831832757072,
            1274.3187553155537,
            1274.653105355255,
            1274.9878223950004,
            1275.3236374348758,
            1280.7210990757828,
            1284.6787415457225,
            1285.6849666652038,
            1286.9836738194153,
            1287.3226628596676,
            1287.6556708992098,
            1287.9862369384618,
            1288.330596979352,
            1288.6654360191117,
            1292.9940495331011,
            1293.3292555729042,
            1293.6629956125335,
            1293.9962476521046,
            1294.3285226915598,
            1311.6902187531275,
            1313.1872899308933,
            1316.649448341998,
            1323.7046251797458,
            1324.7108502992276,
            1329.6719108883153,
            1331.6407831221036,
            1332.6450552413532,
            1333.6468873603133,
            1341.7034063169629,
            1342.7038944357632,
            1343.7048715546214,
            1355.6741109758766,
            1356.6789940951987,
            1369.6882726399506,
            1373.6726481130645,
            1374.677165232343,
            1375.6754563508825,
            1379.6471368224888,
            1384.2172053651498,
            1384.7170834245062,
            1412.7383267518135,
            1413.742110871005,
            1414.7413789896605,
            1422.7766579437882,
            1423.7728740620812,
            1444.7197755493644,
            1445.7212406682809,
            1446.7227057871971,
            1454.7463887399479,
            1455.749318859038,
            1462.7091576854655,
            1463.7118438045266,
            1464.719045924124,
            1493.8115783786386,
            1494.6836494821903,
            1494.8168274980042,
            1495.6829166008458,
            1496.6891427203273,
            1497.760797847578,
            1514.4364588276846,
            1515.75835898465,
            1516.7697111047403,
            1517.7677582232507,
            1551.813905265969,
            1553.8350235059613,
            1583.7788750615634,
            1584.7926681819436,
            1606.8977738067547,
            1607.9027789260913,
            1614.8299037486343,
            1638.8655506026826,
            1703.8903393238763,
            1721.9231784651372,
            1722.9270845843432,
            1723.9352637040568,
            1724.9309908222917,
            1737.860680357593,
            1738.8605584763206,
            1753.896448261717,
            1754.8993783808073,
            1755.9067025004194,
            1756.9036506187992,
            1769.8302881537381,
            1770.8341942729444,
            1771.833828391643,
            1933.0677345369297,
            2015.0988722774966,
            2692.6348407296828,
            2903.29502274396,
            3909.40354021161,
            3922.8735128110657,
        ]
        assert results[0].intensity == [
            28995.111328125,
            4046.4367675781,
            4084.0302734375,
            173970.671875,
            5553.9169921875,
            4357.5883789063,
            7220.5678710938,
            7682.7495117188,
            90175.953125,
            5991.0668945313,
            3461.8889160156,
            3706.0383300781,
            3461.0654296875,
            3944.0356445313,
            39129.59765625,
            39143.16015625,
            24263.212890625,
            14769.966796875,
            64052.90625,
            6395.0952148438,
            4310.734375,
            66334.796875,
            4317.6274414063,
            35644.30078125,
            4734.8911132813,
            46672.76171875,
            5281.931640625,
            80358.4140625,
            4774.1650390625,
            3659.1892089844,
            8167.9560546875,
            7077.6103515625,
            9838.1298828125,
            5982.2631835938,
            3856.3542480469,
            74685.8203125,
            5730.2075195313,
            29340.779296875,
            3867.7229003906,
            12396.775390625,
            4359.390625,
            93355.578125,
            5271.830078125,
            6094.900390625,
            3802.8884277344,
            15433.1201171875,
            6982.4516601563,
            9998.6103515625,
            3759.8737792969,
            7263.83203125,
            90704.890625,
            7250.9814453125,
            4906.8452148438,
            39570.96484375,
            4021.5661621094,
            72669.6015625,
            9971.8369140625,
            13114.513671875,
            23643.33203125,
            6315.740234375,
            4267.0947265625,
            3554.6635742188,
            5103.0756835938,
            63033.7265625,
            11243.9462890625,
            56327.03125,
            12588.5166015625,
            6721.392578125,
            17123.044921875,
            6545.9916992188,
            19414.05859375,
            4370.2294921875,
            3765.1401367188,
            3461.6784667969,
            6026.3833007813,
            4523.07421875,
            7491.6767578125,
            32860.83203125,
            16916.8203125,
            93221.1484375,
            7302.5830078125,
            9183.90234375,
            19442.3828125,
            4557.7021484375,
            5682.6611328125,
            7881.119140625,
            4731.5576171875,
            5598.1743164063,
            13769.13671875,
            25501.21875,
            179895.84375,
            21604.333984375,
            9693.16015625,
            6522.9541015625,
            4028.0368652344,
            23502.298828125,
            11359.6298828125,
            3581.1611328125,
            16345.671875,
            38680.92578125,
            4544.9384765625,
            4339.0385742188,
            10759.658203125,
            5521.8046875,
            10809.1181640625,
            32498.265625,
            6614.7353515625,
            5481.578125,
            153068.578125,
            41168.7890625,
            17964.419921875,
            3966.7414550781,
            8199.48828125,
            49813.22265625,
            11399.4306640625,
            54652.234375,
            8668.3173828125,
            5502.0927734375,
            5684.9614257813,
            4735.4135742188,
            249343.03125,
            20671.205078125,
            35785.421875,
            8069.1635742188,
            3885.212890625,
            17756.99609375,
            20435.830078125,
            6650.8725585938,
            7486.68359375,
            5237.3872070313,
            12020.7548828125,
            13230.6796875,
            5584.943359375,
            15504.0380859375,
            38283.609375,
            5286.6147460938,
            7210.7426757813,
            47399.62890625,
            46696.89453125,
            6863.8432617188,
            9078.8984375,
            18293.0234375,
            3898.9663085938,
            19502.923828125,
            5653.5688476563,
            4322.8706054688,
            8603.921875,
            11051.166015625,
            3995.3630371094,
            13644.1689453125,
            44766.9609375,
            5946.0629882813,
            4318.5317382813,
            11809.375,
            167253.53125,
            9482.33984375,
            26927.03515625,
            10374.4765625,
            10461.5390625,
            4220.2797851563,
            11268.845703125,
            13560.7763671875,
            5998.2934570313,
            287684.03125,
            98117.4921875,
            16989.2265625,
            7346.7211914063,
            5305.8447265625,
            9206.4169921875,
            13891.08984375,
            34166.89453125,
            4476.9711914063,
            13015.3291015625,
            5666.087890625,
            20668.041015625,
            156409.40625,
            52307.50390625,
            47682.91015625,
            18452.6796875,
            5674.359375,
            7470.42578125,
            7125.0795898438,
            6444.685546875,
            33441.5859375,
            4344.296875,
            9367.47265625,
            14262.7158203125,
            4290.9775390625,
            4047.1862792969,
            8386.443359375,
            3933.1357421875,
            9696.7294921875,
            4218.7763671875,
            25691.955078125,
            6921.9057617188,
            9624.841796875,
            126754.59375,
            47843.2265625,
            7741.8461914063,
            9911.7470703125,
            10360.3349609375,
            15425.7138671875,
            4681.5048828125,
            11575.2900390625,
            28670.806640625,
            5372.9702148438,
            161768.890625,
            32630.990234375,
            35305.5859375,
            4526.150390625,
            4097.2290039063,
            26216.26953125,
            6578.98046875,
            5179.3110351563,
            9102.2109375,
            4914.4609375,
            16006.0556640625,
            3998.3127441406,
            4590.4775390625,
            4171.921875,
            5428.6635742188,
            5801.5961914063,
            7565.5014648438,
            7996.5180664063,
            6894.0170898438,
            11292.8974609375,
            61682.58984375,
            30752.521484375,
            11345.3388671875,
            4077.2802734375,
            4305.5537109375,
            4270.98828125,
            14337.4599609375,
            278675.0625,
            143683.921875,
            49234.64453125,
            40022.921875,
            10483.8115234375,
            6215.1962890625,
            4995.6123046875,
            54776.7734375,
            590503.9375,
            11337.66796875,
            162690.09375,
            24194.5078125,
            4842.689453125,
            8612.0791015625,
            159483.1875,
            48646.0390625,
            4245.9907226563,
            4483.8427734375,
            6269.3525390625,
            5002.0009765625,
            61145.3828125,
            50188.59375,
            12968.423828125,
            6578.6596679688,
            13239.16015625,
            8409.6328125,
            4544.0424804688,
            24642.248046875,
            7676.9731445313,
            3981.7631835938,
            5039.3784179688,
            3760.7641601563,
            47212.9765625,
            28455.0703125,
            7992.474609375,
            5211.421875,
            4260.1064453125,
            18788.15625,
            4299.9487304688,
            4437.2758789063,
            5334.5541992188,
            75283.1875,
            7668.8090820313,
            50417.84375,
            4665.4458007813,
            10300.9423828125,
            8367.7119140625,
            5231.919921875,
            12953.59375,
            6314.5473632813,
            5098.212890625,
            6902.6127929688,
            13062.625,
            4054.3933105469,
            40931.5,
            30615.91015625,
            5486.2290039063,
            4505.80859375,
            4208.1201171875,
            5026.5004882813,
            6634.6625976563,
            98471.546875,
            4799.55859375,
            5087.0541992188,
            74107.1796875,
            22894.9140625,
            7547.5546875,
            5654.0815429688,
            9894.490234375,
            54759.81640625,
            116273.046875,
            19208.087890625,
            33937.28125,
            7770.76953125,
            10951.86328125,
            4733.7138671875,
            62893.28515625,
            57036.84375,
            18471.8515625,
            4001.2380371094,
            5344.9931640625,
            5383.4096679688,
            5924.4858398438,
            64079.75390625,
            33693.56640625,
            23972.583984375,
            5564.4331054688,
            18353.513671875,
            5264.54296875,
            6348.0576171875,
            5528.3842773438,
            6464.04296875,
            66076.1953125,
            57195.484375,
            35228.140625,
            11661.7353515625,
            7977.8950195313,
            5526.5083007813,
            4396.3530273438,
            4965.375,
            6227.744140625,
            9184.162109375,
            12008.287109375,
            14794.5830078125,
            46281.98828125,
            11139.6708984375,
            46088.60546875,
            21626.6875,
            6799.41796875,
            13213.34765625,
            7012.4038085938,
            8544.826171875,
            4357.1826171875,
            36829.6015625,
            5989.8701171875,
            27793.849609375,
            12786.4765625,
            14028.5,
            14841.84375,
            8611.404296875,
            89504.546875,
            32740.435546875,
            7927.4682617188,
            5993.6743164063,
            9204.88671875,
            5291.4482421875,
            4589.6508789063,
            5223.4697265625,
            4651.4057617188,
            415165.375,
            7133.3881835938,
            156335.328125,
            9186.798828125,
            8504.23828125,
            36892.2265625,
            6284.1059570313,
            11993.765625,
            11076.953125,
            15147.080078125,
            10944.4697265625,
            5875.7553710938,
            7855.3583984375,
            13479.2919921875,
            33153.7109375,
            27996.58203125,
            207273.8125,
            212853.078125,
            7644.3266601563,
            92740.40625,
            32628.189453125,
            3982.037109375,
            6780.306640625,
            820074.25,
            615291.5,
            290883.96875,
            91825.09375,
            26112.53515625,
            5066.9111328125,
            4681.75,
            36055.40625,
            43987.22265625,
            9135.8583984375,
            17270.845703125,
            151819.15625,
            138301.109375,
            105682.5703125,
            125297.6796875,
            60219.640625,
            35584.7109375,
            8575.2861328125,
            25513.71484375,
            7736.3901367188,
            9704.53515625,
            5303.8120117188,
            5838.279296875,
            6920.8159179688,
            6447.87109375,
            975628.25,
            821125.0,
            420837.8125,
            173369.546875,
            44611.36328125,
            7838.1020507813,
            5750.3178710938,
            6515.0258789063,
            26324.712890625,
            24775.01171875,
            22605.08984375,
            20870.771484375,
            7872.7041015625,
            4776.1997070313,
            5430.0424804688,
            7321.0546875,
            12455.603515625,
            17913.9296875,
            5320.7573242188,
            5061.0239257813,
            6330.40234375,
            413839.875,
            164611.25,
            55485.22265625,
            7492.9633789063,
            25819.267578125,
            18217.626953125,
            22118.580078125,
            7169.87890625,
            10577.427734375,
            23436.1953125,
            29144.693359375,
            9189.05859375,
            9186.9169921875,
            4352.7197265625,
            11041.6142578125,
            5918.3452148438,
            4178.3759765625,
            4238.7124023438,
            8511.302734375,
            52596.453125,
            21442.9375,
            7688.447265625,
            7479.5239257813,
            6397.8002929688,
            15146.177734375,
            11077.0146484375,
            8564.0966796875,
            5452.3022460938,
            13241.771484375,
            7429.908203125,
            27109.16015625,
            24493.80859375,
            7790.9165039063,
            6040.3413085938,
            7851.7026367188,
            5434.1474609375,
            45578.24609375,
            100231.90625,
            69486.6484375,
            8687.478515625,
            55633.7734375,
            26108.068359375,
            9466.03515625,
            6166.9057617188,
            6924.5341796875,
            9685.908203125,
            22108.904296875,
            14145.330078125,
            15279.0654296875,
            8706.4296875,
            15517.056640625,
            16991.96875,
            9120.22265625,
            28997.1875,
            9321.5126953125,
            6466.279296875,
            8022.8413085938,
            6571.9877929688,
            6744.3149414063,
            9034.51171875,
            33988.41796875,
            83250.953125,
            105568.3125,
            85938.859375,
            72087.75,
            53534.953125,
            33293.765625,
            19140.615234375,
            11764.1162109375,
            12933.486328125,
            636605.0625,
            1475346.625,
            1917647.75,
            1802097.125,
            1128948.0,
            590185.875,
            6860.3388671875,
            91781.8984375,
            10836.6396484375,
            59769.66796875,
            29255.330078125,
            5852.00390625,
            7426.3251953125,
            13954.8115234375,
            20518.5,
            4737.7451171875,
            24420.896484375,
            12720.9140625,
            11282.6611328125,
            9646.099609375,
            9290.962890625,
            9201.296875,
            51309.5703125,
            76484.2265625,
            73961.6484375,
            49353.6328125,
            32383.5078125,
            6732.4995117188,
            6104.7524414063,
            7207.2939453125,
            13764.1484375,
            35824.59375,
            39094.37890625,
            5732.2622070313,
            56143.0078125,
            7345.8198242188,
            46078.08203125,
            45727.26171875,
            31613.404296875,
            9081.1103515625,
            9054.7744140625,
            6123.5991210938,
            12330.0703125,
            11244.06640625,
            7458.1625976563,
            50356.015625,
            120173.4921875,
            134593.34375,
            86904.7109375,
            48740.48046875,
            26501.412109375,
            7622.9052734375,
            28592.21484375,
            37899.87890625,
            30565.87109375,
            22064.677734375,
            14046.37890625,
            19185.689453125,
            12152.119140625,
            6012.4291992188,
            283162.96875,
            394333.1875,
            300220.21875,
            7010.8583984375,
            184724.65625,
            40722.375,
            18292.8046875,
            36423.71875,
            22981.59375,
            14125.7919921875,
            7122.8247070313,
            13185.83203125,
            11255.974609375,
            11560.0888671875,
            13090.357421875,
            9189.4296875,
            63477.22265625,
            47548.58984375,
            170132.1875,
            225996.953125,
            189584.6875,
            98059.65625,
            37645.93359375,
            13057.8740234375,
            14120.0419921875,
            6670.0063476563,
            7069.6831054688,
            6068.154296875,
            8922.53515625,
            52828.6640625,
            25440.720703125,
            365110.21875,
            164334.4375,
            32618.330078125,
            5335.4682617188,
            49377.015625,
            31541.041015625,
            5756.9252929688,
            18143.642578125,
            10544.6845703125,
            11514.8427734375,
            6305.3403320313,
            57529.171875,
            50760.7109375,
            20279.0390625,
            11114.21484375,
            74979.9375,
            10854.9306640625,
            28372.466796875,
            7970.0126953125,
            8466.576171875,
            8460.5341796875,
            5393.4819335938,
            5944.6752929688,
            16704.8203125,
            16839.296875,
            12995.66796875,
            6503.9497070313,
            36828.140625,
            93314.7578125,
            98654.9609375,
            97147.484375,
            35147.3984375,
            18174.8984375,
            40619.90625,
            27415.71875,
            17460.6796875,
            28605.5234375,
            28826.453125,
            14171.55078125,
            5517.1870117188,
            48201.28515625,
            55882.22265625,
            18237.8203125,
            11629.6943359375,
            24329.2578125,
            15506.4423828125,
            16112.9130859375,
            8996.1640625,
            28691.2109375,
            34069.37109375,
            9565.25390625,
            7379.8530273438,
            6113.16015625,
            7832.861328125,
            5341.6357421875,
            14152.203125,
            6298.41015625,
            5796.9262695313,
            74046.8125,
            21506.771484375,
            9195.1083984375,
            7539.8666992188,
            15147.4912109375,
            33286.0078125,
            25284.02734375,
            8353.7880859375,
            6965.0991210938,
            6791.6328125,
            5473.1274414063,
            5963.5673828125,
            9109.8271484375,
            11519.9931640625,
            66589.5234375,
            27606.47265625,
            11298.1669921875,
            4976.1127929688,
            22042.27734375,
            14697.3291015625,
            5577.2631835938,
            18375.359375,
            5358.8198242188,
            8429.8564453125,
            34859.26953125,
            32363.744140625,
            20371.255859375,
            6013.9331054688,
            5140.3974609375,
            11769.1181640625,
            19630.576171875,
            30194.03125,
            60928.5703125,
            66496.984375,
            40469.1484375,
            22310.3515625,
            8337.8173828125,
            24057.978515625,
            23165.47265625,
            17293.951171875,
            6048.806640625,
            25783.609375,
            12891.9501953125,
            7809.2373046875,
            19576.10546875,
            30743.451171875,
            13431.7548828125,
            5459.6533203125,
            13859.525390625,
            7269.3432617188,
            12898.197265625,
            10645.3232421875,
            47673.8203125,
            25126.595703125,
            23582.712890625,
            5332.7250976563,
            340018.6875,
            182913.921875,
            69856.21875,
            15554.9921875,
            5947.451171875,
            6097.2275390625,
            19228.5234375,
            12229.5625,
            6107.052734375,
            6124.091796875,
            12149.8359375,
            34432.86328125,
            53498.45703125,
            28992.830078125,
            18051.509765625,
            35711.375,
            20270.728515625,
            9848.57421875,
            6808.1455078125,
            7154.1450195313,
            7640.9174804688,
            10395.611328125,
            11899.6318359375,
            24273.14453125,
            11557.6748046875,
            8982.025390625,
            17269.923828125,
            31338.09765625,
            45075.15625,
            25621.232421875,
            7475.3603515625,
            7318.908203125,
            11336.8330078125,
            5522.6899414063,
            6860.7651367188,
            15042.3232421875,
            20268.943359375,
            6239.4604492188,
            7611.677734375,
            7628.6899414063,
            38102.5390625,
            56275.8125,
            42397.2578125,
            29017.53125,
            9139.8134765625,
            8573.1474609375,
            12405.4580078125,
            14474.0625,
            16430.55078125,
            9809.4697265625,
            6899.9111328125,
            81708.3203125,
            50395.2265625,
            21190.623046875,
            39095.75,
            33682.859375,
            9593.7685546875,
            14054.4619140625,
            7588.111328125,
            11841.6806640625,
            56683.6484375,
            30729.419921875,
            10665.91796875,
            6406.66015625,
            7880.2646484375,
            6656.3095703125,
            22877.41796875,
            20765.560546875,
            8529.8095703125,
            18264.802734375,
            11133.9755859375,
            44287.42578125,
            30563.341796875,
            17956.205078125,
            10906.693359375,
            6869.1069335938,
            19637.91015625,
            12305.7314453125,
            7438.5961914063,
            13929.1630859375,
            16305.53515625,
            8530.7236328125,
            20125.21875,
            7796.9638671875,
            6158.7421875,
            5308.2856445313,
            29983.13671875,
            18867.5390625,
            11896.1943359375,
            5261.9223632813,
            6051.2568359375,
            7565.890625,
            5612.8388671875,
            9538.3330078125,
            6548.306640625,
            10029.814453125,
            14926.3251953125,
            5131.609375,
            65330.703125,
            40799.7109375,
            22127.521484375,
            7578.8647460938,
            29273.59375,
            23477.125,
            38658.11328125,
            45349.1171875,
            21330.4765625,
            8439.7666015625,
            15392.1669921875,
            18456.44921875,
            9000.85546875,
            7089.44921875,
            5358.0415039063,
            4858.9428710938,
            4915.0346679688,
            5437.94140625,
            4767.9130859375,
        ]
        # ToDo: check more rows? could loop over spectra in MGF and compare to DB

        # SpectrumIdentification
        rs = conn.execute(text("SELECT * FROM SpectrumIdentification;"))
        assert 22 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == 'SII_3_1'  # id from first <SpectrumIdentificationItem>
        assert results[0].spectrum_id == 'index=3'  # spectrumID from <SpectrumIdentificationResult>
        # spectraData_ref from <SpectrumIdentificationResult>
        assert results[0].spectra_data_ref == \
               'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf'
        # peptide_ref from <SpectrumIdentificationItem>
        assert results[0].pep1_id == \
               '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p1'
        # peptide_ref from matched <SpectrumIdentificationItem> by crosslink_identification_id
        assert results[0].pep2_id == \
               '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p0'
        assert results[0].charge_state == 5  # chargeState from <SpectrumIdentificationItem>
        assert results[0].pass_threshold  # passThreshold from <SpectrumIdentificationItem>
        assert results[0].rank == 1  # rank from <SpectrumIdentificationItem>
        # scores parsed from score related cvParams in <SpectrumIdentificationItem>
        assert results[0].scores == '{"xi:score": 33.814201}'
        # experimentalMassToCharge from <SpectrumIdentificationItem>
        assert results[0].exp_mz == 945.677359
        # calculatedMassToCharge from <SpectrumIdentificationItem>
        assert results[0].calc_mz == 945.6784858667701
        # Meta columns are only parsed from csv docs
        assert results[0].meta1 == ''
        assert results[0].meta2 == ''
        assert results[0].meta3 == ''

        # SpectrumIdentificationProtocol
        rs = conn.execute(text("SELECT * FROM SpectrumIdentificationProtocol;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()
        # parsed from <FragmentTolerance> in <SpectrumIdentificationProtocol>
        assert results[0].id == 'SearchProtocol_1_0'  # id from <SpectrumIdentificationProtocol>
        assert results[0].frag_tol == '5.0 ppm'
        # cvParams from <AdditionalSearchParams> 'ion series considered in search' (MS:1002473)
        assert results[0].ions == ['MS:1001118', 'MS:1001262']
        assert results[0].analysis_software == (  # referenced <AnalysisSoftware> json
            '{"version": "2.1.5.2", "id": "xiFDR_id", "name": "XiFDR", "SoftwareName": '
            '{"xiFDR": ""}}')

        # Upload
        rs = conn.execute(text("SELECT * FROM Upload;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()

        assert results[0].identification_file_name == 'mgf_ecoli_dsso.mzid'
        assert results[0].provider == (
            '{"id": "PROVIDER", "ContactRole": ['
            '{"contact_ref": "PERSON_DOC_OWNER", "Role": "researcher"}]}')
        assert results[0].audits == (
            '{"Person": {"lastName": "Kolbowski", "firstName": "Lars", "id": "PERSON_DOC_OWNER", '
            '"Affiliation": [{"organization_ref": "ORG_DOC_OWNER"}], '
            '"contact address": "TIB 4/4-3 Geb\\u00e4ude 17, Aufgang 1, Raum 476 '
            'Gustav-Meyer-Allee 25 13355 Berlin", '
            '"contact email": "lars.kolbowski@tu-berlin.de"}, '
            '"Organization": {"id": "ORG_DOC_OWNER", "name": "TU Berlin", '
            '"contact name": "TU Berlin"}}'
        )
        assert results[0].samples == '{}'
        assert results[0].bib == '[]'
        assert results[0].spectra_formats == (
            '[{"location": "recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf", '
            '"id": "SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf", '
            '"FileFormat": "Mascot MGF format", '
            '"SpectrumIDFormat": "multiple peak list nativeID format"}, '
            '{"location": "recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf", '
            '"id": "SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf", '
            '"FileFormat": "Mascot MGF format", '
            '"SpectrumIDFormat": "multiple peak list nativeID format"}]')
        assert results[0].contains_crosslinks
        assert results[0].upload_error is None
        assert results[0].error_type is None
        assert results[0].upload_warnings == []
        assert not results[0].deleted

    engine.dispose()


def test_mzid_parser_postgres_mzml(tmpdir, db_info, use_database, engine):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, db_info, use_database, engine)

    # test DBSequence (proteins)
    with engine.connect() as conn:
        # DBSequence
        rs = conn.execute(text("SELECT * FROM DBSequence;"))
        assert 12 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == "dbseq_P0C0V0_target"   # id from mzid
        assert results[0].accession == "P0C0V0"  # accession from mzid
        assert results[0].name == (  # name from mzid
            "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
            "OX=83333 GN=degP PE=1 SV=1")
        assert results[0].description == (  # protein description cvParam
            "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
            "OX=83333 GN=degP PE=1 SV=1"
        )
        assert results[0].sequence == (  # <Seq> value from mzid
            "MKKTTLALSALALSLGLALSPLSATAAETSSATTAQQMPSLAPMLEKVMPSVVSINVEGSTTVNTPRMPRNFQQFFGDDSPFCQEG"
            "SPFQSSPFCQGGQGGNGGGQQQKFMALGSGVIIDADKGYVVTNNHVVDNATVIKVQLSDGRKFDAKMVGKDPRSDIALIQIQNPKN"
            "LTAIKMADSDALRVGDYTVAIGNPFGLGETVTSGIVSALGRSGLNAENYENFIQTDAAINRGNSGGALVNLNGELIGINTAILAPD"
            "GGNIGIGFAIPSNMVKNLTSQMVEYGQVKRGELGIMGTELNSELAKAMKVDAQRGAFVSQVLPNSSAAKAGIKAGDVITSLNGKPI"
            "SSFAALRAQVGTMPVGSKLTLGLLRDGKQVNVNLELQQSSQNQVDSSSIFNGIEGAEMSNKGKDQGVVVNNVKTGTPAAQIGLKKG"
            "DVIIGANQQAVKNIAELRKVLDSKPSVLALNIQRGDSTIYLLMQ")
        # ToDo: check more rows?

        # Layout
        rs = conn.execute(text("SELECT * FROM Layout;"))
        assert 0 == rs.rowcount


        # Modification - parsed from <SearchModification>s
        rs = conn.execute(text("SELECT * FROM Modification;"))
        assert 8 == rs.rowcount
        compare_modifications_dsso_mzid(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        rs = conn.execute(text("SELECT * FROM Enzyme;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == "Trypsin_0"  # id from Enzyme element
        assert results[0].protocol_id == "SearchProtocol_1_0"
        assert results[0].c_term_gain == "OH"
        assert results[0].min_distance is None
        assert results[0].missed_cleavages == 2
        assert results[0].n_term_gain == "H"
        assert results[0].name == "Trypsin"
        assert results[0].semi_specific is False
        assert results[0].site_regexp == '(?<=[KR])(?\\!P)'
        assert results[0].accession == "MS:1001251"

        # PeptideEvidence
        rs = conn.execute(text("SELECT * FROM PeptideEvidence;"))
        assert 38 == rs.rowcount
        results = rs.fetchall()
        # peptide_ref from <PeptideEvidence>
        assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
        # dbsequence_ref from <PeptideEvidence>
        assert results[0].dbsequence_ref == 'dbseq_P0C0V0_target'
        assert results[0].pep_start == 148  # start from <PeptideEvidence>
        assert not results[0].is_decoy  # is_decoy from <PeptideEvidence>
        # ToDo: check more rows?

        # ModifiedPeptide
        rs = conn.execute(text("SELECT * FROM ModifiedPeptide;"))
        assert 38 == rs.rowcount
        results = rs.fetchall()
        # id from <Peptide> id
        assert results[0].id == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
        assert results[0].base_sequence == 'KFDAKMVGK'  # value of <PeptideSequence>
        assert results[0].modification_ids == []
        assert results[0].modification_positions == []
        # location of <Modification> with cross-link acceptor/receiver cvParam
        assert results[0].link_site == 5
        # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
        assert results[0].crosslinker_modmass == 0
        # value of cross-link acceptor/receiver cvParam
        assert results[0].crosslinker_pair_id == '1.0'

        # id from <Peptide> id
        assert results[1].id == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p0'
        assert results[1].base_sequence == 'KVLDSKPSVLALNIQR'  # value of <PeptideSequence>
        assert results[1].modification_ids == []
        assert results[1].modification_positions == []
        # location of <Modification> with cross-link acceptor/receiver cvParam
        assert results[1].link_site == 1
        # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
        assert results[1].crosslinker_modmass == 158.0037644600003
        # value of cross-link acceptor/receiver cvParam
        assert results[1].crosslinker_pair_id == '1.0'
        # ToDo: check more rows?

        # Spectrum
        rs = conn.execute(text("SELECT * FROM Spectrum;"))
        assert 22 == rs.rowcount
        results = rs.fetchall()
        # spectrumID from <SpectrumIdentificationResult>
        assert results[0].id == 'controllerType=0 controllerNumber=1 scan=14905'
        # spectraData_ref from <SpectrumIdentificationResult>
        assert results[0].spectra_data_ref == (
               'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML')
        # assert results[0].scan_id == '3'  # ToDo: keep this?
        assert results[0].peak_list_file_name == (  # ToDo
            'B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML')
        # Precursor info from mzML
        # Spectrum->precursorList->precursor[0]->selectedIonList->selectedIon[0]
        assert results[0].precursor_mz == 945.677381209342  # selected ion m/z
        assert results[0].precursor_charge == 5  # charge state
        # assert results[0].mz == []  # ToDo
        # assert results[0].intensity == []  # ToDo
        # ToDo: check more rows? could loop over spectra in MGF and compare to DB

        # SpectrumIdentification
        rs = conn.execute(text("SELECT * FROM SpectrumIdentification;"))
        assert 22 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == 'SII_3_1'  # id from first <SpectrumIdentificationItem>
        # spectrumID from <SpectrumIdentificationResult>
        assert results[0].spectrum_id == 'controllerType=0 controllerNumber=1 scan=14905'
        # spectraData_ref from <SpectrumIdentificationResult>
        assert results[0].spectra_data_ref == \
               'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML'
        # peptide_ref from <SpectrumIdentificationItem>
        assert results[0].pep1_id == \
               '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p1'
        # peptide_ref from matched <SpectrumIdentificationItem> by crosslink_identification_id
        assert results[0].pep2_id == \
               '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p0'
        assert results[0].charge_state == 5  # chargeState from <SpectrumIdentificationItem>
        assert results[0].pass_threshold  # passThreshold from <SpectrumIdentificationItem>
        assert results[0].rank == 1  # rank from <SpectrumIdentificationItem>
        # scores parsed from score related cvParams in <SpectrumIdentificationItem>
        assert results[0].scores == '{"xi:score": 33.814201}'
        # experimentalMassToCharge from <SpectrumIdentificationItem>
        assert results[0].exp_mz == 945.677359
        # calculatedMassToCharge from <SpectrumIdentificationItem>
        assert results[0].calc_mz == 945.6784858667701
        # Meta columns are only parsed from csv docs
        assert results[0].meta1 == ''
        assert results[0].meta2 == ''
        assert results[0].meta3 == ''

        # SpectrumIdentificationProtocol
        rs = conn.execute(text("SELECT * FROM SpectrumIdentificationProtocol;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()
        # parsed from <FragmentTolerance> in <SpectrumIdentificationProtocol>
        assert results[0].id == 'SearchProtocol_1_0'  # id from <SpectrumIdentificationProtocol>
        assert results[0].frag_tol == '5.0 ppm'
        assert results[0].ions == ['MS:1001118', 'MS:1001262']  # fallback to b and y ions
        assert results[0].analysis_software == (  # referenced <AnalysisSoftware> json
            '{"version": "2.1.5.2", "id": "xiFDR_id", "name": "XiFDR", "SoftwareName": '
            '{"xiFDR": ""}}')

        # Upload
        rs = conn.execute(text("SELECT * FROM Upload;"))
        assert 1 == rs.rowcount
        results = rs.fetchall()

        assert results[0].identification_file_name == 'mzml_ecoli_dsso.mzid'
        assert results[0].provider == (
            '{"id": "PROVIDER", "ContactRole": ['
            '{"contact_ref": "PERSON_DOC_OWNER", "Role": "researcher"}]}')
        assert results[0].audits == (
            '{"Person": {"lastName": "Kolbowski", "firstName": "Lars", "id": "PERSON_DOC_OWNER", '
            '"Affiliation": [{"organization_ref": "ORG_DOC_OWNER"}], '
            '"contact address": "TIB 4/4-3 Geb\\u00e4ude 17, Aufgang 1, Raum 476 '
            'Gustav-Meyer-Allee 25 13355 Berlin", '
            '"contact email": "lars.kolbowski@tu-berlin.de"}, '
            '"Organization": {"id": "ORG_DOC_OWNER", "name": "TU Berlin", '
            '"contact name": "TU Berlin"}}'
        )
        assert results[0].samples == '{}'
        assert results[0].bib == '[]'
        assert results[0].spectra_formats == (
            '[{"location": "B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML", '
            '"id": "SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML", '
            '"FileFormat": "mzML format", '
            '"SpectrumIDFormat": "mzML unique identifier"}, '
            '{"location": "B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML", '
            '"id": "SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML", '
            '"FileFormat": "mzML format", '
            '"SpectrumIDFormat": "mzML unique identifier"}]'
        )
        assert results[0].contains_crosslinks
        assert results[0].upload_error is None
        assert results[0].error_type is None
        assert results[0].upload_warnings == [
            'mzidentML file does not specify any fragment ions (child terms of MS_1002473) within '
            '<AdditionalSearchParams>. Falling back to b and y ions.']
        assert not results[0].deleted

    engine.dispose()

def test_mzid_parser_postgres_matrixscience(tmpdir, db_info, use_database, engine):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'F002553.mzid')
    peak_list_folder = False

    parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, db_info, use_database, engine)

    # test DBSequence (proteins)
    with engine.connect() as conn:

        # DBSequence
        rs = conn.execute(text("SELECT * FROM DBSequence;"))
        #  assert 12 == rs.rowcount
        results = rs.fetchall()
        pass

# def test_xispec_mzid_parser_mzml(tmpdir):
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
#     mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
#     peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
#     test_database = os.path.join(str(tmpdir), 'test.db')
#
#
#     # parse the mzid file
#     id_parser = MzIdParser.xiSPEC_MzIdParser(mzid, str(tmpdir), peak_list_folder, SQLite, logger)
#
#     id_parser.initialise_mzid_reader()
#     SQLite.create_tables(id_parser.cur, id_parser.con)
#     id_parser.parse()
#
#     # connect to the databases
#     test_con = SQLite.connect(test_database)
#     test_cur = test_con.cursor()
#
#     expected_db = os.path.join(fixtures_dir, 'mzml_ecoli_dsso_sqlite.db')
#     expected_con = SQLite.connect(expected_db)
#     expected_cur = expected_con.cursor()
#
#     compare_databases(expected_cur, test_cur)
#
#
# def test_xispec_mzid_parser_mgf(tmpdir):
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
#     mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
#     peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
#     test_database = os.path.join(str(tmpdir), 'test.db')
#
#     # parse the mzid file
#     id_parser = MzIdParser.xiSPEC_MzIdParser(mzid, str(tmpdir), peak_list_folder, SQLite, logger,
#                                              db_name=test_database)
#
#     id_parser.initialise_mzid_reader()
#     SQLite.create_tables(id_parser.cur, id_parser.con)
#     id_parser.parse()
#
#     # connect to the databases
#     test_con = SQLite.connect(test_database)
#     test_cur = test_con.cursor()
#
#     expected_db = os.path.join(fixtures_dir, 'mgf_ecoli_dsso_sqlite.db')
#     expected_con = SQLite.connect(expected_db)
#     expected_cur = expected_con.cursor()
#
#     compare_databases(expected_cur, test_cur)
