# build-meshtastic
(Unofficial) Re-Usable GitHub Action for building meshtastic firmware

## Example usage

```yaml
uses: vidplace7/build-meshtastic@main
with:
  git-ref: master
  arch: nrf52840
  board: xiao_ble
```

## Inputs

| Name                  | Required | Default   | Description                                                     |
| --------------------- | -------- | --------- | --------------------------------------------------------------- |
| `git-ref`             | True     | `master`  | The git ref (tag/branch) of the meshtastic firmware to checkout |
| `arch`                | True     | `esp32`   |                                                                 |
| `board`               | True     | _None_    |                                                                 |

## Outputs

| Name      | Description |
| --------- | ----------- |
| `version` |             |


## Output files

