# Reserved Future Integrations

This project reserves several command namespaces so the public UX can remain stable when Xiaomi MiMo exposes more APIs.

## `mimo image generate`

Reserved for text-to-image / image generation.

Implementation plan when a stable endpoint is documented:

- add `--prompt`, `--out`, `--aspect-ratio`, `--n`, `--seed`
- support URL/base64 download
- add payload tests and live smoke tests

## `mimo music generate`

Reserved for text-to-music / song generation.

Implementation plan:

- add `--prompt`, `--lyrics`, `--lyrics-file`, `--instrumental`, `--out`
- support async task polling if required
- save mp3/wav output

## `mimo speech transcribe`

Reserved for standalone ASR.

Implementation plan:

- add local file and URL inputs
- output text/json/srt if supported
- support multi-speaker metadata if API provides it

## `mimo gui`

Reserved for GUI/computer-use/browser-control capability.

Implementation plan:

- keep it opt-in and explicit because GUI automation can have side effects
- require dry-run/confirmation modes
- document security boundaries
