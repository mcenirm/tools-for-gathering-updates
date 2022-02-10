## dependencies

* wsusoffline on RHEL 8
   * `cabextract`
   * `dialog`
   * `xmlstarlet`

* DVD burning on RHEL 8
   * `dvd+rw-tools` (for `growisofs`)
   * `genisoimage` (used by wsusoffline)
   * `wodim` (aka `cdrecord`)


## wsusoffline commands

* download updates

   *Note: `download-updates.bash` will check files under `.../wsusoffline/timestamps/`, and skip categories based on the `interval_length_*` settings in `.../wsusoffline/sh/libraries/timestamps.bash` (eg, 4 hours for Windows Defender definitions, but 2 days for most of the others)*

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

## ISO image and optical media commands

*Note: Members of group `cdrom` have read-write access to `/dev/cdrom` (`/dev/sr0`).*

|||
|-|-|
| **ISO images**
| primary volume descriptor | `isoinfo -i $ISOFILE -d`
| "*ls -lR*"-style contents | `isoinfo -i $ISOFILE -l`
| "*find . -print*"-style contents | `isoinfo -i $ISOFILE -f`
|
| **optical drives**
| eject disc | `eject`
| close tray | `eject --trayclose`
| list optical drives and media | `wodim --devices`
|
| **burning**
| burn ISO to disc | `wodim -v $ISOFILE` <br> **OR** <br> `growisofs -dvd-compat -Z /dev/cdrom=$ISOFILE`

From _growisofs(1)_ man page:

> To  master  and  burn  an ISO9660 volume with Joliet and Rock-Ridge extensions on a DVD or Blu-ray Disc:
>
> `growisofs -Z /dev/dvd -R -J /some/files`
>
> To append more data to same media:
>
> `growisofs -M /dev/dvd -R -J /more/files`
>
> Make sure to use the same options for both initial burning and when appending data.
>
> To finalize the multisession DVD maintaining maximum compatibility:
>
> `growisofs -M /dev/dvd=/dev/zero`
>
> To use growisofs to write a pre-mastered ISO-image to a DVD:
>
> `growisofs -dvd-compat -Z /dev/dvd=image.iso`
>
> where image.iso represents an arbitrary object in the filesystem, such as file, named pipe or  device  entry.  Nothing is growing here and command name is not intuitive in this context.

Notes on `growisofs {-Z,-M}` and its `mkisofs`/`genisoimage` backend:

* The *`pathspec`* option is a folder whose contents will be placed at the root of the DVD. Multiple can be listed and their contents will be merged.

   ```shell
   growisofs -Z /dev/dvd -r -R -J pathspec1 pathspec2
   ```

* The DVD will include the original uid/gid of files unless the `-r` option is used.

   ```shell
   growisofs -Z /dev/dvd -r -R -J $FOLDER_WITH_FILES
   ```

* Some _*.cab_ file names will be truncated unless the `-joliet-long` option is included.

   ```shell
   growisofs -Z /dev/dvd -r -R -J -joliet-long $FOLDER_WITH_FILES
   ```

* wsusoffline's `sh/create-iso-image.bash` uses these options:
   * `-verbose`
   * `-iso-level 4`
   * `-joliet`
   * `-joliet-long`
   * `-rational-rock`
   * `-udf`

* To prevent an extra optical drive eject (after `growisofs -Z`), initialize and close the disc using the `-dvd-compat` option:

   ```shell
   growisofs -dvd-compat -Z /dev/sr1 -verbose -iso-level 4 -joliet -joliet-long -rational-rock -udf $FOLDER_WITH_FILES
   ```
