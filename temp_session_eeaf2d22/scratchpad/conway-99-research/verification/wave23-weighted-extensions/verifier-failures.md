# Retained verifier failures

## Initial timeout

The first independent-verifier invocation used a five-second command timeout
to check whether the process would yield.  The complete census had not
finished, so the process was terminated.  No output or mathematical inference
from that run was retained.  A 300-second invocation completed normally.

## Privacy-scanner false positive

While removing a literal local username from the verifier's privacy scanner,
an intermediate generalized check rejected the string `"/users/"` inside the
candidate checker's own path-detection source code.  This was a verifier
packaging false positive, not a discovery defect.  The final scanner requires
a full POSIX home path with a user component or a Windows drive-rooted path.
The corrected verifier passed, its 20 hostile tests passed, and the exact
result remained byte-identical.
