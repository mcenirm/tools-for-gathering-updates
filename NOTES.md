## dependencies

* wsusoffline on RHEL 8
   * `cabextract`
   * `dialog`
   * `xmlstarlet`

* DVD burning on RHEL 8
   * `dvd+rw-tools` (for `growisofs`)
   * `genisoimage` (used by wsusoffline)
   * `wodim` (aka `cdrecord`)

* Windows code-signing tools
   * `osslsigncode` (from _EPEL_)
   * `perl-Image-ExifTool` (from _EPEL_) for showing metadata from exe files


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


## weekly updates

### Windows Defender definitions

_Note: wsusoffline also downloads `mpam-fe.exe`, so the manual step is not necessary._

* "Manually download the update" from [Security intelligence updates for Microsoft Defender Antivirus and other Microsoft antimalware](https://www.microsoft.com/en-us/wdsi/defenderupdates)
   * "Microsoft Defender Antivirus for Windows 10 and Windows 8.1", "64-bit" link
   * The downloaded updater file is `mpam-fe.exe`.
*  [How to manually download the latest antimalware definition updates for Microsoft Forefront Client Security, Microsoft Forefront Endpoint Protection 2010 and Microsoft System Center 2012 Endpoint Protection](https://support.microsoft.com/en-us/topic/how-to-manually-download-the-latest-antimalware-definition-updates-for-microsoft-forefront-client-security-microsoft-forefront-endpoint-protection-2010-and-microsoft-system-center-2012-endpoint-protection-984a3fee-6354-e02f-619a-a71da6291d8a)
   * `mpam-fe.exe -q` - "This switch installs the definition update in quiet mode. Quiet mode suppresses the file extraction dialog box."


### Nessus plugin set

* [Install Plugins Manually](https://docs.tenable.com/nessus/Content/InstallPluginsManually.htm)
* `C:\Program Files\Tenable\Nessus\nessuscli.exe update {{tar.gz-filename}}`
