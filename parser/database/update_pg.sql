--add index to useraccount?

CREATE TABLE spectrumidentificationprotocol (
	id text NOT NULL,
	upload_id bigint NOT NULL,
	frag_tol text NOT NULL,
	search_params json NULL,
	analysis_software json NULL
);

ALTER TABLE public.modifications RENAME TO searchmodification;
ALTER TABLE public.modifications ADD protocol_id text NOT NULL;
ALTER TABLE public.modifications ADD specificity_rules json NOT NULL;
ALTER TABLE public.modifications ADD fixed_mod bool NOT NULL;
ALTER TABLE public.modifications ADD crosslinker_id text NULL;


CREATE TABLE enzyme (
	id text NOT NULL,
	upload_id bigint NOT NULL,
	protocol_id text NOT NULL,
	c_term_gain text NULL,
	min_distance int NULL,
	missed_cleavages int NULL,
	n_term_gain text NULL,
	"name" text NULL,
	semi_specific boolean NULL,
	site_regexp text NULL,
	accession text NULL
);

ALTER TABLE IF EXISTS db_sequences RENAME TO dbsequence;
ALTER TABLE dbsequence rename COLUMN protein_name TO name;

ALTER TABLE IF EXISTS peptides RENAME TO modifiedpeptide;
ALTER TABLE public.modifiedpeptide RENAME COLUMN seq_mods TO base_sequence;
ALTER TABLE public.modifiedpeptide ADD mod_accessions json NOT NULL;
ALTER TABLE public.modifiedpeptide ADD mod_avg_mass_deltas json NULL;
ALTER TABLE public.modifiedpeptide ADD mod_monoiso_mass_deltas json NULL;
ALTER TABLE public.modifiedpeptide ADD mod_positions json NULL;
ALTER TABLE public.modifiedpeptide RENAME COLUMN link_site TO link_site1;
ALTER TABLE public.modifiedpeptide ADD link_site2 int4 NULL;
ALTER TABLE public.modifiedpeptide ADD crosslinker_accession text NULL;

ALTER TABLE public.peptide_evidences RENAME TO peptideevidence;

ALTER TABLE public.spectrum_identifications RENAME TO spectrumidentification;
ALTER TABLE public.spectrumidentification ADD spectra_data_ref text NULL;
ALTER TABLE public.spectrumidentification ADD crosslinker_identification_id integer NULL;
ALTER TABLE public.spectrumidentification DROP COLUMN ions;
ALTER TABLE public.spectrumidentification ALTER COLUMN id TYPE text USING id::text;
ALTER TABLE public.spectrumidentification ALTER COLUMN spectrum_id TYPE text USING spectrum_id::text;

ALTER TABLE public.layouts RENAME TO layout;
ALTER TABLE public.layout RENAME COLUMN search_id TO upload_id;

ALTER TABLE public.spectra RENAME TO spectrum;

ALTER TABLE public.upload DROP COLUMN peak_list_file_names;
ALTER TABLE public.upload DROP COLUMN analysis_software;
ALTER TABLE public.upload DROP COLUMN analyses;
ALTER TABLE public.upload DROP COLUMN protocol;
ALTER TABLE public.upload DROP COLUMN default_pdb;
ALTER TABLE public.upload DROP COLUMN origin;
ALTER TABLE public.upload DROP COLUMN ident_count;
ALTER TABLE public.upload DROP COLUMN ident_file_size;
ALTER TABLE public.upload DROP COLUMN zipped_peak_list_file_size;

ALTER TABLE public.spectrumidentificationprotocol RENAME COLUMN ions TO search_params;
