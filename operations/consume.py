def consume(source, sink, source_attr="remaining", sink_attr="remaining"):
    supply, demand = source[source_attr], sink[sink_attr]
    if (supply == 0 or demand == 0):
        return source, sink
    if supply > demand:
        source[source_attr] = supply - demand
        sink[source_attr] = 0
        return source, sink
    if supply == demand:
        source[source_attr] = 0
        sink[source_attr] = 0
        return source, sink
    if supply < demand:
        source[source_attr] = 0
        sink[source_attr] = demand - supply
        return source, sink