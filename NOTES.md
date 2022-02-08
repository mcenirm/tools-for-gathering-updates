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
