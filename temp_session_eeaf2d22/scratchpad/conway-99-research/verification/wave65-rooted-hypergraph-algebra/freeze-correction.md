# Preinspection inventory correction

The initial inventory command used `rg --files` without `--hidden`. It
therefore omitted the discovery package's hidden `.gitattributes` file.
The omission was noticed only after the already-frozen manifest was read.

This is a verifier-procedure limitation, not a discovery-package
mathematical mismatch. The hidden file is hash-checked as part of the
independent manifest audit, but it was not included in the preinspection
inventory. No claim to a complete preinspection freeze is made.
