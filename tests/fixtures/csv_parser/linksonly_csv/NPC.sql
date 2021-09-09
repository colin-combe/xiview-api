--
-- PostgreSQL database dump
--

-- Dumped from database version 12.8 (Ubuntu 12.8-1.pgdg20.04+1)
-- Dumped by pg_dump version 12.8 (Ubuntu 12.8-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: make_uid(); Type: FUNCTION; Schema: public; Owner: xiadmin
--

CREATE FUNCTION public.make_uid() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN 
	return  CAST( '' || trunc(random()*10) ||  trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10)
                                || '-' || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10)
                                || '-' || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10)
                                || '-' || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10) || trunc(random()*10)
                                  AS varchar);
END;
$$;


ALTER FUNCTION public.make_uid() OWNER TO xiadmin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: db_sequences; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.db_sequences (
    id text,
    upload_id integer,
    accession text,
    protein_name text,
    description text,
    sequence text,
    is_decoy boolean
);


ALTER TABLE public.db_sequences OWNER TO xiadmin;

--
-- Name: layouts; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.layouts (
    search_id text NOT NULL,
    user_id integer NOT NULL,
    "time" timestamp without time zone DEFAULT now() NOT NULL,
    layout text,
    description text
);


ALTER TABLE public.layouts OWNER TO xiadmin;

--
-- Name: modifications; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.modifications (
    id bigint,
    upload_id integer,
    mod_name text,
    mass double precision,
    residues text,
    accession text
);


ALTER TABLE public.modifications OWNER TO xiadmin;

--
-- Name: peptide_evidences; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.peptide_evidences (
    upload_id integer,
    peptide_ref text,
    dbsequence_ref text,
    protein_accession text,
    pep_start integer,
    is_decoy boolean
);


ALTER TABLE public.peptide_evidences OWNER TO xiadmin;

--
-- Name: peptides; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.peptides (
    id text,
    upload_id integer,
    seq_mods text,
    link_site integer,
    crosslinker_modmass double precision,
    crosslinker_pair_id character varying
);


ALTER TABLE public.peptides OWNER TO xiadmin;

--
-- Name: spectra; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.spectra (
    id bigint,
    upload_id integer,
    peak_list_file_name text,
    scan_id text,
    frag_tol text,
    spectrum_ref text,
    precursor_charge smallint,
    precursor_mz double precision,
    mz double precision[],
    intensity real[]
);


ALTER TABLE public.spectra OWNER TO xiadmin;

--
-- Name: spectrum_identifications; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.spectrum_identifications (
    id bigint,
    upload_id integer,
    spectrum_id bigint,
    pep1_id text,
    pep2_id text,
    charge_state integer,
    pass_threshold boolean,
    rank integer,
    ions text,
    scores json,
    exp_mz double precision,
    calc_mz double precision,
    meta1 character varying,
    meta2 character varying,
    meta3 character varying
);


ALTER TABLE public.spectrum_identifications OWNER TO xiadmin;

--
-- Name: uploads; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.uploads (
    id integer NOT NULL,
    user_id integer,
    filename text,
    peak_list_file_names json,
    analysis_software json,
    provider json,
    audits json,
    samples json,
    analyses json,
    protocol json,
    bib json,
    spectra_formats json,
    upload_time timestamp without time zone,
    default_pdb text,
    contains_crosslinks boolean,
    upload_error text,
    error_type text,
    upload_warnings json,
    origin text,
    random_id character varying DEFAULT public.make_uid(),
    deleted boolean DEFAULT false,
    ident_count bigint,
    ident_file_size bigint,
    zipped_peak_list_file_size character varying
);


ALTER TABLE public.uploads OWNER TO xiadmin;

--
-- Name: uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: xiadmin
--

CREATE SEQUENCE public.uploads_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uploads_id_seq OWNER TO xiadmin;

--
-- Name: uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xiadmin
--

ALTER SEQUENCE public.uploads_id_seq OWNED BY public.uploads.id;


--
-- Name: user_in_group; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.user_in_group (
    user_id integer,
    group_id integer
);


ALTER TABLE public.user_in_group OWNER TO xiadmin;

--
-- Name: users; Type: TABLE; Schema: public; Owner: xiadmin
--

CREATE TABLE public.users (
    user_name character varying,
    password character varying,
    email character varying,
    max_aas integer,
    max_spectra integer,
    gdpr_token character varying,
    id integer NOT NULL,
    ptoken character varying,
    hidden boolean,
    ptoken_timestamp timestamp without time zone,
    gdpr_timestamp timestamp without time zone
);


ALTER TABLE public.users OWNER TO xiadmin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: xiadmin
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO xiadmin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xiadmin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: uploads id; Type: DEFAULT; Schema: public; Owner: xiadmin
--

