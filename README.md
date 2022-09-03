# domino-maintenance-mode
Easily place Domino in maintenance mode for upgrades and restore afterwards.

![Test](https://github.com/dominodatalab/domino-maintenance-mode/actions/workflows/test.yaml/badge.svg)
[![Docker Repository on Quay](https://quay.io/repository/domino/dmm/status "Docker Repository on Quay")](https://quay.io/repository/domino/dmm)

# Warnings

* It is important that the system is not being used while taking a snapshot until after the restore is complete. Changes to running executions during or after taking a snapshot of the system may result in executions not being fully stopped, or properly restored. If there are new Model API versions that are not fully updated (new version is in running state and old version is fully stopped), please allow this process to complete before using this tool.

* It is possible for a running, functioning App to have a PVC mounted from an unregistered EDV that it depends on. Since the EDV no longer exists, the App cannot be restarted with this PVC mounted and can fail. It is not possible to detect this scenario automatically via the API. Please do not unregister EDVs while in maintenance mode.

# Usage

1. Take a snapshot of running executions:

```
dmm snapshot my-snapshot-file.json
```

This will create a timestamped snapshot file which you will need to use in subsequent steps.

1. Stop all running Apps, Model APIs, Restartable Workspaces, and Scheduled Jobs:

```
dmm shutdown my-snapshot-file.json
```

<!-- 3. [OPTIONAL] You may wait for Jobs and Image Builds to complete themselves. If you would like to manually shut them down:

**Depending on the fault-tolerance of the user code, data may be lost with this operation.**

```
dmm stop-jobs 
```

This will stop Jobs and sync file system changes. You can discard changes by providing the `--discard` argument. 

```
dmm stop-builds
```

This will stop Image Builds. These can be manually retried after the system is upgraded from the Environments UI.  -->

1. Perform Domino maintenance / upgrade.

1. Restore previously running Apps, Model APIs and Scheduled Jobs. Workspaces should be manually restarted by users. 

```
dmm restore my-snapshot-file.json
```

# Domino Version Support

**Domino 4.4+**, please report any issues that may arise due to API changes, as not all versions have been validated.

Classic Workspaces are not currently supported and should be shutdown manually. 
