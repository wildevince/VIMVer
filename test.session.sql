--  phpMyAdmin MySQL-Dump
--  version 2.2.6
--  http://phpwizard.net/phpMyAdmin/
--  http://www.phpmyadmin.net/ (download page)
--  Host: localhost
--  Generation Time: Nov 04, 2004 at 09:16 AM
--  Server version: 3.23.52
--  PHP Version: 4.1.2
--  [bibref]
CREATE TABLE Biblio_Struct (
  Id_Biblio int not null auto_increment default 1 PRIMARY KEY,
  PubMed text NOT NULL default '',
  Title longtext NOT NULL,
  Auteur longtext NOT NULL,
  Journal longtext NOT NULL,
  Date longtext NOT NULL,
  CONSTRAINT PubMed_id UNIQUE (PUbMEd)
);
--  2
--  ?
CREATE TABLE CAZyModO (
  URL_family varchar(5) NOT NULL default '',
  URL_title varchar(20) NOT NULL default '',
  URL_body text NOT NULL,
  URL_relative tinytext NOT NULL,
  URL_note tinytext NOT NULL,
  Modified date NOT NULL default '0000-00-00',
  PRIMARY KEY (URL_family, URL_title)
);
--  2
--  [input]
CREATE TABLE CAZy_DB (
  DB_ac int not null auto_increment default 1,
  -- id
  Protein varchar(100) default NULL,
  DB_nom varchar(20) default NULL,
  Organism varchar(100) default NULL,
  abr varchar(30) default NULL,
  Tax_id int(11) default NULL,
  -- FK
  EC varchar(100) default NULL,
  -- FK
  _3D_status varchar(10) default NULL,
  Length int(11) default NULL,
  Sequence text,
  DB_note text,
  Created date default NULL,
  Modified date default NULL,
  PP_status char(3) NOT NULL default 'no',
  Lib_sort text,
  PRIMARY KEY (DB_ac),
  FOREIGN KEY (Tax_id) REFERENCES Organism(Tax_id),
  FOREIGN KEY (EC) REFERENCES EC_num(EC) -- CAUTION !!! crossing foreign keys
);
--  647
-- CAZy_DB with Genbank accesion protein and nucleic
CREATE TABLE CAZy_GB_GP (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  GP_ac varchar(15) NOT NULL default '',
  GB_ac varchar(15) NOT NULL default '',
  GP_gi varchar(15) default NULL,
  GP_gene varchar(100) default NULL,
  GP_genomic varchar(100) default NULL,
  GP_begin int(11) NOT NULL default '0',
  GP_end int(11) NOT NULL default '0',
  GP_note text,
  PRIMARY KEY (DB_ac, GP_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac)
);
--  644
-- CAZy_DB with attached PDB
CREATE TABLE CAZy_PDB (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  PDB_id varchar(10) NOT NULL default '',
  PDB_chain char(3) NOT NULL default '',
  PDB_begin int(11) NOT NULL default '0',
  PDB_end int(11) NOT NULL default '0',
  PDB_note text,
  PDB_bornModo varchar(10) default NULL,
  PRIMARY KEY (PDB_id, PDB_chain),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac)
);
--  68
-- CAZy_DB identified as polyprotein
CREATE TABLE CAZy_PP (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  PP_ac int(3) NOT NULL default '0',
  PP_gi varchar(15) default NULL,
  PP_gene varchar(100) default NULL,
  PP_begin int(11) NOT NULL default '0',
  PP_end int(11) NOT NULL default '0',
  PP_note text,
  PP_diff char(3) default 'no',
  PRIMARY KEY (DB_ac, PP_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) --  FOREIGN KEY PP_ac (PP_ac)
);
--  773
-- CAZy_DB identified as single protein
CREATE TABLE CAZy_SP (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  SP_ac varchar(100) NOT NULL default '',
  SP_id varchar(15) NOT NULL default '',
  SP_gene varchar(100) default NULL,
  SP_begin int(11) NOT NULL default '0',
  SP_end int(11) NOT NULL default '0',
  SP_note text,
  PRIMARY KEY (SP_ac, SP_id),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) --  FOREIGN KEY SP_ac (SP_ac),
  --  FOREIGN KEY SP_begin (SP_begin),
  --  FOREIGN KEY SP_end (SP_end)
);
--  4
CREATE TABLE EC_num (
  EC varchar(16) NOT NULL default '',
  -- id
  EC_name longtext NOT NULL,
  EC_otherName longtext,
  EC_reaction longtext,
  EC_comment longtext,
  PRIMARY KEY (EC)
);
--  1
CREATE TABLE Cz_EC (
  DB_ac int(10) NOT NULL default '0',
  -- FK
  EC varchar(16) NOT NULL default '',
  -- FK
  PRIMARY KEY (DB_ac, EC),
  FOREIGN KEY (EC) REFERENCES EC_num(EC)
);
--  2
--  [bibref]
CREATE TABLE Fam_biblio (
  Family varchar(5) NOT NULL default '',
  -- FK
  Id_Biblio int(11) NOT NULL default '0',
  -- id
  PRIMARY KEY (Family, Id_Biblio)
);
--  1
-- composition of modules [data]
CREATE TABLE ModO_Composition (
  DB_ac int(11) NOT NULL default 0,
  -- FK
  Mod_num int(11) NOT NULL AUTO_INCREMENT default 1,
  -- id
  Family varchar(10) NOT NULL default '',
  -- FK
  Subf varchar(10) default NULL,
  PRIMARY KEY (DB_ac, Mod_num),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac),
  FOREIGN KEY (Family) REFERENCES ModO_Families(Family) -- FOREIGN KEY (Mod_num) REFERENCES (Mod_num)
);
--  2797
-- information on modules [bibref]
CREATE TABLE ModO_CrossRefs (
  Family varchar(10) NOT NULL default '',
  -- FK
  Link varchar(100) NOT NULL default '',
  -- id?
  URL_base varchar(150) NOT NULL default '',
  URL_string varchar(20) default NULL,
  Ref_note tinytext,
  PRIMARY KEY (Family, Link),
  FOREIGN KEY (Family) REFERENCES ModO_Families(Family)
);
--  77
-- families of modules [data]
CREATE TABLE ModO_Families (
  Family varchar(10) UNIQUE NOT NULL default '',
  -- id
  Family_Name varchar(40) default '',
  Family_Activity text,
  Family_Taxo text,
  Clan varchar(10) default NULL,
  Family_note text,
  Family_Private_note text,
  Fold varchar(20) NOT NULL default '',
  ModoS_uniqfct char(3) NOT NULL default 'no',
  ModoS_Activity text,
  ModoS_Description text,
  ModoS_Fold text,
  ModoS_note text,
  ModoS_Private_note text,
  web_descript varchar(40) default NULL,
  web_status int(1) default NULL,
  PRIMARY KEY (Family)
);
--  514
-- boundaries of each module [data]
CREATE TABLE ModO_Limits (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  Mod_num int(11) NOT NULL default '0',
  -- FK
  Mod_begin int(11) NOT NULL default '0',
  Mod_end int(11) NOT NULL default '0',
  PRIMARY KEY (DB_ac, Mod_num, Mod_begin),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac),
  FOREIGN KEY (Mod_num) REFERENCES ModO_Composition(Mod_num) -- FOREIGN KEY Mod_begin (Mod_begin),
  -- FOREIGN KEY Mod_end (Mod_end)
);
--  2829
--  [data]
CREATE TABLE Motifs (
  motifs_ac int not null auto_increment default 1,
  -- id
  motifs_name varchar(50) NOT NULL default '',
  motifs_activity varchar(50) NOT NULL default '',
  motifs_classification varchar(80) default NULL,
  motifs_form text,
  motifs_note text,
  PRIMARY KEY (motifs_ac)
);
--  91
--  [data]
CREATE TABLE Organism (
  Tax_id varchar(10) UNIQUE NOT NULL default '',
  -- id
  Name text NOT NULL,
  Categorie varchar(30) default NULL,
  Classe longtext,
  Ordre varchar(30) default NULL,
  Fam varchar(30) default NULL,
  -- FK
  SsFam varchar(30) default NULL,
  Genre varchar(30) default NULL,
  Note_org longtext,
  PRIMARY KEY (Tax_id),
  -- UNIQUE KEY Tax_id_2 (Tax_id),
  FOREIGN KEY (Family) REFERENCES ModO_Families(Family)
);
--  166
--  complementary [annotation]
CREATE TABLE Prot_Infos (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  INFO_indice int(4) NOT NULL default '0',
  INFO_ac int(11) NOT NULL default '0',
  INFO_Nature varchar(50) default NULL,
  INFO longtext,
  INFO_pmid int(25) default '0',
  PRIMARY KEY (DB_ac, INFO_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) -- FOREIGN KEY INFO_ac (INFO_ac)
);
--  159
--  protein motif [annotation]
CREATE TABLE Prot_MOTIF (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  MOTIF_indice int(4) NOT NULL default '0',
  MOTIF_ac int(11) NOT NULL default '0',
  -- FK
  MOTIF_name varchar(50) default NULL,
  MOTIF_begin int(11) default NULL,
  MOTIF_end int(11) default NULL,
  MOTIF varchar(200) default NULL,
  MOTIF_activity varchar(50) default NULL,
  MOTIF_class text,
  MOTIF_note text,
  MOTIF_ref text,
  MOTIF_pmid int(25) default NULL,
  PRIMARY KEY (DB_ac, MOTIF_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac),
  FOREIGN KEY (MOTIF_ac) REFERENCES Motifs(motifs_ac)
);
--  908
-- important protein mutation [annotation]
CREATE TABLE Prot_MUT (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  MUT_indice int(4) NOT NULL default '0',
  MUT_ac int(11) NOT NULL default '0',
  MUT varchar(120) default NULL,
  MUT_note text,
  MUT_ref text,
  MUT_pmid int(25) default NULL,
  PRIMARY KEY (DB_ac, MUT_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) -- FOREIGN KEY MUT_ac (MUT_ac)
);
--  9
-- Region (Desordonnée? TransMembranR? ... osef!) [annotation]
CREATE TABLE Prot_REG (
  DB_ac int(11) NOT NULL default '0',
  REG_indice int(4) NOT NULL default '0',
  REG_ac int(11) NOT NULL default '0',
  REG_name varchar(70) default NULL,
  REG_begin int(11) default NULL,
  REG_end int(11) default NULL,
  REG_note text,
  REG_ref text,
  REG_pmid int(25) default NULL,
  PRIMARY KEY (DB_ac, REG_ac, DB_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) -- FOREIGN KEY REG_ac (REG_ac)
);
--  42
-- Region Interraction [annotation]
CREATE TABLE Prot_RI (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  RI_indice int(4) NOT NULL default '0',
  RI_ac int(11) NOT NULL default '0',
  RI_name varchar(70) default NULL,
  RI_begin int(11) default NULL,
  RI_end int(11) default NULL,
  RI_no_limit varchar(70) default NULL,
  RI_note text,
  RI_ref text,
  RI_pmid int(25) default NULL,
  PRIMARY KEY (DB_ac, RI_ac, DB_ac),
  FOREIGN KEY (DB_ac) REFERENCES CAZy_DB(DB_ac) -- FOREIGN KEY RI_ac (RI_ac)
);
--  112
--  [bibref]
CREATE TABLE Prot_biblio (
  DB_ac int(11) NOT NULL default '0',
  -- FK
  Id_Biblio int(11) NOT NULL default '0',
  -- id
  PRIMARY KEY (DB_ac, Id_Biblio)
);
--  1