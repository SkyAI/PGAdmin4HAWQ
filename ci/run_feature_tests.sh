#!/bin/sh

echo "EXECUTING: Feature tests"
echo

echo "Starting virtual frame buffer..."
echo

Xvfb -ac :99 -screen 0 1280x1024x16 &
FB_PID=$!
export DISPLAY=:99

echo "Creating Python ${PYTHON_VERSION} virtual environment..."
echo

cd ${WORKSPACE}/

PYTHON_SUFFIX=""

if [[ "${PYTHON_VERSION}" == 3* ]]; then
    PYTHON_SUFFIX="3"
fi

if [ "${PYTHON_VERSION}" == 2.6 -o "${PYTHON_VERSION}" == 3.3 ]; then
    /usr/bin/virtualenv --no-wheel -p /usr/local/python-${PYTHON_VERSION}/bin/python${PYTHON_SUFFIX} ${WORKSPACE}/pgadmin-venv || { echo 'ERROR: Failed to create the Python virtual environment.' ; exit 1; }
    . ${WORKSPACE}/pgadmin-venv/bin/activate || { echo 'ERROR: Failed to activate the Python virtual environment.' ; exit 1; }
    ${WORKSPACE}/pgadmin-venv/bin/pip install wheel==0.29.0 || { echo 'ERROR: Failed to install wheel 0.29.0.' ; exit 1; }
else
    /usr/bin/virtualenv -p /usr/local/python-${PYTHON_VERSION}/bin/python${PYTHON_SUFFIX} ${WORKSPACE}/pgadmin-venv || { echo 'ERROR: Failed to create the Python virtual environment.' ; exit 1; }
    . ${WORKSPACE}/pgadmin-venv/bin/activate || { echo 'ERROR: Failed to activate the Python virtual environment.' ; exit 1; }
fi

${WORKSPACE}/pgadmin-venv/bin/pip install -r requirements.txt || { echo 'ERROR: Failed to install the application requirements.' ; exit 1; }
${WORKSPACE}/pgadmin-venv/bin/pip install -r web/regression/requirements.txt || { echo 'ERROR: Failed to install the regression test requirements.' ; exit 1; }

cd web
/usr/bin/yarn install || { echo 'ERROR: Failed to install the required Javascript modules.' ; exit 1; }
/usr/bin/yarn run bundle || { echo 'ERROR: Failed to bundle the Javascript code.' ; exit 1; }
cd ../

echo "Running regression tests..."
echo

${WORKSPACE}/pgadmin-venv/bin/python ${WORKSPACE}/web/regression/runtests.py  --pkg feature_tests || { echo 'ERROR: Error detected when running the Feature tests.' ; exit 1; }

echo "Cleaning up..."
echo

kill ${FB_PID}
