# My custom developer theme

prompt_indicator() {
   echo '%B»%b'
}

current_time() {
   echo $(date +%r)
}

PROMPT='%{$FG[250]%}[$(current_time)][%m][%3~]%{$reset_color%}
%{$fg[green]%}%n%{$reset_color%}$(git_prompt_info) $(prompt_indicator) '

ZSH_THEME_GIT_PROMPT_PREFIX=" (%{$FG[220]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%})"
ZSH_THEME_GIT_PROMPT_DIRTY="*"
ZSH_THEME_GIT_PROMPT_CLEAN=""

return_code="%(?..%{$fg[red]%}%? ↵%{$reset_color%})"
RPROMPT='${return_code}$(git_prompt_status)%{$reset_color%}'

ZSH_THEME_GIT_PROMPT_ADDED="%{$fg[green]%} ✚"
ZSH_THEME_GIT_PROMPT_MODIFIED="%{$fg[blue]%} ✹"
ZSH_THEME_GIT_PROMPT_DELETED="%{$fg[red]%} ✖"
ZSH_THEME_GIT_PROMPT_RENAMED="%{$fg[magenta]%} ➜"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg[yellow]%} ═"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg[cyan]%} ✭"
