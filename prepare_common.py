"""DVD preparation tools"""

import datetime
import shutil
import sys

import kits.helpers as helpers
import settings


class DVD:
    """DVD preparation class"""

    def __init__(self, tag: str, label: str, *items: str):
        self.tag = tag
        self.label = label
        self.items = [_ for _ in items]
        self.date = datetime.date.today().strftime("%Y%m%d")
        self.dir = settings.dvds / f"dvd-{self.date}-{tag}"
        self.install_instructions = self.dir / "INSTALL.txt"
        self.burn_and_scan_instructions = f"{self.dir}-BURN_AND_SCAN.txt"
        self.scan_report = f"{self.dir}-scan.log"

        if self.dir.exists():
            raise ValueError("target DVD directory already exists", self.dir)
        helpers.ensure_directory(self.dir)

        # prepare burn and scan instructions
        with open(self.burn_and_scan_instructions, "w", encoding="utf-8") as f:
            f.write(
                f"""

1.  Insert a blank DVD in the optical drive.

2.  Burn the folder to the disc.

    growisofs -dvd-compat -Z {repr(str(settings.dvd_device))} -verbose \\
        -iso-level 4 -joliet -joliet-long -rational-rock -udf \\
        -V {repr(self.label + " " + self.date)} \\
        {repr(str(self.dir))}

3.  Wait for the disc ejection after the burning completes.

4.  Reinsert the disc.

5.  As root, mount the DVD contents.

    mount -v -o ro -- {repr(str(settings.dvd_device))} {repr(str(settings.dvd_mountpoint))}

6.  As non-root, run the scan.

    (cd -- {repr(str(settings.dvd_mountpoint))} && clamscan -v -a -r --log={repr(str(self.scan_report))} .)

7.  As root, unmount and eject the disc.

    eject -v -- {repr(str(settings.dvd_mountpoint))}

8.  Label the DVD.

    {self.label}  {self.date}
"""
            )
            for item in self.items:
                print(f"    - {item}", file=f)
            print(file=f)

    def show_instructions(self) -> None:
        """Show the instructions for this DVD"""
        with open(self.install_instructions, encoding="utf-8") as f:
            print("---------- Installation instructions -----------------------")
            shutil.copyfileobj(f, sys.stdout)
            print("------------------------------------------------------------")
        print()
        with open(self.burn_and_scan_instructions, encoding="utf-8") as f:
            print("---------- Burn and scan instructions ----------------------")
            shutil.copyfileobj(f, sys.stdout)
            print("------------------------------------------------------------")

    def append_to_install_instructions(self, message: str) -> None:
        """Append installation instructions"""
        with open(self.install_instructions, "a", encoding="utf-8") as f:
            print(message, file=f)
