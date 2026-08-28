from dataclasses import dataclass, field
from typing import Dict, Tuple
import time


# ============================================================
# FLOW KEY
# ============================================================

FlowKey = Tuple[
    str,   # source IP
    str,   # destination IP
    int,   # source port
    int,   # destination port
    int    # protocol
]


# ============================================================
# FLOW DATA
# ============================================================

@dataclass
class LiveFlow:

    src_ip: str
    dst_ip: str

    src_port: int
    dst_port: int

    protocol: int

    first_seen: float
    last_seen: float

    # Packet counts
    fwd_packets: int = 0
    bwd_packets: int = 0

    # Byte counts
    fwd_bytes: int = 0
    bwd_bytes: int = 0

    # Packet sizes
    packet_lengths: list = field(
        default_factory=list
    )

    fwd_packet_lengths: list = field(
        default_factory=list
    )

    bwd_packet_lengths: list = field(
        default_factory=list
    )

    # TCP flags
    syn_count: int = 0
    ack_count: int = 0
    rst_count: int = 0


# ============================================================
# FLOW ENGINE
# ============================================================

class FlowEngine:

    def __init__(
        self,
        timeout_seconds: float = 5.0
    ):

        self.timeout_seconds = (
            timeout_seconds
        )

        self.flows: Dict[
            FlowKey,
            LiveFlow
        ] = {}


    # ========================================================
    # CREATE CANONICAL KEY
    # ========================================================

    def _get_key(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        protocol: int
    ) -> FlowKey:

        endpoint_a = (
            src_ip,
            src_port
        )

        endpoint_b = (
            dst_ip,
            dst_port
        )

        if endpoint_a <= endpoint_b:

            return (
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                protocol
            )

        return (
            dst_ip,
            src_ip,
            dst_port,
            src_port,
            protocol
        )


    # ========================================================
    # ADD PACKET
    # ========================================================

    def add_packet(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        protocol: int,
        packet_length: int,
        syn: bool = False,
        ack: bool = False,
        rst: bool = False
    ):

        now = time.time()

        key = self._get_key(
            src_ip,
            dst_ip,
            src_port,
            dst_port,
            protocol
        )


        # ----------------------------------------------------
        # New flow
        # ----------------------------------------------------

        if key not in self.flows:

            self.flows[key] = LiveFlow(

                src_ip=src_ip,

                dst_ip=dst_ip,

                src_port=src_port,

                dst_port=dst_port,

                protocol=protocol,

                first_seen=now,

                last_seen=now
            )


        flow = self.flows[key]

        flow.last_seen = now


        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        forward = (
            src_ip == flow.src_ip
            and
            src_port == flow.src_port
        )


        if forward:

            flow.fwd_packets += 1

            flow.fwd_bytes += packet_length

            flow.fwd_packet_lengths.append(
                packet_length
            )

        else:

            flow.bwd_packets += 1

            flow.bwd_bytes += packet_length

            flow.bwd_packet_lengths.append(
                packet_length
            )


        # ----------------------------------------------------
        # General packet statistics
        # ----------------------------------------------------

        flow.packet_lengths.append(
            packet_length
        )


        # ----------------------------------------------------
        # TCP flags
        # ----------------------------------------------------

        if syn:
            flow.syn_count += 1

        if ack:
            flow.ack_count += 1

        if rst:
            flow.rst_count += 1


    # ========================================================
    # EXPIRE FLOWS
    # ========================================================

    def get_expired_flows(self):

        now = time.time()

        expired = []


        for key, flow in list(
            self.flows.items()
        ):

            if (
                now - flow.last_seen
                >= self.timeout_seconds
            ):

                expired.append(
                    self._to_features(flow)
                )

                del self.flows[key]


        return expired


    # ========================================================
    # FLUSH
    # ========================================================

    def flush(self):

        expired = []

        for key, flow in list(
            self.flows.items()
        ):

            expired.append(
                self._to_features(flow)
            )

            del self.flows[key]


        return expired


    # ========================================================
    # CALCULATE MEAN
    # ========================================================

    @staticmethod
    def _mean(values):

        if not values:

            return 0.0

        return sum(values) / len(values)


    # ========================================================
    # CALCULATE STD
    # ========================================================

    @staticmethod
    def _std(values):

        if len(values) <= 1:

            return 0.0

        mean = (
            sum(values)
            / len(values)
        )

        variance = (
            sum(
                (x - mean) ** 2
                for x in values
            )
            / len(values)
        )

        return variance ** 0.5


    # ========================================================
    # CONVERT FLOW → MODEL FEATURES
    # ========================================================

    def _to_features(
        self,
        flow: LiveFlow
    ):

        # Duration in microseconds,
        # matching the CICIDS feature convention.

        duration_seconds = max(
            flow.last_seen
            - flow.first_seen,
            1e-6
        )

        duration_microseconds = (
            duration_seconds
            * 1_000_000
        )


        total_packets = (
            flow.fwd_packets
            + flow.bwd_packets
        )


        total_bytes = (
            flow.fwd_bytes
            + flow.bwd_bytes
        )


        # ----------------------------------------------------
        # Rates
        # ----------------------------------------------------

        flow_bytes_per_second = (
            total_bytes
            / duration_seconds
        )


        flow_packets_per_second = (
            total_packets
            / duration_seconds
        )


        fwd_packets_per_second = (
            flow.fwd_packets
            / duration_seconds
        )


        bwd_packets_per_second = (
            flow.bwd_packets
            / duration_seconds
        )


        # ----------------------------------------------------
        # Packet statistics
        # ----------------------------------------------------

        packet_mean = (
            self._mean(
                flow.packet_lengths
            )
        )


        packet_std = (
            self._std(
                flow.packet_lengths
            )
        )


        minimum_packet = (
            min(flow.packet_lengths)
            if flow.packet_lengths
            else 0.0
        )


        maximum_packet = (
            max(flow.packet_lengths)
            if flow.packet_lengths
            else 0.0
        )


        # ----------------------------------------------------
        # Return EXACT model feature names
        # ----------------------------------------------------

        return {

            "Destination Port":
                float(flow.dst_port),

            "Flow Duration":
                float(duration_microseconds),

            "Total Fwd Packets":
                float(flow.fwd_packets),

            "Total Backward Packets":
                float(flow.bwd_packets),

            "Total Length of Fwd Packets":
                float(flow.fwd_bytes),

            "Total Length of Bwd Packets":
                float(flow.bwd_bytes),

            "Flow Bytes/s":
                float(flow_bytes_per_second),

            "Flow Packets/s":
                float(flow_packets_per_second),

            "Fwd Packets/s":
                float(fwd_packets_per_second),

            "Bwd Packets/s":
                float(bwd_packets_per_second),

            "SYN Flag Count":
                float(flow.syn_count),

            "ACK Flag Count":
                float(flow.ack_count),

            "RST Flag Count":
                float(flow.rst_count),

            "Average Packet Size":
                float(packet_mean),

            "Min Packet Length":
                float(minimum_packet),

            "Max Packet Length":
                float(maximum_packet),

            "Packet Length Mean":
                float(packet_mean),

            "Packet Length Std":
                float(packet_std),

            # Metadata used by dashboard,
            # NOT sent to model.
            "_src_ip":
                flow.src_ip,

            "_dst_ip":
                flow.dst_ip,

            "_src_port":
                flow.src_port,

            "_dst_port":
                flow.dst_port
        }