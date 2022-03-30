ALTER TABLE IF EXISTS users RENAME TO useraccount;
alter table useraccount drop column max_aas;
alter table useraccount drop column max_spectra;
alter table useraccount drop column hidden;
drop table user_in_group;
--add index to useraccount

**remove uploads where deleted = true

ALTER TABLE IF EXISTS uploads RENAME TO upload;
ALTER COLUMN id [SET DATA] TYPE uuid;