# build-meshtastic
(Unofficial) Re-Usable GitHub Action for building meshtastic firmware

## Example usage

```yaml
uses: vidplace7/build-meshtastic@main
with:
  git-ref: master
  arch: nrf52840
  board: xiao_ble
  build-script-path: bin/build-nrf52.sh
```

## Inputs

| Name                  | Required | Default   | Description                                                     |
| --------------------- | -------- | --------- | --------------------------------------------------------------- |
| `git-ref`             | True     | `master`  | The git ref (tag/branch) of the meshtastic firmware to checkout |
| `arch`                | True     | `esp32`   |                                                                 |
| `board`               | True     | _None_    |                                                                 |
| `build-script-path`   | True     | _None_    |                                                                 |
| `remove-debug-flags`  | False    | `""`      |                                                                 |
| `ota-firmware-source` | False    | `""`      |                                                                 |
| `ota-firmware-target` | False    | `""`      |                                                                 |
| `include-web-ui`      | False    | `"false"` |                                                                 |


## Outputs

| Name      | Description |
| --------- | ----------- |
| `version` |             |


## Output files

