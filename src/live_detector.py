from pathlib import Path
import json
import joblib
import pandas as pd

from scapy.all import (
    sniff,
    IP,
    TCP,
    UDP,
    conf
)

from .live_flow import FlowEngine


# ============================================================
# SCAPY WINDOWS CONFIG
# ============================================================

conf.use_pcap = True


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

MODEL_DIR = (
    BASE_DIR / "models"
)


# ============================================================
# LIVE DETECTOR
# ============================================================

class LiveDetector:

    def __init__(self):

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        self.model = joblib.load(
            MODEL_DIR / "best_model.pkl"
        )


        # ----------------------------------------------------
        # Load features
        # ----------------------------------------------------

        self.features = joblib.load(
            MODEL_DIR / "features.pkl"
        )


        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        metadata_path = (
            MODEL_DIR
            / "model_metadata.json"
        )


        if metadata_path.exists():

            with open(
                metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.metadata = json.load(
                    file
                )

        else:

            self.metadata = {
                "threshold": 0.5
            }


        self.threshold = float(
            self.metadata.get(
                "threshold",
                0.5
            )
        )


        # ----------------------------------------------------
        # Flow engine
        # ----------------------------------------------------

        self.engine = FlowEngine(
            timeout_seconds=5
        )


    # ========================================================
    # PACKET → FLOW
    # ========================================================

    def process_packet(
        self,
        packet
    ):

        if not packet.haslayer(IP):

            return


        ip = packet[IP]


        protocol = int(
            ip.proto
        )


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

            src_port = int(
                tcp.sport
            )

            dst_port = int(
                tcp.dport
            )


            # TCP flag string can contain:
            # S = SYN
            # A = ACK
            # R = RST

            flags = str(
                tcp.flags
            )


            syn = "S" in flags

            ack = "A" in flags

            rst = "R" in flags


        # ----------------------------------------------------
        # UDP
        # ----------------------------------------------------

        elif packet.haslayer(UDP):

            udp = packet[UDP]

            src_port = int(
                udp.sport
            )

            dst_port = int(
                udp.dport
            )


        # ----------------------------------------------------
        # Add to flow
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


    # ========================================================
    # PREDICT FLOW
    # ========================================================

    def predict_flow(
        self,
        flow
    ):

        # ----------------------------------------------------
        # Extract exactly model features
        # ----------------------------------------------------

        feature_data = {

            feature:
                flow[feature]

            for feature in self.features
        }


        X = pd.DataFrame(
            [feature_data],
            columns=self.features
        )


        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        probability = float(
            self.model
            .predict_proba(X)[0][1]
        )


        prediction = int(
            probability
            >= self.threshold
        )


        label = (
            "ATTACK"
            if prediction == 1
            else "NOT ATTACK"
        )


        return {

            "prediction":
                label,

            "prediction_code":
                prediction,

            "probability":
                probability,

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
                flow["_dst_port"]
        }


    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        interface=None
    ):

        print(
            "=" * 70
        )

        print(
            "NETGUARD AI - LIVE DETECTOR"
        )

        print(
            "=" * 70
        )

        print(
            f"Model threshold: "
            f"{self.threshold:.2f}"
        )

        print(
            "\nCapturing network traffic..."
        )

        print(
            "Press CTRL+C to stop.\n"
        )


        def callback(packet):

            self.process_packet(
                packet
            )


            expired = (
                self.engine
                .get_expired_flows()
            )


            for flow in expired:

                try:

                    result = (
                        self.predict_flow(
                            flow
                        )
                    )


                    if (
                        result["prediction"]
                        == "ATTACK"
                    ):

                        prefix = (
                            "🚨 ATTACK"
                        )

                    else:

                        prefix = (
                            "✅ NOT ATTACK"
                        )


                    print(

                        f"{prefix} | "

                        f"{result['source']} "

                        f"→ "

                        f"{result['destination']} "

                        f"| "

                        f"P(attack)="

                        f"{result['probability']:.2%}"

                    )


                except Exception as exc:

                    print(
                        "Prediction error:",
                        exc
                    )


        try:

            sniff(

                iface=interface,

                prn=callback,

                store=False

            )

        except KeyboardInterrupt:

            print(
                "\nStopping..."
            )

        finally:

            for flow in (
                self.engine.flush()
            ):

                try:

                    print(
                        self.predict_flow(
                            flow
                        )
                    )

                except Exception:

                    pass