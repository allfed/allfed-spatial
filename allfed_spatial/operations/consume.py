

def consume(
    source, sink, source_attr="remaining", sink_attr="remaining", efficiency=1
):
    """
    Each source has an 'effective supply', which is the maximum demand
    that it can meet based on efficiency. When consumption occurs, supply
    will be decremented by the efficiency-adjusted amount, whereas demand
    will be decremented by the non-adjusted amount.

    Arguments:
        source {[type]} -- [description]
        sink {[type]} -- [description]

    Keyword Arguments:
        source_attr {str} -- [description] (default: {"remaining"})
        sink_attr {str} -- [description] (default: {"remaining"})
        efficiency {int} -- [description] (default: {1})

    Returns:
        [type] -- [description]
    """

    supply, demand = source[source_attr], sink[sink_attr]
    effective_supply = efficiency * supply

    if (supply == 0 or demand == 0):
        consumed = 0
        return source, sink, consumed

    if effective_supply > demand:
        consumed = demand
        source[source_attr] = supply - (consumed / efficiency)
        sink[source_attr] = 0
        return source, sink, consumed

    if effective_supply == demand:
        consumed = effective_supply
        source[source_attr] = 0
        sink[source_attr] = 0
        return source, sink, consumed

    if effective_supply < demand:
        consumed = effective_supply
        source[source_attr] = 0
        sink[source_attr] = demand - effective_supply
        return source, sink, consumed
