# build-meshtastic
(Unofficial) Re-Usable GitHub Action for building meshtastic firmware

## Example usage

```yaml
uses: vidplace7/build-meshtastic@main
with:
  board:
  github_token:
  build-script-path:
  arch:
```

## Inputs

| Name                  | Required | Default   | Description |
| --------------------- | -------- | --------- | ----------- |
| `arch`                | True     | `esp32`   |             |
| `board`               | True     | _None_    |             |
| `build-script-path`   | True     | _None_    |             |
| `remove-debug-flags`  | False    | `""`      |             |
| `ota-firmware-source` | False    | `""`      |             |
| `ota-firmware-target` | False    | `""`      |             |
| `artifact-paths`      | False    | `""`      |             |
| `include-web-ui`      | False    | `"false"` |             |


## Outputs

| Name      | Description |
| --------- | ----------- |
| `version` |             |


## Output files

