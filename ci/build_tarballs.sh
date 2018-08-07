#!/bin/sh

echo "EXECUTING: Build Tarballs"
echo

cd ${WORKSPACE}

. ${WORKSPACE}/pgadmin-venv/bin/activate

SPHINX_VER=""
if [ "${PYTHON_VERSION}" = "2.6" -o "${PYTHON_VERSION}" = "3.3" ]; then
    SPHINX_VER="==1.4.9"
fi

${WORKSPACE}/pgadmin-venv/bin/pip install Sphinx${SPHINX_VER} || { echo 'ERROR: Failed to install Sphinx to build the tarballs.' ; exit 1; }
cd ${WORKSPACE}/
make src || { echo 'ERROR: Failed to build the tarballs.' ; exit 1; }