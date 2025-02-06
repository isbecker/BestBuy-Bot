default:
  {{just_executable()}} -l

sync:
  rye sync
install pkg:
  rye install {{pkg}}
add pkg:
  rye add {{pkg}}
upgrade pkg:
  rye sync --update {{pkg}}
remove pkg:
  rye remove {{pkg}}
up:
  rye sync --update-all
run:
  rye run main
fmt:
  rye fmt
lint:
  rye lint --fix
style:
  {{just_executable()}} fmt lint
test:
  rye test
check:
  {{just_executable()}} fmt lint test

alias s := sync
alias f := style
alias c := check
