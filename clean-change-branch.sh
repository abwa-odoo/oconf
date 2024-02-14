#! /bin/bash
# Switch odoo version
cd /home/abwa/ODOO/src/enterprise && git checkout $1 && git pull && find . -name \*.pyc -delete && git clean -df
cd /home/abwa/ODOO/src/design-themes && git checkout $1 && git pull && find . -name \*.pyc -delete && git clean -df
cd /home/abwa/ODOO/src/odoo && git checkout $1 && git pull && find . -name \*.pyc -delete && git clean -df

