#!/usr/bin/env bash

# Source the common helpers script.
source scripts/common.bash

printf "${yellow}"
print_banner "Python 3"
printf "${normal}\n"
# add -s for verbose output

opt_venv='--user'
if [ ! -z ${VIRTUAL_ENV} ]; then
    message_std "Virtual environment ${green}detected${normal}."
    opt_venv=''
else
    message_std "Virtual environment ${red}not detected${normal}."
fi
printf "\n"

execute_command_checked "./exec-reqs-install.sh > /dev/null 2>&1"

# clean up any precompiled code before the tests are executd
find . -name "__pycache__" -exec rm -rf {} \; >& /dev/null
find . -name "*.py?" -exec rm {} \;           >& /dev/null

options=(
    --cov-report=term
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov=configparserenhanced
    )

python3 -m pytest ${options[@]}
err=$?

printf "\n"
if [ $err != 0 ]; then
    printf "${red}"
    print_banner "TESTING FAILED"
    printf "${normal}"
    printf "\n"
    exit $err
fi

# Check installation
pwd
execute_command_checked "python3 -m pip install ${opt_venv} . >& _test-install.log"

# Run the Example(s)
execute_command_checked "pushd examples"
execute_command_checked "python3 ConfigParserEnhanced-example-01.py >& _test-example-01.log"
execute_command_checked "popd"

# Check uninstaller
execute_command_checked "python3 -m pip uninstall -y configparserenhanced >& _test-uninstall.log"


# Clean up generated bytecode
if [ $err -eq 0 ]; then
    execute_command "find . -name '__pycache__' -exec rm -rf {} \;          > /dev/null 2>&1"
    execute_command "find . -name '*.py?' -exec rm {} \;                    > /dev/null 2>&1"
    execute_command "find . -depth 2 -name '_example-*.ini' -exec rm {} \;  > /dev/null 2>&1"
    execute_command "find . -maxdepth 2 -name '_test-*.log' -exec rm {} \;  > /dev/null 2>&1"
    execute_command "find . -maxdepth 1 -name '___*.ini' -exec rm {} \;     > /dev/null 2>&1"
fi

printf "\n"
printf "${green}"
print_banner "TESTING PASSED"
printf "${normal}"
printf "\n"
