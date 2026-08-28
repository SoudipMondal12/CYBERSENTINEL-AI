from __future__ import annotations

import threading
import time
from collections import deque
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from scapy.all import IP, TCP, UDP, conf, sniff

from src.live_flow import FlowEngine


# ============================================================
# SCAPY
# ============================================================

conf.use_pcap = True


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# LIVE MONITOR
# ============================================================

class LiveMonitor:

    def __init__(
        self,
        timeout_seconds: float = 5.0,
        max_results: int = 500
    ):

        self.model = joblib.load(
            MODEL_DIR / "best_model.pkl"
        )

        self.features = joblib.load(
            MODEL_DIR / "features.pkl"
        )

        self.engine = FlowEngine(
            timeout_seconds=timeout_seconds
        )

        self.results = deque(
            maxlen=max_results
        )

        self.lock = threading.Lock()

        self.running = False

        self.thread: Optional[
            threading.Thread
        ] = None

        self.interface = None

        self.total_flows = 0

        self.attack_count = 0

        self.benign_count = 0

        self.packet_count = 0

        self.start_time = None


    # ========================================================
    # PROCESS PACKET
    # ========================================================

    def process_packet(self, packet):

        if not packet.haslayer(IP):
            return

        self.packet_count += 1

        ip = packet[IP]

        protocol = int(ip.proto)

        src_port = 0
        dst_port = 0

        syn = False
        ack = False
        rst = False


        # ----------------------------------------------------
        # TCP
        # ----------------------------------------------------

        if packet.haslayer(TCP):

            tcp = packet[TCP]

            src_port = int(tcp.sport)
            dst_port = int(tcp.dport)

            flags = str(tcp.flags)

            syn = "S" in flags
            ack = "A" in flags
            rst = "R" in flags


        # ----------------------------------------------------
        # UDP
        # ----------------------------------------------------

        elif packet.haslayer(UDP):

            udp = packet[UDP]

            src_port = int(udp.sport)
            dst_port = int(udp.dport)


        # ----------------------------------------------------
        # Add packet to flow engine
        # ----------------------------------------------------

        self.engine.add_packet(

            src_ip=ip.src,

            dst_ip=ip.dst,

            src_port=src_port,

            dst_port=dst_port,

            protocol=protocol,

            packet_length=len(packet),

            syn=syn,

            ack=ack,

            rst=rst
        )


        # ----------------------------------------------------
        # Check expired flows
        # ----------------------------------------------------

        expired_flows = (
            self.engine
            .get_expired_flows()
        )


        for flow in expired_flows:

            self.predict_flow(flow)


    # ========================================================
    # PREDICT
    # ========================================================

    def predict_flow(self, flow):

        try:

            values = {
                feature: flow[feature]
                for feature in self.features
            }

            X = pd.DataFrame(
                [values],
                columns=self.features
            )

            probability = float(
                self.model
                .predict_proba(X)[0][1]
            )

            prediction = int(
                probability >= 0.5
            )

            label = (
                "ATTACK"
                if prediction == 1
                else "NOT ATTACK"
            )

            result = {

                "timestamp":
                    time.strftime("%H:%M:%S"),

                "source":
                    f"{flow['_src_ip']}:{flow['_src_port']}",

                "destination":
                    f"{flow['_dst_ip']}:{flow['_dst_port']}",

                "source_ip":
                    flow["_src_ip"],

                "destination_ip":
                    flow["_dst_ip"],

                "source_port":
                    flow["_src_port"],

                "destination_port":
                    flow["_dst_port"],

                "prediction":
                    label,

                "probability":
                    probability,

                "flow_duration":
                    flow["Flow Duration"],

                "packets":
                    (
                        flow["Total Fwd Packets"]
                        +
                        flow["Total Backward Packets"]
                    )
            }

            with self.lock:

                self.results.append(result)

                self.total_flows += 1

                if label == "ATTACK":

                    self.attack_count += 1

                else:

                    self.benign_count += 1


        except Exception as exc:

            print(
                "Prediction error:",
                exc
            )


    # ========================================================
    # CAPTURE LOOP
    # ========================================================

    def _capture_loop(self):

        self.start_time = time.time()

        try:

            sniff(

                iface=self.interface,

                prn=self.process_packet,

                store=False,

                stop_filter=lambda pkt: not self.running

            )

        except Exception as exc:

            print(
                "Capture error:",
                exc
            )

        finally:

            # Process remaining active flows

            remaining = (
                self.engine.flush()
            )

            for flow in remaining:

                self.predict_flow(
                    flow
                )


    # ========================================================
    # START
    # ========================================================

    def start(
        self,
        interface=None
    ):

        if self.running:
            return

        self.interface = interface

        self.running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )

        self.thread.start()


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        self.running = False


    # ========================================================
    # RESULTS
    # ========================================================

    def get_results(self):

        with self.lock:

            return list(
                self.results
            )


    # ========================================================
    # STATS
    # ========================================================

    def get_stats(self):

        with self.lock:

            total = self.total_flows

            attacks = self.attack_count

            benign = self.benign_count

            if total > 0:

                threat_rate = (
                    attacks
                    / total
                    * 100
                )

            else:

                threat_rate = 0.0


            return {

                "flows":
                    total,

                "attacks":
                    attacks,

                "benign":
                    benign,

                "packets":
                    self.packet_count,

                "threat_rate":
                    threat_rate,

                "running":
                    self.running
            }


    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        with self.lock:

            self.results.clear()

            self.total_flows = 0

            self.attack_count = 0

            self.benign_count = 0

            self.packet_count = 0