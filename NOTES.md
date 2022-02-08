## dependencies

* wsusoffline on rhel8
   * cabextract
   * dialog
   * genisoimage
   * xmlstarlet


## commands

* download updates
   ```shell
   cd .../wsusoffline/sh
   ./download-updates.bash w100-x64 enu -includesp -includecpp -includedotnet -includewddefs
   ```

* update generator
   * interactive
   * creates `sh/update-generator.ini` and `sh/windows-10-versions.ini`
   ```shell
   cd .../wsusoffline/sh
   ./update-generator.bash
   ```

* create ISO image
   ```shell
   cd .../wsusoffline/sh
   ./create-iso-image.bash w100-x64 -includesp -includecpp -includedotnet -includewddefs -output-path "../iso-$(date +%Y%m%d-%H%M%S)" -create-hashes
   ```
