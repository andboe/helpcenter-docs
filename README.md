# helpcenter-docs
A prototype mockup of the peopleware help center based on Antora.

## Libraries

Create libraries for:

### Breadcrumbs

Pattern: `bc-lvl1-lvl2-lvl3...`

```
    bc-forecast-workloads: menu:Forecast[Workloads]
    bc-wfm-administration: menu:WFM[Administration]
    bc-account-roles: menu:Account[Roles]
```

### Icons

Pattern: `icon-descriptive-name`

```
:icon-context-menu: image:help-center:ROOT:icons/3_dots_vertical.svg["context menu"]
:icon-descriptive-name: ...
```

### Permissions

Pattern: `permission-module-name`

```
permission-roles-full-access-to-roles: Full access to roles
permission-wfm-enable-access-to-wfm: Enable access to WFM
```

### Sort file contents alphabetically

Run in terminal:

```
python3 scripts/sort-file-contents.py <filepath>
```