from enum import Enum


class BoTIoTColumns(int, Enum):
    "BoT-IoT feature columns and its indexes"
    PKSEQID = 0
    STIME = 1
    FLGS = 2
    PROTO = 3
    SADDR = 4
    SPORT = 5
    DADDR = 6
    DPORT = 7
    PKTS = 8
    BYTES = 9
    STATE = 10
    LTIME = 11
    SEQ = 12
    DUR = 13
    MEAN = 14
    STDDEV = 15
    SMAC = 16
    DMAC = 17
    SUM = 18
    MIN = 19
    MAX = 20
    SOUI = 21
    DOUI = 22
    SCO = 23
    DCO = 24
    SPKTS = 25
    DPKTS = 26
    SBYTES = 27
    DBYTES = 28
    RATE = 29
    SRATE = 30
    DRATE = 31
    ATTACK = 32
    CATEGORY = 33
    SUBCATEGORY = 34
    SIPV4_POS1 = 35
    SIPV4_POS2 = 36
    SIPV4_POS3 = 37
    SIPV4_POS4 = 38
    SIPV6_POS1 = 39
    SIPV6_POS2 = 40
    SIPV6_POS3 = 41
    SIPV6_POS4 = 42
    SIPV6_POS5 = 43
    SIPV6_POS6 = 44
    SIPV6_POS7 = 45
    SIPV6_POS8 = 46
    DIPV4_POS1 = 47
    DIPV4_POS2 = 48
    DIPV4_POS3 = 49
    DIPV4_POS4 = 50
    DIPV6_POS1 = 51
    DIPV6_POS2 = 52
    DIPV6_POS3 = 53
    DIPV6_POS4 = 54
    DIPV6_POS5 = 55
    DIPV6_POS6 = 56
    DIPV6_POS7 = 57
    DIPV6_POS8 = 58


IntegerFeatures = [
    BoTIoTColumns.PKSEQID,
    BoTIoTColumns.SPORT,
    BoTIoTColumns.DPORT,
    BoTIoTColumns.PKTS,
    BoTIoTColumns.BYTES,
    BoTIoTColumns.SEQ,
    BoTIoTColumns.SPKTS,
    BoTIoTColumns.DPKTS,
    BoTIoTColumns.SBYTES,
    BoTIoTColumns.DBYTES,
]

NumberFeatures = [
    BoTIoTColumns.STIME,
    BoTIoTColumns.LTIME,
    BoTIoTColumns.DUR,
    BoTIoTColumns.MEAN,
    BoTIoTColumns.STDDEV,
    BoTIoTColumns.SUM,
    BoTIoTColumns.MIN,
    BoTIoTColumns.MAX,
    BoTIoTColumns.RATE,
    BoTIoTColumns.SRATE,
    BoTIoTColumns.DRATE,
]

DummieFeatures = [BoTIoTColumns.FLGS, BoTIoTColumns.PROTO, BoTIoTColumns.STATE]


FeaturesToRemove = [
    BoTIoTColumns.SMAC,
    BoTIoTColumns.DMAC,
    BoTIoTColumns.SOUI,
    BoTIoTColumns.DOUI,
    BoTIoTColumns.SCO,
    BoTIoTColumns.DCO,
    BoTIoTColumns.SADDR,
    BoTIoTColumns.DADDR,
    BoTIoTColumns.CATEGORY,
    BoTIoTColumns.SUBCATEGORY,
]
