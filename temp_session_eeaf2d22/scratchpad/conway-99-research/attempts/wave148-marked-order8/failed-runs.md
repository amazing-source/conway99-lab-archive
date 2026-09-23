# Wave 148 retained run failure

The first focused test replay reported one failure in the independent
order-eight column aggregate test.  The test required every order-eight class
to occur as a key in a sparse `Counter`.  The empty graph has exact aggregate
coefficient zero, so it is correctly absent from that sparse map.

The generator's internal dense-key control already included the empty class
and passed.  The test was repaired to interpret a missing sparse key as zero
and to require all present keys to belong to the frozen class stream.  No
mathematical row or stored artifact changed.

