#!/usr/bin/env bash
here=$(cd -- "$(dirname -- "$BASH_SOURCE")" && /bin/pwd)
/usr/bin/env conda env update --prune --prefix "$here/../conda_env" --file="$here/conda_requirements.yml"
/usr/bin/env conda shell.bash activate "$here/../conda_env" > "$here/.env"
