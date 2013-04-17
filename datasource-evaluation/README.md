datasource-list
================

IEM Datasource Evaluation Script

- Run `./datasource-list.sh` to execute the Datasource Evaluation.
- If the script finds any duplicated datasource, an e-mail will be sent to the recipients defined in the "mail" file. If there is no problem with the datasources, no output will be given.

# Installation:
- With the holmes-admin configured, no aditional customization is needed beside the customization of the "mail" file and reference inside the script.
- If the script is executed as a cronjob, all the files it creates are generated inside the home folder of the user who owns the crontab. In that case, the "mail" file must be in the home folder as well.