ALTER TABLE ONLY public.uploads ALTER COLUMN id SET DEFAULT nextval('public.uploads_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: xiadmin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: db_sequences; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.db_sequences (id, upload_id, accession, protein_name, description, sequence, is_decoy) FROM stdin;
sp|P57740|NU107_HUMAN	1	P57740	NU107_HUMAN		\N	\N
sp|P52948|NUP98_HUMAN	1	P52948	NUP98_HUMAN		\N	\N
sp|Q8NFH4|NUP37_HUMAN	1	Q8NFH4	NUP37_HUMAN		\N	\N
sp|Q8WYP5|ELYS_HUMAN	1	Q8WYP5	ELYS_HUMAN		\N	\N
-	1	-	-		\N	\N
sp|P55735|SEC13_HUMAN	1	P55735	SEC13_HUMAN		\N	\N
sp|Q8WUM0|NU133_HUMAN	1	Q8WUM0	NU133_HUMAN		\N	\N
sp|Q9BW27|NUP85_HUMAN	1	Q9BW27	NUP85_HUMAN		\N	\N
sp|Q8NFH3|NUP43_HUMAN	1	Q8NFH3	NUP43_HUMAN		\N	\N
sp|Q96EE3|SEH1_HUMAN	1	Q96EE3	SEH1_HUMAN		\N	\N
sp|Q12769|NU160_HUMAN	1	Q12769	NU160_HUMAN		\N	\N
\.


--
-- Data for Name: layouts; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.layouts (search_id, user_id, "time", layout, description) FROM stdin;
\.


--
-- Data for Name: modifications; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.modifications (id, upload_id, mod_name, mass, residues, accession) FROM stdin;
\.


--
-- Data for Name: peptide_evidences; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.peptide_evidences (upload_id, peptide_ref, dbsequence_ref, protein_accession, pep_start, is_decoy) FROM stdin;
1	0	sp|P57740|NU107_HUMAN	P57740	803	f
1	1	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	2	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	3	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	4	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	5	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	6	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	7	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	8	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	9	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	10	sp|Q12769|NU160_HUMAN	Q12769	608	f
1	11	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1992	f
1	12	sp|P57740|NU107_HUMAN	P57740	537	f
1	13	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	967	f
1	14	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	15	sp|P52948|NUP98_HUMAN	P52948	858	f
1	16	sp|Q9BW27|NUP85_HUMAN	Q9BW27	44	f
1	17	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	2163	f
1	18	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	19	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1049	f
1	20	sp|P57740|NU107_HUMAN	P57740	367	f
1	21	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1010	f
1	22	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	23	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	24	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	25	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	26	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	27	sp|Q8NFH3|NUP43_HUMAN	Q8NFH3	161	f
1	28	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	29	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1010	f
1	30	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	31	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	32	sp|P57740|NU107_HUMAN	P57740	814	f
1	33	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	968	f
1	34	sp|Q12769|NU160_HUMAN	Q12769	1096	f
1	35	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	36	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	37	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1010	f
1	38	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	39	sp|Q8NFH3|NUP43_HUMAN	Q8NFH3	161	f
1	40	sp|Q9BW27|NUP85_HUMAN	Q9BW27	218	f
1	41	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	42	sp|P52948|NUP98_HUMAN	P52948	1040	f
1	43	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	44	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	45	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	46	sp|P52948|NUP98_HUMAN	P52948	534	f
1	47	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	186	f
1	48	sp|P52948|NUP98_HUMAN	P52948	1052	f
1	49	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	50	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1989	f
1	51	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1049	f
1	52	sp|P57740|NU107_HUMAN	P57740	367	f
1	53	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	595	f
1	54	sp|Q12769|NU160_HUMAN	Q12769	1120	f
1	55	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	523	f
1	56	sp|Q96EE3|SEH1_HUMAN	Q96EE3	54	f
1	57	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	58	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	969	f
1	59	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1061	f
1	60	sp|Q96EE3|SEH1_HUMAN	Q96EE3	54	f
1	61	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	62	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	63	sp|P52948|NUP98_HUMAN	P52948	1200	f
1	64	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	65	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	66	sp|P52948|NUP98_HUMAN	P52948	1200	f
1	67	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	68	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1002	f
1	69	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1010	f
1	70	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	71	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	72	sp|P57740|NU107_HUMAN	P57740	698	f
1	73	sp|P57740|NU107_HUMAN	P57740	704	f
1	74	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	75	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	76	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	77	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	78	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	79	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	80	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1110	f
1	81	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1049	f
1	82	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	83	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	84	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	85	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	86	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	87	sp|Q9BW27|NUP85_HUMAN	Q9BW27	551	f
1	88	sp|P57740|NU107_HUMAN	P57740	690	f
1	89	sp|P57740|NU107_HUMAN	P57740	837	f
1	90	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	91	sp|Q9BW27|NUP85_HUMAN	Q9BW27	471	f
1	92	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	787	f
1	93	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	842	f
1	94	sp|Q9BW27|NUP85_HUMAN	Q9BW27	218	f
1	95	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	96	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	114	f
1	97	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	103	f
1	98	sp|Q96EE3|SEH1_HUMAN	Q96EE3	255	f
1	99	sp|Q96EE3|SEH1_HUMAN	Q96EE3	251	f
1	100	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	787	f
1	101	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	842	f
1	102	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	103	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	104	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	105	sp|P52948|NUP98_HUMAN	P52948	1040	f
1	106	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	107	sp|Q9BW27|NUP85_HUMAN	Q9BW27	551	f
1	108	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1017	f
1	109	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1010	f
1	110	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	111	sp|Q9BW27|NUP85_HUMAN	Q9BW27	551	f
1	112	sp|Q8NFH3|NUP43_HUMAN	Q8NFH3	161	f
1	113	sp|Q8NFH3|NUP43_HUMAN	Q8NFH3	161	f
1	114	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	115	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	116	sp|Q9BW27|NUP85_HUMAN	Q9BW27	471	f
1	117	sp|Q9BW27|NUP85_HUMAN	Q9BW27	551	f
1	118	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	119	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	120	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	121	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	122	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	123	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	124	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	125	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	126	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1251	f
1	127	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	709	f
1	128	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	129	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	130	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	131	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	132	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	133	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	134	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	135	sp|P52948|NUP98_HUMAN	P52948	1040	f
1	136	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	137	sp|P52948|NUP98_HUMAN	P52948	1200	f
1	138	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	139	sp|Q9BW27|NUP85_HUMAN	Q9BW27	540	f
1	140	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	141	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	142	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	787	f
1	143	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	842	f
1	144	sp|Q96EE3|SEH1_HUMAN	Q96EE3	54	f
1	145	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	146	sp|P52948|NUP98_HUMAN	P52948	1200	f
1	147	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	148	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	149	sp|Q9BW27|NUP85_HUMAN	Q9BW27	471	f
1	150	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	94	f
1	151	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	114	f
1	152	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	153	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	154	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	155	sp|Q9BW27|NUP85_HUMAN	Q9BW27	551	f
1	156	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	787	f
1	157	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	842	f
1	158	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	159	sp|Q9BW27|NUP85_HUMAN	Q9BW27	103	f
1	160	sp|Q9BW27|NUP85_HUMAN	Q9BW27	218	f
1	161	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	162	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	114	f
1	163	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	103	f
1	164	sp|Q96EE3|SEH1_HUMAN	Q96EE3	255	f
1	165	-	-	-1	f
1	166	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1107	f
1	167	-	-	-1	f
1	168	sp|Q12769|NU160_HUMAN	Q12769	1422	f
1	169	-	-	-1	f
1	170	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	171	-	-	-1	f
1	172	sp|Q96EE3|SEH1_HUMAN	Q96EE3	208	f
1	173	-	-	-1	f
1	174	sp|Q9BW27|NUP85_HUMAN	Q9BW27	449	f
1	175	-	-	-1	f
1	176	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	177	-	-	-1	f
1	178	sp|Q9BW27|NUP85_HUMAN	Q9BW27	42	f
1	179	-	-	-1	f
1	180	sp|P55735|SEC13_HUMAN	P55735	195	f
1	181	-	-	-1	f
1	182	sp|P55735|SEC13_HUMAN	P55735	203	f
1	183	-	-	-1	f
1	184	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1034	f
1	185	-	-	-1	f
1	186	sp|P52948|NUP98_HUMAN	P52948	1601	f
1	187	-	-	-1	f
1	188	sp|P57740|NU107_HUMAN	P57740	645	f
1	189	-	-	-1	f
1	190	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	969	f
1	191	-	-	-1	f
1	192	sp|Q96EE3|SEH1_HUMAN	Q96EE3	255	f
1	193	-	-	-1	f
1	194	sp|P57740|NU107_HUMAN	P57740	502	f
1	195	-	-	-1	f
1	196	sp|Q96EE3|SEH1_HUMAN	Q96EE3	208	f
1	197	-	-	-1	f
1	198	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	1107	f
1	199	-	-	-1	f
1	200	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	114	f
1	201	-	-	-1	f
1	202	sp|P57740|NU107_HUMAN	P57740	645	f
1	203	-	-	-1	f
1	204	sp|Q9BW27|NUP85_HUMAN	Q9BW27	42	f
1	205	-	-	-1	f
1	206	sp|P55735|SEC13_HUMAN	P55735	195	f
1	207	-	-	-1	f
1	208	sp|Q96EE3|SEH1_HUMAN	Q96EE3	208	f
1	209	-	-	-1	f
1	210	sp|P57740|NU107_HUMAN	P57740	626	f
1	211	-	-	-1	f
1	212	sp|Q9BW27|NUP85_HUMAN	Q9BW27	59	f
1	213	-	-	-1	f
1	214	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	1271	f
1	215	-	-	-1	f
1	216	sp|Q12769|NU160_HUMAN	Q12769	1006	f
1	217	-	-	-1	f
1	218	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	219	-	-	-1	f
1	220	sp|Q12769|NU160_HUMAN	Q12769	1006	f
1	221	-	-	-1	f
1	222	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	991	f
1	223	-	-	-1	f
1	224	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	225	-	-	-1	f
1	226	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	227	-	-	-1	f
1	228	sp|Q12769|NU160_HUMAN	Q12769	939	f
1	229	-	-	-1	f
1	230	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	231	-	-	-1	f
1	232	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	233	-	-	-1	f
1	234	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	35	f
1	235	-	-	-1	f
1	236	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	258	f
1	237	-	-	-1	f
1	238	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	35	f
1	239	-	-	-1	f
1	240	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	241	-	-	-1	f
1	242	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	758	f
1	243	-	-	-1	f
1	244	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	654	f
1	245	-	-	-1	f
1	246	sp|P52948|NUP98_HUMAN	P52948	1722	f
1	247	-	-	-1	f
1	248	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	674	f
1	249	-	-	-1	f
1	250	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	654	f
1	251	-	-	-1	f
1	252	sp|Q96EE3|SEH1_HUMAN	Q96EE3	124	f
1	253	-	-	-1	f
1	254	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	35	f
1	255	-	-	-1	f
1	256	sp|Q96EE3|SEH1_HUMAN	Q96EE3	54	f
1	257	-	-	-1	f
1	258	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	259	-	-	-1	f
1	260	sp|Q9BW27|NUP85_HUMAN	Q9BW27	218	f
1	261	-	-	-1	f
1	262	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	263	-	-	-1	f
1	264	sp|Q96EE3|SEH1_HUMAN	Q96EE3	243	f
1	265	-	-	-1	f
1	266	sp|Q12769|NU160_HUMAN	Q12769	1120	f
1	267	-	-	-1	f
1	268	sp|P52948|NUP98_HUMAN	P52948	1200	f
1	269	-	-	-1	f
1	270	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	758	f
1	271	-	-	-1	f
1	272	sp|Q12769|NU160_HUMAN	Q12769	833	f
1	273	-	-	-1	f
1	274	sp|P52948|NUP98_HUMAN	P52948	1341	f
1	275	-	-	-1	f
1	276	sp|Q96EE3|SEH1_HUMAN	Q96EE3	251	f
1	277	-	-	-1	f
1	278	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	606	f
1	279	-	-	-1	f
1	280	sp|P55735|SEC13_HUMAN	P55735	207	f
1	281	-	-	-1	f
1	282	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	758	f
1	283	-	-	-1	f
1	284	sp|Q12769|NU160_HUMAN	Q12769	343	f
1	285	-	-	-1	f
1	286	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	287	-	-	-1	f
1	288	sp|P55735|SEC13_HUMAN	P55735	203	f
1	289	-	-	-1	f
1	290	sp|P57740|NU107_HUMAN	P57740	626	f
1	291	-	-	-1	f
1	292	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	293	-	-	-1	f
1	294	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	295	-	-	-1	f
1	296	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	297	-	-	-1	f
1	298	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	239	f
1	299	-	-	-1	f
1	300	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	239	f
1	301	-	-	-1	f
1	302	sp|P52948|NUP98_HUMAN	P52948	1668	f
1	303	-	-	-1	f
1	304	sp|Q96EE3|SEH1_HUMAN	Q96EE3	251	f
1	305	-	-	-1	f
1	306	sp|Q12769|NU160_HUMAN	Q12769	343	f
1	307	-	-	-1	f
1	308	sp|P57740|NU107_HUMAN	P57740	646	f
1	309	-	-	-1	f
1	310	sp|P57740|NU107_HUMAN	P57740	837	f
1	311	-	-	-1	f
1	312	sp|Q12769|NU160_HUMAN	Q12769	1120	f
1	313	-	-	-1	f
1	314	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	315	-	-	-1	f
1	316	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	317	-	-	-1	f
1	318	sp|Q9BW27|NUP85_HUMAN	Q9BW27	44	f
1	319	-	-	-1	f
1	320	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	321	-	-	-1	f
1	322	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	323	-	-	-1	f
1	324	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	325	-	-	-1	f
1	326	sp|P52948|NUP98_HUMAN	P52948	1040	f
1	327	-	-	-1	f
1	328	sp|P57740|NU107_HUMAN	P57740	502	f
1	329	-	-	-1	f
1	330	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	318	f
1	331	-	-	-1	f
1	332	sp|Q12769|NU160_HUMAN	Q12769	722	f
1	333	-	-	-1	f
1	334	sp|Q9BW27|NUP85_HUMAN	Q9BW27	257	f
1	335	-	-	-1	f
1	336	sp|Q96EE3|SEH1_HUMAN	Q96EE3	211	f
1	337	-	-	-1	f
1	338	sp|Q12769|NU160_HUMAN	Q12769	1159	f
1	339	-	-	-1	f
1	340	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	341	-	-	-1	f
1	342	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	246	f
1	343	-	-	-1	f
1	344	sp|P52948|NUP98_HUMAN	P52948	1749	f
1	345	-	-	-1	f
1	346	sp|P52948|NUP98_HUMAN	P52948	1722	f
1	347	-	-	-1	f
1	348	sp|P55735|SEC13_HUMAN	P55735	305	f
1	349	-	-	-1	f
1	350	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	351	-	-	-1	f
1	352	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	353	-	-	-1	f
1	354	sp|P52948|NUP98_HUMAN	P52948	1213	f
1	355	-	-	-1	f
1	356	sp|P57740|NU107_HUMAN	P57740	332	f
1	357	-	-	-1	f
1	358	sp|P52948|NUP98_HUMAN	P52948	1341	f
1	359	-	-	-1	f
1	360	sp|P52948|NUP98_HUMAN	P52948	1052	f
1	361	-	-	-1	f
1	362	sp|Q12769|NU160_HUMAN	Q12769	689	f
1	363	-	-	-1	f
1	364	sp|Q96EE3|SEH1_HUMAN	Q96EE3	37	f
1	365	-	-	-1	f
1	366	sp|P52948|NUP98_HUMAN	P52948	1213	f
1	367	-	-	-1	f
1	368	sp|P57740|NU107_HUMAN	P57740	814	f
1	369	-	-	-1	f
1	370	sp|Q96EE3|SEH1_HUMAN	Q96EE3	124	f
1	371	-	-	-1	f
1	372	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	246	f
1	373	-	-	-1	f
1	374	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	375	-	-	-1	f
1	376	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	654	f
1	377	-	-	-1	f
1	378	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	379	-	-	-1	f
1	380	sp|Q96EE3|SEH1_HUMAN	Q96EE3	54	f
1	381	-	-	-1	f
1	382	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	2092	f
1	383	-	-	-1	f
1	384	sp|Q8WYP5|ELYS_HUMAN	Q8WYP5	2092	f
1	385	-	-	-1	f
1	386	sp|Q96EE3|SEH1_HUMAN	Q96EE3	265	f
1	387	-	-	-1	f
1	388	sp|Q12769|NU160_HUMAN	Q12769	1006	f
1	389	-	-	-1	f
1	390	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	391	-	-	-1	f
1	392	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	393	-	-	-1	f
1	394	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	258	f
1	395	-	-	-1	f
1	396	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	397	-	-	-1	f
1	398	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	606	f
1	399	-	-	-1	f
1	400	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	401	-	-	-1	f
1	402	sp|Q9BW27|NUP85_HUMAN	Q9BW27	285	f
1	403	-	-	-1	f
1	404	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	991	f
1	405	-	-	-1	f
1	406	sp|Q9BW27|NUP85_HUMAN	Q9BW27	218	f
1	407	-	-	-1	f
1	408	sp|P52948|NUP98_HUMAN	P52948	1722	f
1	409	-	-	-1	f
1	410	sp|Q12769|NU160_HUMAN	Q12769	307	f
1	411	-	-	-1	f
1	412	sp|P55735|SEC13_HUMAN	P55735	175	f
1	413	-	-	-1	f
1	414	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	415	-	-	-1	f
1	416	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	654	f
1	417	-	-	-1	f
1	418	sp|P55735|SEC13_HUMAN	P55735	207	f
1	419	-	-	-1	f
1	420	sp|P52948|NUP98_HUMAN	P52948	1052	f
1	421	-	-	-1	f
1	422	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	423	-	-	-1	f
1	424	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	758	f
1	425	-	-	-1	f
1	426	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	427	-	-	-1	f
1	428	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	239	f
1	429	-	-	-1	f
1	430	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	758	f
1	431	-	-	-1	f
1	432	sp|Q9BW27|NUP85_HUMAN	Q9BW27	95	f
1	433	-	-	-1	f
1	434	sp|P55735|SEC13_HUMAN	P55735	203	f
1	435	-	-	-1	f
1	436	sp|P52948|NUP98_HUMAN	P52948	1668	f
1	437	-	-	-1	f
1	438	sp|P52948|NUP98_HUMAN	P52948	1040	f
1	439	-	-	-1	f
1	440	sp|Q96EE3|SEH1_HUMAN	Q96EE3	124	f
1	441	-	-	-1	f
1	442	sp|Q96EE3|SEH1_HUMAN	Q96EE3	105	f
1	443	-	-	-1	f
1	444	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	239	f
1	445	-	-	-1	f
1	446	sp|Q96EE3|SEH1_HUMAN	Q96EE3	96	f
1	447	-	-	-1	f
1	448	sp|P52948|NUP98_HUMAN	P52948	1224	f
1	449	-	-	-1	f
1	450	sp|Q12769|NU160_HUMAN	Q12769	1159	f
1	451	-	-	-1	f
1	452	sp|Q12769|NU160_HUMAN	Q12769	258	f
1	453	-	-	-1	f
1	454	sp|P57740|NU107_HUMAN	P57740	502	f
1	455	-	-	-1	f
1	456	sp|Q96EE3|SEH1_HUMAN	Q96EE3	12	f
1	457	-	-	-1	f
1	458	sp|Q9BW27|NUP85_HUMAN	Q9BW27	257	f
1	459	-	-	-1	f
1	460	sp|P52948|NUP98_HUMAN	P52948	1668	f
1	461	-	-	-1	f
1	462	sp|Q12769|NU160_HUMAN	Q12769	1159	f
1	463	-	-	-1	f
1	464	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	318	f
1	465	-	-	-1	f
1	466	sp|Q9BW27|NUP85_HUMAN	Q9BW27	124	f
1	467	-	-	-1	f
1	468	sp|Q96EE3|SEH1_HUMAN	Q96EE3	255	f
1	469	-	-	-1	f
1	470	sp|P52948|NUP98_HUMAN	P52948	1207	f
1	471	-	-	-1	f
1	472	sp|Q9BW27|NUP85_HUMAN	Q9BW27	70	f
1	473	-	-	-1	f
1	474	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	118	f
1	475	-	-	-1	f
1	476	sp|Q96EE3|SEH1_HUMAN	Q96EE3	162	f
1	477	-	-	-1	f
1	478	sp|P55735|SEC13_HUMAN	P55735	195	f
1	479	-	-	-1	f
1	480	sp|P57740|NU107_HUMAN	P57740	837	f
1	481	-	-	-1	f
1	482	sp|P52948|NUP98_HUMAN	P52948	1107	f
1	483	-	-	-1	f
1	484	sp|Q96EE3|SEH1_HUMAN	Q96EE3	211	f
1	485	-	-	-1	f
1	486	sp|Q12769|NU160_HUMAN	Q12769	1006	f
1	487	-	-	-1	f
1	488	sp|P52948|NUP98_HUMAN	P52948	1019	f
1	489	-	-	-1	f
1	490	sp|P55735|SEC13_HUMAN	P55735	175	f
1	491	-	-	-1	f
1	492	sp|P57740|NU107_HUMAN	P57740	382	f
1	493	-	-	-1	f
1	494	sp|P55735|SEC13_HUMAN	P55735	180	f
1	495	-	-	-1	f
1	496	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	118	f
1	497	-	-	-1	f
1	498	sp|P52948|NUP98_HUMAN	P52948	1187	f
1	499	-	-	-1	f
1	500	sp|Q8NFH4|NUP37_HUMAN	Q8NFH4	135	f
1	501	-	-	-1	f
1	502	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	258	f
1	503	-	-	-1	f
1	504	sp|Q9BW27|NUP85_HUMAN	Q9BW27	494	f
1	505	-	-	-1	f
1	506	sp|P55735|SEC13_HUMAN	P55735	207	f
1	507	-	-	-1	f
1	508	sp|Q12769|NU160_HUMAN	Q12769	722	f
1	509	-	-	-1	f
1	510	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	511	-	-	-1	f
1	512	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	513	-	-	-1	f
1	514	sp|Q8NFH3|NUP43_HUMAN	Q8NFH3	298	f
1	515	-	-	-1	f
1	516	sp|Q12769|NU160_HUMAN	Q12769	1006	f
1	517	-	-	-1	f
1	518	sp|Q9BW27|NUP85_HUMAN	Q9BW27	631	f
1	519	-	-	-1	f
1	520	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	239	f
1	521	-	-	-1	f
1	522	sp|Q12769|NU160_HUMAN	Q12769	1159	f
1	523	-	-	-1	f
1	524	sp|Q12769|NU160_HUMAN	Q12769	1159	f
1	525	-	-	-1	f
1	526	sp|P52948|NUP98_HUMAN	P52948	1224	f
1	527	-	-	-1	f
1	528	sp|Q9BW27|NUP85_HUMAN	Q9BW27	92	f
1	529	-	-	-1	f
1	530	sp|P52948|NUP98_HUMAN	P52948	1187	f
1	531	-	-	-1	f
1	532	sp|Q8WUM0|NU133_HUMAN	Q8WUM0	913	f
1	533	-	-	-1	f
\.


--
-- Data for Name: peptides; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.peptides (id, upload_id, seq_mods, link_site, crosslinker_modmass, crosslinker_pair_id) FROM stdin;
0	1		1	\N	0
1	1		1	\N	0
2	1		1	\N	1
3	1		1	\N	1
4	1		1	\N	2
5	1		1	\N	2
6	1		1	\N	3
7	1		1	\N	3
8	1		1	\N	4
9	1		1	\N	4
10	1		1	\N	5
11	1		1	\N	5
12	1		1	\N	6
13	1		1	\N	6
14	1		1	\N	7
15	1		1	\N	7
16	1		1	\N	8
17	1		1	\N	8
18	1		1	\N	9
19	1		1	\N	9
20	1		1	\N	10
21	1		1	\N	10
22	1		1	\N	11
23	1		1	\N	11
24	1		1	\N	12
25	1		1	\N	12
26	1		1	\N	13
27	1		1	\N	13
28	1		1	\N	14
29	1		1	\N	14
30	1		1	\N	15
31	1		1	\N	15
32	1		1	\N	16
33	1		1	\N	16
34	1		1	\N	17
35	1		1	\N	17
36	1		1	\N	18
37	1		1	\N	18
38	1		1	\N	19
39	1		1	\N	19
40	1		1	\N	20
41	1		1	\N	20
42	1		1	\N	21
43	1		1	\N	21
44	1		1	\N	22
45	1		1	\N	22
46	1		1	\N	23
47	1		1	\N	23
48	1		1	\N	24
49	1		1	\N	24
50	1		1	\N	25
51	1		1	\N	25
52	1		1	\N	26
53	1		1	\N	26
54	1		1	\N	27
55	1		1	\N	27
56	1		1	\N	28
57	1		1	\N	28
58	1		1	\N	29
59	1		1	\N	29
60	1		1	\N	30
61	1		1	\N	30
62	1		1	\N	31
63	1		1	\N	31
64	1		1	\N	32
65	1		1	\N	32
66	1		1	\N	33
67	1		1	\N	33
68	1		1	\N	34
69	1		1	\N	34
70	1		1	\N	35
71	1		1	\N	35
72	1		1	\N	36
73	1		1	\N	36
74	1		1	\N	37
75	1		1	\N	37
76	1		1	\N	38
77	1		1	\N	38
78	1		1	\N	39
79	1		1	\N	39
80	1		1	\N	40
81	1		1	\N	40
82	1		1	\N	41
83	1		1	\N	41
84	1		1	\N	42
85	1		1	\N	42
86	1		1	\N	43
87	1		1	\N	43
88	1		1	\N	44
89	1		1	\N	44
90	1		1	\N	45
91	1		1	\N	45
92	1		1	\N	46
93	1		1	\N	46
94	1		1	\N	47
95	1		1	\N	47
96	1		1	\N	48
97	1		1	\N	48
98	1		1	\N	49
99	1		1	\N	49
100	1		1	\N	50
101	1		1	\N	50
102	1		1	\N	51
103	1		1	\N	51
104	1		1	\N	52
105	1		1	\N	52
106	1		1	\N	53
107	1		1	\N	53
108	1		1	\N	54
109	1		1	\N	54
110	1		1	\N	55
111	1		1	\N	55
112	1		1	\N	56
113	1		1	\N	56
114	1		1	\N	57
115	1		1	\N	57
116	1		1	\N	58
117	1		1	\N	58
118	1		1	\N	59
119	1		1	\N	59
120	1		1	\N	60
121	1		1	\N	60
122	1		1	\N	61
123	1		1	\N	61
124	1		1	\N	62
125	1		1	\N	62
126	1		1	\N	63
127	1		1	\N	63
128	1		1	\N	64
129	1		1	\N	64
130	1		1	\N	65
131	1		1	\N	65
132	1		1	\N	66
133	1		1	\N	66
134	1		1	\N	67
135	1		1	\N	67
136	1		1	\N	68
137	1		1	\N	68
138	1		1	\N	69
139	1		1	\N	69
140	1		1	\N	70
141	1		1	\N	70
142	1		1	\N	71
143	1		1	\N	71
144	1		1	\N	72
145	1		1	\N	72
146	1		1	\N	73
147	1		1	\N	73
148	1		1	\N	74
149	1		1	\N	74
150	1		1	\N	75
151	1		1	\N	75
152	1		1	\N	76
153	1		1	\N	76
154	1		1	\N	77
155	1		1	\N	77
156	1		1	\N	78
157	1		1	\N	78
158	1		1	\N	79
159	1		1	\N	79
160	1		1	\N	80
161	1		1	\N	80
162	1		1	\N	81
163	1		1	\N	81
164	1		1	\N	82
165	1		1	\N	82
166	1		1	\N	83
167	1		1	\N	83
168	1		1	\N	84
169	1		1	\N	84
170	1		1	\N	85
171	1		1	\N	85
172	1		1	\N	86
173	1		1	\N	86
174	1		1	\N	87
175	1		1	\N	87
176	1		1	\N	88
177	1		1	\N	88
178	1		1	\N	89
179	1		1	\N	89
180	1		1	\N	90
181	1		1	\N	90
182	1		1	\N	91
183	1		1	\N	91
184	1		1	\N	92
185	1		1	\N	92
186	1		1	\N	93
187	1		1	\N	93
188	1		1	\N	94
189	1		1	\N	94
190	1		1	\N	95
191	1		1	\N	95
192	1		1	\N	96
193	1		1	\N	96
194	1		1	\N	97
195	1		1	\N	97
196	1		1	\N	98
197	1		1	\N	98
198	1		1	\N	99
199	1		1	\N	99
200	1		1	\N	100
201	1		1	\N	100
202	1		1	\N	101
203	1		1	\N	101
204	1		1	\N	102
205	1		1	\N	102
206	1		1	\N	103
207	1		1	\N	103
208	1		1	\N	104
209	1		1	\N	104
210	1		1	\N	105
211	1		1	\N	105
212	1		1	\N	106
213	1		1	\N	106
214	1		1	\N	107
215	1		1	\N	107
216	1		1	\N	108
217	1		1	\N	108
218	1		1	\N	109
219	1		1	\N	109
220	1		1	\N	110
221	1		1	\N	110
222	1		1	\N	111
223	1		1	\N	111
224	1		1	\N	112
225	1		1	\N	112
226	1		1	\N	113
227	1		1	\N	113
228	1		1	\N	114
229	1		1	\N	114
230	1		1	\N	115
231	1		1	\N	115
232	1		1	\N	116
233	1		1	\N	116
234	1		1	\N	117
235	1		1	\N	117
236	1		1	\N	118
237	1		1	\N	118
238	1		1	\N	119
239	1		1	\N	119
240	1		1	\N	120
241	1		1	\N	120
242	1		1	\N	121
243	1		1	\N	121
244	1		1	\N	122
245	1		1	\N	122
246	1		1	\N	123
247	1		1	\N	123
248	1		1	\N	124
249	1		1	\N	124
250	1		1	\N	125
251	1		1	\N	125
252	1		1	\N	126
253	1		1	\N	126
254	1		1	\N	127
255	1		1	\N	127
256	1		1	\N	128
257	1		1	\N	128
258	1		1	\N	129
259	1		1	\N	129
260	1		1	\N	130
261	1		1	\N	130
262	1		1	\N	131
263	1		1	\N	131
264	1		1	\N	132
265	1		1	\N	132
266	1		1	\N	133
267	1		1	\N	133
268	1		1	\N	134
269	1		1	\N	134
270	1		1	\N	135
271	1		1	\N	135
272	1		1	\N	136
273	1		1	\N	136
274	1		1	\N	137
275	1		1	\N	137
276	1		1	\N	138
277	1		1	\N	138
278	1		1	\N	139
279	1		1	\N	139
280	1		1	\N	140
281	1		1	\N	140
282	1		1	\N	141
283	1		1	\N	141
284	1		1	\N	142
285	1		1	\N	142
286	1		1	\N	143
287	1		1	\N	143
288	1		1	\N	144
289	1		1	\N	144
290	1		1	\N	145
291	1		1	\N	145
292	1		1	\N	146
293	1		1	\N	146
294	1		1	\N	147
295	1		1	\N	147
296	1		1	\N	148
297	1		1	\N	148
298	1		1	\N	149
299	1		1	\N	149
300	1		1	\N	150
301	1		1	\N	150
302	1		1	\N	151
303	1		1	\N	151
304	1		1	\N	152
305	1		1	\N	152
306	1		1	\N	153
307	1		1	\N	153
308	1		1	\N	154
309	1		1	\N	154
310	1		1	\N	155
311	1		1	\N	155
312	1		1	\N	156
313	1		1	\N	156
314	1		1	\N	157
315	1		1	\N	157
316	1		1	\N	158
317	1		1	\N	158
318	1		1	\N	159
319	1		1	\N	159
320	1		1	\N	160
321	1		1	\N	160
322	1		1	\N	161
323	1		1	\N	161
324	1		1	\N	162
325	1		1	\N	162
326	1		1	\N	163
327	1		1	\N	163
328	1		1	\N	164
329	1		1	\N	164
330	1		1	\N	165
331	1		1	\N	165
332	1		1	\N	166
333	1		1	\N	166
334	1		1	\N	167
335	1		1	\N	167
336	1		1	\N	168
337	1		1	\N	168
338	1		1	\N	169
339	1		1	\N	169
340	1		1	\N	170
341	1		1	\N	170
342	1		1	\N	171
343	1		1	\N	171
344	1		1	\N	172
345	1		1	\N	172
346	1		1	\N	173
347	1		1	\N	173
348	1		1	\N	174
349	1		1	\N	174
350	1		1	\N	175
351	1		1	\N	175
352	1		1	\N	176
353	1		1	\N	176
354	1		1	\N	177
355	1		1	\N	177
356	1		1	\N	178
357	1		1	\N	178
358	1		1	\N	179
359	1		1	\N	179
360	1		1	\N	180
361	1		1	\N	180
362	1		1	\N	181
363	1		1	\N	181
364	1		1	\N	182
365	1		1	\N	182
366	1		1	\N	183
367	1		1	\N	183
368	1		1	\N	184
369	1		1	\N	184
370	1		1	\N	185
371	1		1	\N	185
372	1		1	\N	186
373	1		1	\N	186
374	1		1	\N	187
375	1		1	\N	187
376	1		1	\N	188
377	1		1	\N	188
378	1		1	\N	189
379	1		1	\N	189
380	1		1	\N	190
381	1		1	\N	190
382	1		1	\N	191
383	1		1	\N	191
384	1		1	\N	192
385	1		1	\N	192
386	1		1	\N	193
387	1		1	\N	193
388	1		1	\N	194
389	1		1	\N	194
390	1		1	\N	195
391	1		1	\N	195
392	1		1	\N	196
393	1		1	\N	196
394	1		1	\N	197
395	1		1	\N	197
396	1		1	\N	198
397	1		1	\N	198
398	1		1	\N	199
399	1		1	\N	199
400	1		1	\N	200
401	1		1	\N	200
402	1		1	\N	201
403	1		1	\N	201
404	1		1	\N	202
405	1		1	\N	202
406	1		1	\N	203
407	1		1	\N	203
408	1		1	\N	204
409	1		1	\N	204
410	1		1	\N	205
411	1		1	\N	205
412	1		1	\N	206
413	1		1	\N	206
414	1		1	\N	207
415	1		1	\N	207
416	1		1	\N	208
417	1		1	\N	208
418	1		1	\N	209
419	1		1	\N	209
420	1		1	\N	210
421	1		1	\N	210
422	1		1	\N	211
423	1		1	\N	211
424	1		1	\N	212
425	1		1	\N	212
426	1		1	\N	213
427	1		1	\N	213
428	1		1	\N	214
429	1		1	\N	214
430	1		1	\N	215
431	1		1	\N	215
432	1		1	\N	216
433	1		1	\N	216
434	1		1	\N	217
435	1		1	\N	217
436	1		1	\N	218
437	1		1	\N	218
438	1		1	\N	219
439	1		1	\N	219
440	1		1	\N	220
441	1		1	\N	220
442	1		1	\N	221
443	1		1	\N	221
444	1		1	\N	222
445	1		1	\N	222
446	1		1	\N	223
447	1		1	\N	223
448	1		1	\N	224
449	1		1	\N	224
450	1		1	\N	225
451	1		1	\N	225
452	1		1	\N	226
453	1		1	\N	226
454	1		1	\N	227
455	1		1	\N	227
456	1		1	\N	228
457	1		1	\N	228
458	1		1	\N	229
459	1		1	\N	229
460	1		1	\N	230
461	1		1	\N	230
462	1		1	\N	231
463	1		1	\N	231
464	1		1	\N	232
465	1		1	\N	232
466	1		1	\N	233
467	1		1	\N	233
468	1		1	\N	234
469	1		1	\N	234
470	1		1	\N	235
471	1		1	\N	235
472	1		1	\N	236
473	1		1	\N	236
474	1		1	\N	237
475	1		1	\N	237
476	1		1	\N	238
477	1		1	\N	238
478	1		1	\N	239
479	1		1	\N	239
480	1		1	\N	240
481	1		1	\N	240
482	1		1	\N	241
483	1		1	\N	241
484	1		1	\N	242
485	1		1	\N	242
486	1		1	\N	243
487	1		1	\N	243
488	1		1	\N	244
489	1		1	\N	244
490	1		1	\N	245
491	1		1	\N	245
492	1		1	\N	246
493	1		1	\N	246
494	1		1	\N	247
495	1		1	\N	247
496	1		1	\N	248
497	1		1	\N	248
498	1		1	\N	249
499	1		1	\N	249
500	1		1	\N	250
501	1		1	\N	250
502	1		1	\N	251
503	1		1	\N	251
504	1		1	\N	252
505	1		1	\N	252
506	1		1	\N	253
507	1		1	\N	253
508	1		1	\N	254
509	1		1	\N	254
510	1		1	\N	255
511	1		1	\N	255
512	1		1	\N	256
513	1		1	\N	256
514	1		1	\N	257
515	1		1	\N	257
516	1		1	\N	258
517	1		1	\N	258
518	1		1	\N	259
519	1		1	\N	259
520	1		1	\N	260
521	1		1	\N	260
522	1		1	\N	261
523	1		1	\N	261
524	1		1	\N	262
525	1		1	\N	262
526	1		1	\N	263
527	1		1	\N	263
528	1		1	\N	264
529	1		1	\N	264
530	1		1	\N	265
531	1		1	\N	265
532	1		1	\N	266
533	1		1	\N	266
\.


--
-- Data for Name: spectra; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.spectra (id, upload_id, peak_list_file_name, scan_id, frag_tol, spectrum_ref, precursor_charge, precursor_mz, mz, intensity) FROM stdin;
\.


--
-- Data for Name: spectrum_identifications; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.spectrum_identifications (id, upload_id, spectrum_id, pep1_id, pep2_id, charge_state, pass_threshold, rank, ions, scores, exp_mz, calc_mz, meta1, meta2, meta3) FROM stdin;
0	1	\N	0	1	\N	t	1	\N	{"score": 0.0}	\N	\N			
1	1	\N	2	3	\N	t	1	\N	{"score": 0.0}	\N	\N			
2	1	\N	4	5	\N	t	1	\N	{"score": 0.0}	\N	\N			
3	1	\N	6	7	\N	t	1	\N	{"score": 0.0}	\N	\N			
4	1	\N	8	9	\N	t	1	\N	{"score": 0.0}	\N	\N			
5	1	\N	10	11	\N	t	1	\N	{"score": 0.0}	\N	\N			
6	1	\N	12	13	\N	t	1	\N	{"score": 0.0}	\N	\N			
7	1	\N	14	15	\N	t	1	\N	{"score": 0.0}	\N	\N			
8	1	\N	16	17	\N	t	1	\N	{"score": 0.0}	\N	\N			
9	1	\N	18	19	\N	t	1	\N	{"score": 0.0}	\N	\N			
10	1	\N	20	21	\N	t	1	\N	{"score": 0.0}	\N	\N			
11	1	\N	22	23	\N	t	1	\N	{"score": 0.0}	\N	\N			
12	1	\N	24	25	\N	t	1	\N	{"score": 0.0}	\N	\N			
13	1	\N	26	27	\N	t	1	\N	{"score": 0.0}	\N	\N			
14	1	\N	28	29	\N	t	1	\N	{"score": 0.0}	\N	\N			
15	1	\N	30	31	\N	t	1	\N	{"score": 0.0}	\N	\N			
16	1	\N	32	33	\N	t	1	\N	{"score": 0.0}	\N	\N			
17	1	\N	34	35	\N	t	1	\N	{"score": 0.0}	\N	\N			
18	1	\N	36	37	\N	t	1	\N	{"score": 0.0}	\N	\N			
19	1	\N	38	39	\N	t	1	\N	{"score": 0.0}	\N	\N			
20	1	\N	40	41	\N	t	1	\N	{"score": 0.0}	\N	\N			
21	1	\N	42	43	\N	t	1	\N	{"score": 0.0}	\N	\N			
22	1	\N	44	45	\N	t	1	\N	{"score": 0.0}	\N	\N			
23	1	\N	46	47	\N	t	1	\N	{"score": 0.0}	\N	\N			
24	1	\N	48	49	\N	t	1	\N	{"score": 0.0}	\N	\N			
25	1	\N	50	51	\N	t	1	\N	{"score": 0.0}	\N	\N			
26	1	\N	52	53	\N	t	1	\N	{"score": 0.0}	\N	\N			
27	1	\N	54	55	\N	t	1	\N	{"score": 0.0}	\N	\N			
28	1	\N	56	57	\N	t	1	\N	{"score": 0.0}	\N	\N			
29	1	\N	58	59	\N	t	1	\N	{"score": 0.0}	\N	\N			
30	1	\N	60	61	\N	t	1	\N	{"score": 0.0}	\N	\N			
31	1	\N	62	63	\N	t	1	\N	{"score": 0.0}	\N	\N			
32	1	\N	64	65	\N	t	1	\N	{"score": 0.0}	\N	\N			
33	1	\N	66	67	\N	t	1	\N	{"score": 0.0}	\N	\N			
34	1	\N	68	69	\N	t	1	\N	{"score": 0.0}	\N	\N			
35	1	\N	70	71	\N	t	1	\N	{"score": 0.0}	\N	\N			
36	1	\N	72	73	\N	t	1	\N	{"score": 0.0}	\N	\N			
37	1	\N	74	75	\N	t	1	\N	{"score": 0.0}	\N	\N			
38	1	\N	76	77	\N	t	1	\N	{"score": 0.0}	\N	\N			
39	1	\N	78	79	\N	t	1	\N	{"score": 0.0}	\N	\N			
40	1	\N	80	81	\N	t	1	\N	{"score": 0.0}	\N	\N			
41	1	\N	82	83	\N	t	1	\N	{"score": 0.0}	\N	\N			
42	1	\N	84	85	\N	t	1	\N	{"score": 0.0}	\N	\N			
43	1	\N	86	87	\N	t	1	\N	{"score": 0.0}	\N	\N			
44	1	\N	88	89	\N	t	1	\N	{"score": 0.0}	\N	\N			
45	1	\N	90	91	\N	t	1	\N	{"score": 0.0}	\N	\N			
46	1	\N	92	93	\N	t	1	\N	{"score": 0.0}	\N	\N			
47	1	\N	94	95	\N	t	1	\N	{"score": 0.0}	\N	\N			
48	1	\N	96	97	\N	t	1	\N	{"score": 0.0}	\N	\N			
49	1	\N	98	99	\N	t	1	\N	{"score": 0.0}	\N	\N			
50	1	\N	100	101	\N	t	1	\N	{"score": 0.0}	\N	\N			
51	1	\N	102	103	\N	t	1	\N	{"score": 0.0}	\N	\N			
52	1	\N	104	105	\N	t	1	\N	{"score": 0.0}	\N	\N			
53	1	\N	106	107	\N	t	1	\N	{"score": 0.0}	\N	\N			
54	1	\N	108	109	\N	t	1	\N	{"score": 0.0}	\N	\N			
55	1	\N	110	111	\N	t	1	\N	{"score": 0.0}	\N	\N			
56	1	\N	112	113	\N	t	1	\N	{"score": 0.0}	\N	\N			
57	1	\N	114	115	\N	t	1	\N	{"score": 0.0}	\N	\N			
58	1	\N	116	117	\N	t	1	\N	{"score": 0.0}	\N	\N			
59	1	\N	118	119	\N	t	1	\N	{"score": 0.0}	\N	\N			
60	1	\N	120	121	\N	t	1	\N	{"score": 0.0}	\N	\N			
61	1	\N	122	123	\N	t	1	\N	{"score": 0.0}	\N	\N			
62	1	\N	124	125	\N	t	1	\N	{"score": 0.0}	\N	\N			
63	1	\N	126	127	\N	t	1	\N	{"score": 0.0}	\N	\N			
64	1	\N	128	129	\N	t	1	\N	{"score": 0.0}	\N	\N			
65	1	\N	130	131	\N	t	1	\N	{"score": 0.0}	\N	\N			
66	1	\N	132	133	\N	t	1	\N	{"score": 0.0}	\N	\N			
67	1	\N	134	135	\N	t	1	\N	{"score": 0.0}	\N	\N			
68	1	\N	136	137	\N	t	1	\N	{"score": 0.0}	\N	\N			
69	1	\N	138	139	\N	t	1	\N	{"score": 0.0}	\N	\N			
70	1	\N	140	141	\N	t	1	\N	{"score": 0.0}	\N	\N			
71	1	\N	142	143	\N	t	1	\N	{"score": 0.0}	\N	\N			
72	1	\N	144	145	\N	t	1	\N	{"score": 0.0}	\N	\N			
73	1	\N	146	147	\N	t	1	\N	{"score": 0.0}	\N	\N			
74	1	\N	148	149	\N	t	1	\N	{"score": 0.0}	\N	\N			
75	1	\N	150	151	\N	t	1	\N	{"score": 0.0}	\N	\N			
76	1	\N	152	153	\N	t	1	\N	{"score": 0.0}	\N	\N			
77	1	\N	154	155	\N	t	1	\N	{"score": 0.0}	\N	\N			
78	1	\N	156	157	\N	t	1	\N	{"score": 0.0}	\N	\N			
79	1	\N	158	159	\N	t	1	\N	{"score": 0.0}	\N	\N			
80	1	\N	160	161	\N	t	1	\N	{"score": 0.0}	\N	\N			
81	1	\N	162	163	\N	t	1	\N	{"score": 0.0}	\N	\N			
82	1	\N	164	165	\N	t	1	\N	{"score": 0.0}	\N	\N			
83	1	\N	166	167	\N	t	1	\N	{"score": 0.0}	\N	\N			
84	1	\N	168	169	\N	t	1	\N	{"score": 0.0}	\N	\N			
85	1	\N	170	171	\N	t	1	\N	{"score": 0.0}	\N	\N			
86	1	\N	172	173	\N	t	1	\N	{"score": 0.0}	\N	\N			
87	1	\N	174	175	\N	t	1	\N	{"score": 0.0}	\N	\N			
88	1	\N	176	177	\N	t	1	\N	{"score": 0.0}	\N	\N			
89	1	\N	178	179	\N	t	1	\N	{"score": 0.0}	\N	\N			
90	1	\N	180	181	\N	t	1	\N	{"score": 0.0}	\N	\N			
91	1	\N	182	183	\N	t	1	\N	{"score": 0.0}	\N	\N			
92	1	\N	184	185	\N	t	1	\N	{"score": 0.0}	\N	\N			
93	1	\N	186	187	\N	t	1	\N	{"score": 0.0}	\N	\N			
94	1	\N	188	189	\N	t	1	\N	{"score": 0.0}	\N	\N			
95	1	\N	190	191	\N	t	1	\N	{"score": 0.0}	\N	\N			
96	1	\N	192	193	\N	t	1	\N	{"score": 0.0}	\N	\N			
97	1	\N	194	195	\N	t	1	\N	{"score": 0.0}	\N	\N			
98	1	\N	196	197	\N	t	1	\N	{"score": 0.0}	\N	\N			
99	1	\N	198	199	\N	t	1	\N	{"score": 0.0}	\N	\N			
100	1	\N	200	201	\N	t	1	\N	{"score": 0.0}	\N	\N			
101	1	\N	202	203	\N	t	1	\N	{"score": 0.0}	\N	\N			
102	1	\N	204	205	\N	t	1	\N	{"score": 0.0}	\N	\N			
103	1	\N	206	207	\N	t	1	\N	{"score": 0.0}	\N	\N			
104	1	\N	208	209	\N	t	1	\N	{"score": 0.0}	\N	\N			
105	1	\N	210	211	\N	t	1	\N	{"score": 0.0}	\N	\N			
106	1	\N	212	213	\N	t	1	\N	{"score": 0.0}	\N	\N			
107	1	\N	214	215	\N	t	1	\N	{"score": 0.0}	\N	\N			
108	1	\N	216	217	\N	t	1	\N	{"score": 0.0}	\N	\N			
109	1	\N	218	219	\N	t	1	\N	{"score": 0.0}	\N	\N			
110	1	\N	220	221	\N	t	1	\N	{"score": 0.0}	\N	\N			
111	1	\N	222	223	\N	t	1	\N	{"score": 0.0}	\N	\N			
112	1	\N	224	225	\N	t	1	\N	{"score": 0.0}	\N	\N			
113	1	\N	226	227	\N	t	1	\N	{"score": 0.0}	\N	\N			
114	1	\N	228	229	\N	t	1	\N	{"score": 0.0}	\N	\N			
115	1	\N	230	231	\N	t	1	\N	{"score": 0.0}	\N	\N			
116	1	\N	232	233	\N	t	1	\N	{"score": 0.0}	\N	\N			
117	1	\N	234	235	\N	t	1	\N	{"score": 0.0}	\N	\N			
118	1	\N	236	237	\N	t	1	\N	{"score": 0.0}	\N	\N			
119	1	\N	238	239	\N	t	1	\N	{"score": 0.0}	\N	\N			
120	1	\N	240	241	\N	t	1	\N	{"score": 0.0}	\N	\N			
121	1	\N	242	243	\N	t	1	\N	{"score": 0.0}	\N	\N			
122	1	\N	244	245	\N	t	1	\N	{"score": 0.0}	\N	\N			
123	1	\N	246	247	\N	t	1	\N	{"score": 0.0}	\N	\N			
124	1	\N	248	249	\N	t	1	\N	{"score": 0.0}	\N	\N			
125	1	\N	250	251	\N	t	1	\N	{"score": 0.0}	\N	\N			
126	1	\N	252	253	\N	t	1	\N	{"score": 0.0}	\N	\N			
127	1	\N	254	255	\N	t	1	\N	{"score": 0.0}	\N	\N			
128	1	\N	256	257	\N	t	1	\N	{"score": 0.0}	\N	\N			
129	1	\N	258	259	\N	t	1	\N	{"score": 0.0}	\N	\N			
130	1	\N	260	261	\N	t	1	\N	{"score": 0.0}	\N	\N			
131	1	\N	262	263	\N	t	1	\N	{"score": 0.0}	\N	\N			
132	1	\N	264	265	\N	t	1	\N	{"score": 0.0}	\N	\N			
133	1	\N	266	267	\N	t	1	\N	{"score": 0.0}	\N	\N			
134	1	\N	268	269	\N	t	1	\N	{"score": 0.0}	\N	\N			
135	1	\N	270	271	\N	t	1	\N	{"score": 0.0}	\N	\N			
136	1	\N	272	273	\N	t	1	\N	{"score": 0.0}	\N	\N			
137	1	\N	274	275	\N	t	1	\N	{"score": 0.0}	\N	\N			
138	1	\N	276	277	\N	t	1	\N	{"score": 0.0}	\N	\N			
139	1	\N	278	279	\N	t	1	\N	{"score": 0.0}	\N	\N			
140	1	\N	280	281	\N	t	1	\N	{"score": 0.0}	\N	\N			
141	1	\N	282	283	\N	t	1	\N	{"score": 0.0}	\N	\N			
142	1	\N	284	285	\N	t	1	\N	{"score": 0.0}	\N	\N			
143	1	\N	286	287	\N	t	1	\N	{"score": 0.0}	\N	\N			
144	1	\N	288	289	\N	t	1	\N	{"score": 0.0}	\N	\N			
145	1	\N	290	291	\N	t	1	\N	{"score": 0.0}	\N	\N			
146	1	\N	292	293	\N	t	1	\N	{"score": 0.0}	\N	\N			
147	1	\N	294	295	\N	t	1	\N	{"score": 0.0}	\N	\N			
148	1	\N	296	297	\N	t	1	\N	{"score": 0.0}	\N	\N			
149	1	\N	298	299	\N	t	1	\N	{"score": 0.0}	\N	\N			
150	1	\N	300	301	\N	t	1	\N	{"score": 0.0}	\N	\N			
151	1	\N	302	303	\N	t	1	\N	{"score": 0.0}	\N	\N			
152	1	\N	304	305	\N	t	1	\N	{"score": 0.0}	\N	\N			
153	1	\N	306	307	\N	t	1	\N	{"score": 0.0}	\N	\N			
154	1	\N	308	309	\N	t	1	\N	{"score": 0.0}	\N	\N			
155	1	\N	310	311	\N	t	1	\N	{"score": 0.0}	\N	\N			
156	1	\N	312	313	\N	t	1	\N	{"score": 0.0}	\N	\N			
157	1	\N	314	315	\N	t	1	\N	{"score": 0.0}	\N	\N			
158	1	\N	316	317	\N	t	1	\N	{"score": 0.0}	\N	\N			
159	1	\N	318	319	\N	t	1	\N	{"score": 0.0}	\N	\N			
160	1	\N	320	321	\N	t	1	\N	{"score": 0.0}	\N	\N			
161	1	\N	322	323	\N	t	1	\N	{"score": 0.0}	\N	\N			
162	1	\N	324	325	\N	t	1	\N	{"score": 0.0}	\N	\N			
163	1	\N	326	327	\N	t	1	\N	{"score": 0.0}	\N	\N			
164	1	\N	328	329	\N	t	1	\N	{"score": 0.0}	\N	\N			
165	1	\N	330	331	\N	t	1	\N	{"score": 0.0}	\N	\N			
166	1	\N	332	333	\N	t	1	\N	{"score": 0.0}	\N	\N			
167	1	\N	334	335	\N	t	1	\N	{"score": 0.0}	\N	\N			
168	1	\N	336	337	\N	t	1	\N	{"score": 0.0}	\N	\N			
169	1	\N	338	339	\N	t	1	\N	{"score": 0.0}	\N	\N			
170	1	\N	340	341	\N	t	1	\N	{"score": 0.0}	\N	\N			
171	1	\N	342	343	\N	t	1	\N	{"score": 0.0}	\N	\N			
172	1	\N	344	345	\N	t	1	\N	{"score": 0.0}	\N	\N			
173	1	\N	346	347	\N	t	1	\N	{"score": 0.0}	\N	\N			
174	1	\N	348	349	\N	t	1	\N	{"score": 0.0}	\N	\N			
175	1	\N	350	351	\N	t	1	\N	{"score": 0.0}	\N	\N			
176	1	\N	352	353	\N	t	1	\N	{"score": 0.0}	\N	\N			
177	1	\N	354	355	\N	t	1	\N	{"score": 0.0}	\N	\N			
178	1	\N	356	357	\N	t	1	\N	{"score": 0.0}	\N	\N			
179	1	\N	358	359	\N	t	1	\N	{"score": 0.0}	\N	\N			
180	1	\N	360	361	\N	t	1	\N	{"score": 0.0}	\N	\N			
181	1	\N	362	363	\N	t	1	\N	{"score": 0.0}	\N	\N			
182	1	\N	364	365	\N	t	1	\N	{"score": 0.0}	\N	\N			
183	1	\N	366	367	\N	t	1	\N	{"score": 0.0}	\N	\N			
184	1	\N	368	369	\N	t	1	\N	{"score": 0.0}	\N	\N			
185	1	\N	370	371	\N	t	1	\N	{"score": 0.0}	\N	\N			
186	1	\N	372	373	\N	t	1	\N	{"score": 0.0}	\N	\N			
187	1	\N	374	375	\N	t	1	\N	{"score": 0.0}	\N	\N			
188	1	\N	376	377	\N	t	1	\N	{"score": 0.0}	\N	\N			
189	1	\N	378	379	\N	t	1	\N	{"score": 0.0}	\N	\N			
190	1	\N	380	381	\N	t	1	\N	{"score": 0.0}	\N	\N			
191	1	\N	382	383	\N	t	1	\N	{"score": 0.0}	\N	\N			
192	1	\N	384	385	\N	t	1	\N	{"score": 0.0}	\N	\N			
193	1	\N	386	387	\N	t	1	\N	{"score": 0.0}	\N	\N			
194	1	\N	388	389	\N	t	1	\N	{"score": 0.0}	\N	\N			
195	1	\N	390	391	\N	t	1	\N	{"score": 0.0}	\N	\N			
196	1	\N	392	393	\N	t	1	\N	{"score": 0.0}	\N	\N			
197	1	\N	394	395	\N	t	1	\N	{"score": 0.0}	\N	\N			
198	1	\N	396	397	\N	t	1	\N	{"score": 0.0}	\N	\N			
199	1	\N	398	399	\N	t	1	\N	{"score": 0.0}	\N	\N			
200	1	\N	400	401	\N	t	1	\N	{"score": 0.0}	\N	\N			
201	1	\N	402	403	\N	t	1	\N	{"score": 0.0}	\N	\N			
202	1	\N	404	405	\N	t	1	\N	{"score": 0.0}	\N	\N			
203	1	\N	406	407	\N	t	1	\N	{"score": 0.0}	\N	\N			
204	1	\N	408	409	\N	t	1	\N	{"score": 0.0}	\N	\N			
205	1	\N	410	411	\N	t	1	\N	{"score": 0.0}	\N	\N			
206	1	\N	412	413	\N	t	1	\N	{"score": 0.0}	\N	\N			
207	1	\N	414	415	\N	t	1	\N	{"score": 0.0}	\N	\N			
208	1	\N	416	417	\N	t	1	\N	{"score": 0.0}	\N	\N			
209	1	\N	418	419	\N	t	1	\N	{"score": 0.0}	\N	\N			
210	1	\N	420	421	\N	t	1	\N	{"score": 0.0}	\N	\N			
211	1	\N	422	423	\N	t	1	\N	{"score": 0.0}	\N	\N			
212	1	\N	424	425	\N	t	1	\N	{"score": 0.0}	\N	\N			
213	1	\N	426	427	\N	t	1	\N	{"score": 0.0}	\N	\N			
214	1	\N	428	429	\N	t	1	\N	{"score": 0.0}	\N	\N			
215	1	\N	430	431	\N	t	1	\N	{"score": 0.0}	\N	\N			
216	1	\N	432	433	\N	t	1	\N	{"score": 0.0}	\N	\N			
217	1	\N	434	435	\N	t	1	\N	{"score": 0.0}	\N	\N			
218	1	\N	436	437	\N	t	1	\N	{"score": 0.0}	\N	\N			
219	1	\N	438	439	\N	t	1	\N	{"score": 0.0}	\N	\N			
220	1	\N	440	441	\N	t	1	\N	{"score": 0.0}	\N	\N			
221	1	\N	442	443	\N	t	1	\N	{"score": 0.0}	\N	\N			
222	1	\N	444	445	\N	t	1	\N	{"score": 0.0}	\N	\N			
223	1	\N	446	447	\N	t	1	\N	{"score": 0.0}	\N	\N			
224	1	\N	448	449	\N	t	1	\N	{"score": 0.0}	\N	\N			
225	1	\N	450	451	\N	t	1	\N	{"score": 0.0}	\N	\N			
226	1	\N	452	453	\N	t	1	\N	{"score": 0.0}	\N	\N			
227	1	\N	454	455	\N	t	1	\N	{"score": 0.0}	\N	\N			
228	1	\N	456	457	\N	t	1	\N	{"score": 0.0}	\N	\N			
229	1	\N	458	459	\N	t	1	\N	{"score": 0.0}	\N	\N			
230	1	\N	460	461	\N	t	1	\N	{"score": 0.0}	\N	\N			
231	1	\N	462	463	\N	t	1	\N	{"score": 0.0}	\N	\N			
232	1	\N	464	465	\N	t	1	\N	{"score": 0.0}	\N	\N			
233	1	\N	466	467	\N	t	1	\N	{"score": 0.0}	\N	\N			
234	1	\N	468	469	\N	t	1	\N	{"score": 0.0}	\N	\N			
235	1	\N	470	471	\N	t	1	\N	{"score": 0.0}	\N	\N			
236	1	\N	472	473	\N	t	1	\N	{"score": 0.0}	\N	\N			
237	1	\N	474	475	\N	t	1	\N	{"score": 0.0}	\N	\N			
238	1	\N	476	477	\N	t	1	\N	{"score": 0.0}	\N	\N			
239	1	\N	478	479	\N	t	1	\N	{"score": 0.0}	\N	\N			
240	1	\N	480	481	\N	t	1	\N	{"score": 0.0}	\N	\N			
241	1	\N	482	483	\N	t	1	\N	{"score": 0.0}	\N	\N			
242	1	\N	484	485	\N	t	1	\N	{"score": 0.0}	\N	\N			
243	1	\N	486	487	\N	t	1	\N	{"score": 0.0}	\N	\N			
244	1	\N	488	489	\N	t	1	\N	{"score": 0.0}	\N	\N			
245	1	\N	490	491	\N	t	1	\N	{"score": 0.0}	\N	\N			
246	1	\N	492	493	\N	t	1	\N	{"score": 0.0}	\N	\N			
247	1	\N	494	495	\N	t	1	\N	{"score": 0.0}	\N	\N			
248	1	\N	496	497	\N	t	1	\N	{"score": 0.0}	\N	\N			
249	1	\N	498	499	\N	t	1	\N	{"score": 0.0}	\N	\N			
250	1	\N	500	501	\N	t	1	\N	{"score": 0.0}	\N	\N			
251	1	\N	502	503	\N	t	1	\N	{"score": 0.0}	\N	\N			
252	1	\N	504	505	\N	t	1	\N	{"score": 0.0}	\N	\N			
253	1	\N	506	507	\N	t	1	\N	{"score": 0.0}	\N	\N			
254	1	\N	508	509	\N	t	1	\N	{"score": 0.0}	\N	\N			
255	1	\N	510	511	\N	t	1	\N	{"score": 0.0}	\N	\N			
256	1	\N	512	513	\N	t	1	\N	{"score": 0.0}	\N	\N			
257	1	\N	514	515	\N	t	1	\N	{"score": 0.0}	\N	\N			
258	1	\N	516	517	\N	t	1	\N	{"score": 0.0}	\N	\N			
259	1	\N	518	519	\N	t	1	\N	{"score": 0.0}	\N	\N			
260	1	\N	520	521	\N	t	1	\N	{"score": 0.0}	\N	\N			
261	1	\N	522	523	\N	t	1	\N	{"score": 0.0}	\N	\N			
262	1	\N	524	525	\N	t	1	\N	{"score": 0.0}	\N	\N			
263	1	\N	526	527	\N	t	1	\N	{"score": 0.0}	\N	\N			
264	1	\N	528	529	\N	t	1	\N	{"score": 0.0}	\N	\N			
265	1	\N	530	531	\N	t	1	\N	{"score": 0.0}	\N	\N			
266	1	\N	532	533	\N	t	1	\N	{"score": 0.0}	\N	\N			
\.


--
-- Data for Name: uploads; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.uploads (id, user_id, filename, peak_list_file_names, analysis_software, provider, audits, samples, analyses, protocol, bib, spectra_formats, upload_time, default_pdb, contains_crosslinks, upload_error, error_type, upload_warnings, origin, random_id, deleted, ident_count, ident_file_size, zipped_peak_list_file_size) FROM stdin;
1	0	NPC.csv	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	-	0	f	\N	\N	\N
\.


--
-- Data for Name: user_in_group; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.user_in_group (user_id, group_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: xiadmin
--

COPY public.users (user_name, password, email, max_aas, max_spectra, gdpr_token, id, ptoken, hidden, ptoken_timestamp, gdpr_timestamp) FROM stdin;
\.


--
-- Name: uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xiadmin
--

SELECT pg_catalog.setval('public.uploads_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xiadmin
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: layouts layouts_pkey; Type: CONSTRAINT; Schema: public; Owner: xiadmin
--

ALTER TABLE ONLY public.layouts
    ADD CONSTRAINT layouts_pkey PRIMARY KEY (search_id, user_id, "time");


--
-- Name: uploads uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: xiadmin
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT uploads_pkey PRIMARY KEY (id);


--
-- Name: peptide_evidences_upload_id_idx; Type: INDEX; Schema: public; Owner: xiadmin
--

CREATE INDEX peptide_evidences_upload_id_idx ON public.peptide_evidences USING btree (upload_id);


--
-- Name: peptides_upload_id_idx; Type: INDEX; Schema: public; Owner: xiadmin
--

CREATE INDEX peptides_upload_id_idx ON public.peptides USING btree (upload_id);


--
-- Name: spectra_upload_id_idx; Type: INDEX; Schema: public; Owner: xiadmin
--

CREATE INDEX spectra_upload_id_idx ON public.spectra USING btree (upload_id);


--
-- Name: spectrum_identifications_upload_id_idx; Type: INDEX; Schema: public; Owner: xiadmin
--

CREATE INDEX spectrum_identifications_upload_id_idx ON public.spectrum_identifications USING btree (upload_id);


--
-- PostgreSQL database dump complete
--

