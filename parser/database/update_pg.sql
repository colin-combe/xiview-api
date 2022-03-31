ALTER TABLE IF EXISTS users RENAME TO useraccount;
alter table useraccount drop column max_aas;
alter table useraccount drop column max_spectra;
alter table useraccount drop column hidden;
drop table user_in_group;
--add index to useraccount

**remove uploads where deleted = true

ALTER TABLE IF EXISTS uploads RENAME TO upload;
ALTER TABLE upload rename COLUMN filename TO identification_file_name;

CREATE TABLE spectrumidentificationprotocol (
	id text NOT NULL,
	upload_id bigint NOT NULL,
	frag_tol text NOT NULL,
	ions json NULL,
	analysis_software json NULL
);

-- no, rename existing modification table
CREATE TABLE searchmodification (
	id bigint NOT NULL,
	upload_id bigint NOT NULL,
	protocol_id text NOT NULL,
	mod_name text NOT NULL,
	mass float8 NOT NULL,
	residues text NOT NULL,
	specificity_rules json NOT NULL,
	fixed_mod boolean NOT NULL,
	accession text NULL,
	crosslinker_id text NULL
);

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
