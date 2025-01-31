default:
  {{just_executable()}} -l

sync:
  rye sync
install PKG:
  rye install $PKG
add PKG:
  rye add $PKG
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
