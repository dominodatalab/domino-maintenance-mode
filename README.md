# domino-maintenance-mode
Easily place Domino in maintenance mode for upgrades and restore afterwards.

![Test](https://github.com/dominodatalab/domino-maintenance-mode/actions/workflows/test.yaml/badge.svg)
[![Docker Repository on Quay](https://quay.io/repository/domino/dmm/status "Docker Repository on Quay")](https://quay.io/repository/domino/dmm)

# Usage

**It is important the the system is not being used when entering maintenance mode. Changes to running executions after taking a snapshot of the system may result in executions not being fully stopped, or properly restored.**

1. Take a snapshot of running executions:

```
dmm snapshot
```

This will create a timestamped snapshot file which you will need to use in subsequent steps.

2. Stop all running Apps, Model APIs, Restartable Workspaces, and Scheduled Jobs:

```
dmm shutdown <snapshot file from above>
```

3. [OPTIONAL] You may wait for Jobs and Image Builds to complete themselves. If you would like to manually shut them down:

**Depending on the fault-tolerance of the user code, data may be lost with this operation.**

```
dmm stop-jobs 
```

This will stop Jobs and sync file system changes. You can discard changes by providing the `--discard` argument. 

```
dmm stop-builds
```

This will stop Image Builds. These can be manually retried after the system is upgraded from the Environments UI. 

4. Perform Domino maintenance / upgrade.

5. Restore previously running Apps, Model APIs and Scheduled Jobs. Workspaces should be manually restarted by users. 

```
dmm restore <snapshot file from above>
```

# Domino Version Support

**Domino 4.4+**, please report any issues that may arise due to API changes, as not all versions have been validated.

Classic Workspaces are not currently supported and should be shutdown manually. 
