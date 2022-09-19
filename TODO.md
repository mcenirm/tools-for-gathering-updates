* maybe switch to using wsusoffline from cloned tree instead of release?

# revamp approach to mimic package managers?

* treat each thing to update as a set of packages
* if a publisher doesn't have a normal package repository, then create a custom backend that mimics being a repository
* instead of "installing", track if a package has been added to a DVD yet
* clarify profiles of DVDs (eg, weekly vs monthly)
* maybe support explicit version downloads (eg, Microsoft updates by KB number)

example walkthrough:

1. `foo refresh` - check for new versions
2. `foo download` - download latest versions that we don't already have
3. `foo makedvd` - prepare DVD directory with updates


# Temurin OpenJDK install/update options

* update INSTALL instructions for OpenJDK update:

[GUI settings vs MSI features](https://adoptium.net/installation/windows/)

  [-] JDK with Hotspot -- (`FeatureMain`)
    [X] Add to `PATH` -- (`FeatureEnvironment`)
    [X] Associate with `.jar` -- (`FeatureJarFileRunWith`)
    [n] Set `JAVA_HOME` -- (`FeatureJavaHome`)
    [n] JavaSoft (Oracle) registry keys -- (`FeatureOracleJavaSoft`)

  * `INSTALLLEVEL=1` is same as `FeatureMain,FeatureEnvironment,FeatureJarFileRunWith`

> The following example silently installs all the features for `INSTALLLEVEL=1`:
>
> `msiexec /i <package>.msi INSTALLLEVEL=1 /quiet`
