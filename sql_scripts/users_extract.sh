#!/usr/bin/env bash
sqlplus -s /nolog  <<-EOD1
connect micah_chartier/'16sharpCaps2!'@PROD
set trimout on
set trimspool on
set feedback off
set linesize 255
set heading off
rem possibly or probably some other set as well
spool users_export.csv
select 'user_id', 'login_id', 'password', 'first_name', 'last_name', 'email', 'status' from sys.dual;
SELECT spriden_id AS user_id,
	-- The line below is used to pull the username for the user from either their employee email or their student email.
    LOWER(SUBSTR(NVL(UNC_EMAIL.GOREMAL_EMAIL_ADDRESS, UNCS_EMAIL.GOREMAL_EMAIL_ADDRESS), 1, INSTR(NVL(UNC_EMAIL.GOREMAL_EMAIL_ADDRESS, UNCS_EMAIL.GOREMAL_EMAIL_ADDRESS), '@') - 1)) AS login_id,
    '' AS "password",
    NVL(spbpers_pref_first_name, spriden_first_name) AS first_name,
    spriden_last_name AS last_name,
    NVL(UNC_EMAIL.GOREMAL_EMAIL_ADDRESS, UNCS_EMAIL.GOREMAL_EMAIL_ADDRESS) AS email,
    'active' AS status
FROM spriden
INNER JOIN spbpers
    ON spriden_pidm = spbpers_pidm
LEFT OUTER JOIN GENERAL.GOREMAL UNC_EMAIL -- this pulls employee email addresses
    ON UNC_EMAIL.GOREMAL_PIDM           = spriden_PIDM
    AND UNC_EMAIL.GOREMAL_PREFERRED_IND = 'Y'
    AND UNC_EMAIL.GOREMAL_STATUS_IND    = 'A'
    AND UNC_EMAIL.GOREMAL_EMAL_CODE     = 'UNC'
LEFT OUTER JOIN GENERAL.GOREMAL UNCS_EMAIL -- this pulls student email addresses
    ON UNCS_EMAIL.GOREMAL_PIDM = spriden_PIDM
    AND UNCS_EMAIL.GOREMAL_EMAL_CODE = 'UNCS'
    AND UNCS_EMAIL.GOREMAL_STATUS_IND = 'A'
WHERE spriden_change_ind IS NULL
AND NVL(UNC_EMAIL.GOREMAL_EMAIL_ADDRESS, UNCS_EMAIL.GOREMAL_EMAIL_ADDRESS) IS NOT NULL
AND (spriden_pidm IN -- this pulls active employees
       (SELECT PEBEMPL_PIDM ACTIVE_PIDM FROM PEBEMPL WHERE PEBEMPL_EMPL_STATUS = 'A'
        )
    OR spriden_pidm IN -- this pulls instructors who are not employees
       (SELECT SIBINST_PIDM FROM SIBINST WHERE SIBINST_FCST_CODE = 'AC'
        )
    OR spriden_pidm IN -- this pulls all students listed as active for the current term going back to the last active term
        (SELECT SGBSTDN_PIDM
        FROM SATURN.SGBSTDN OUTR
        WHERE SGBSTDN_STST_CODE = 'AS'
	    AND SGBSTDN_TERM_CODE_EFF =
            (SELECT MAX(INNR.SGBSTDN_TERM_CODE_EFF)
            FROM SATURN.SGBSTDN INNR
            WHERE INNR.SGBSTDN_PIDM = OUTR.SGBSTDN_PIDM
            AND INNR.SGBSTDN_TERM_CODE_EFF <=
                (SELECT stvterm_code
                FROM stvterm
				-- Using sysdate plus 20 to remove the time between terms and to start the large import for a new term 20 days before the start of the term.
                WHERE sysdate + 20 BETWEEN stvterm_start_date AND stvterm_end_date
                )
            )
        )
	) ;
spool off
exit
EOD1

