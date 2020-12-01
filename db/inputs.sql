/* password for all is: welcome */
INSERT INTO Users(email, name, hash, salt) VALUES
   ('mike@knights.ucf.edu', 'Michael S', 'pbkdf2:sha256:150000$PWArbloj$32eada7dc35d8c8aa5a0908c8ed50ab2b0e8261ca10432ae6389036b7f2d62af', 'mMvzfT1_s35JRa4qKMzXOtEjoxRD5I9HAYu7v2cHo6k'),
   ('ash@ucla.edu', 'Ash', 'pbkdf2:sha256:150000$EoNsz8Ac$bc35a9823345ab62ca21c34e0322064ca1e0c9824633fdbbd0fb9a260efd84ea', 'VUwAeBx6qoJR9S7bcr1Z7wR8BntUWpKfeufRWhbC5dE'),
   ('brent@hunters.edu', 'Brent', 'pbkdf2:sha256:150000$96bPMIB3$8df9b8e23ab999b9469d0a5df213b24c4f4535adff95d7327645c6520117a802', 'KDR16a2Nq3YdtX3VzN1wrH3X0F2agCPDJbJjD5g_-78')
;

INSERT INTO Managers(uid) VALUES
	(1)
;

INSERT INTO Entities(eid, name, location, title, picture_filename) VALUES
	(1, 'Dr. Weiss', 'West Office', 'DVM', 'redhead_vet.jpg'),
	(2, 'Dr. Jonas', 'South Office', 'Doctor of Internal Medicine', 'blueeyes_doctor.jpeg'),
	(3, 'Dr. Kane', 'North Office', 'Doctor of Dentistry', 'blonde_dentist.jpg')
;

INSERT INTO Appointments(uid, eid, description, datetime_start, datetime_end) VALUES
	(1, 1, 'Dental Checkup', 		'20210705T133701',	'20210705T222222'),
	(1, 1, 'Dental Followup', 		'20210707T133701',	'20210705T222223'),
	(2, 1, 'Comprehensive Exam', 		'20210707T133702',	'20210705T222224'),
	(3, 2, 'Colonoscopy Appointment', 	'20210707T133703',	'20210705T222225'),
	(3, 3, 'Numbing Prescription', 		'20210709T133703',	'20210705T222226')
;
