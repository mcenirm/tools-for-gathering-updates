1. If `conda_requirements.yml` has changed, or if `.env` is missing,
   then reset the conda environment.

   ```shell
   ./reset_conda_env.bash
   ```

2. (Optional) Configure your login shell for conda, replacing `bash`
   with the name of your login shell. See `conda init --help`.

   ```shell
   conda init bash
   ```

3. Activate the conda environment.

   1. If you used `conda init`, then activate the environment in your
      current shell.

      ```shell
      conda activate ../conda_env
      ```

   2. Otherwise, you can run conda in a new shell process.

      ```shell
      bash --rcfile .env
      ```

4. Gather various updates

   ```shell
   python wsusoffline_0_download.py
   python wsusoffline_1_install.py
   python prepare_weekly.py
   ```
