# commands
alias title='clear; source ~/.bashrc'
alias pdfconvert='libreoffice --headless --convert-to pdf' # file
alias pdfcompile='pandoc --pdf-engine=pdflatex -f markdown -o' # out.pdf src.md

# machines bare repository
alias m='git --git-dir=$HOME/.machines.git --work-tree=$HOME'

# common mistypes
alias sl='ls'

# better utilities
alias mv="mv -iv"
alias cp="cp -ivr"
alias rm="rm -v"
alias mkdir="mkdir -vp"
alias rmdir="rmdir -v"

# color
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias tree='tree --dirsfirst -C'

# shell integration for q -s
q() { Q_EXIT=$? Q_CMD=$(fc -ln -1) command q "$@"; }
