# Path to Oh My Fish install.
set -q XDG_DATA_HOME
  and set -gx OMF_PATH "$XDG_DATA_HOME/omf"
  or set -gx OMF_PATH "$HOME/.local/share/omf"

# Command Alis
alias cl='clear'

# Navigation Aliases
alias ..='cd ..'
alias ...='cd ../..'

# File listing (changing ls -> exa)
alias ls='exa -a --color=always --group-directories-first'
alias la='exa -al --color=always --group-directories-first'
alias ll='exa -l --color=always --group-directories-first'
alias lt='exa -aT --color=always --group-directories-first'

# Load Oh My Fish configuration.
source $OMF_PATH/init.fish

# pyenv
# set --export PYENV_ROOT $HOME/.pyenv
# export PATH "$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init --path)"
# eval "$(pyenv virtualenv-init -)"

# ODOO funcs

alias kill_tcp='fuser -k 8069/tcp'

function refresh_db --description "Refreshes selected database refresh_db <db_name>"
#	psql $argv[1] < ~/ODOO/scripts/clean_database_v12.sql
	odev clean $argv[1]
end

function setup_db
	dropdb $argv[1]
	echo "DROPPED "$argv[1]
	createdb $argv[1]
	echo "CREATED "$argv[1]
	extract_db $argv[1] $argv[2]
	echo "EXTRACTED "$argv[2]
	psql $argv[1] < ~/ODOO/src/psae-data/$argv[1]/dump.sql
	echo "SET UP "$argv[1]
	rm -r ~/ODOO/src/psae-data/filestore/$argv[1]
	cp -r ~/ODOO/src/psae-data/$argv[1]/filestore ~/ODOO/src/psae-data/filestore/$argv[1]
	refresh_db $argv[1] 
	echo "DONE SETTING UP "$argv[1]
end

function extract_db
	rm -r ~/ODOO/src/psae-data/$argv[1]
	unzip $argv[2] -d ~/ODOO/src/psae-data/$argv[1]
	mv $argv[2] ~/ODOO/src/psae-data/dump/
end

function pull_odoo_git -d "Fetch ODOO Git"
    git clone git@github.com:odoo/odoo.git
    git clone git@github.com:odoo/enterprise.git
    git clone git@github.com:odoo/design-themes.git
    return
end

function switch_branch -d "Switch ODOO Branch"
    cd /home/abwa/ODOO/$argv[(count $argv)]/enterprise && git checkout $argv[(count $argv)] && git pull && find . -name \*.pyc -delete && git clean -df
    cd /home/abwa/ODOO/$argv[(count $argv)]/design-themes && git checkout $argv[(count $argv)] && git pull && find . -name \*.pyc -delete && git clean -df
    cd /home/abwa/ODOO/$argv[(count $argv)]/odoo && git checkout $argv[(count $argv)] && git pull && find . -name \*.pyc -delete && git clean -df
    return
end

function obranch -d "Create ODOO Branch"
    command mkdir $argv
    if test $status = 0
        switch $argv[(count $argv)]
            case '-*'

            case '*'
                cd $argv[(count $argv)]
                pull_odoo_git
                switch_branch $argv[(count $argv)]
                return
        end
    end
end
