MHz = 10 ** 6
GHz = 10 ** 9

RASPBERRY_PI_MODELS = {
    "900021": {
        "Release Date": "Q3 2016",
        "Model": "A+",
        "PCB Revision": "1.1",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "900032": {
        "Release Date": "Q2 2016?",
        "Model": "B+",
        "PCB Revision": "1.2",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "900092": {
        "Release Date": "Q4 2015",
        "Model": "Zero",
        "PCB Revision": "1.2",
        "Memory": "512 MB",
        "Frequency": 1 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "900093": {
        "Release Date": "Q2 2016",
        "Model": "Zero",
        "PCB Revision": "1.3",
        "Memory": "512 MB",
        "Frequency": 1 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "920093": {
        "Release Date": "Q4 2016?",
        "Model": "Zero",
        "PCB Revision": "1.3",
        "Memory": "512 MB",
        "Frequency": 1 * GHz,
        "Notes": "(Mfg by Embest)"
    },
    "Beta": {
        "Release Date": "Q1 2012",
        "Model": "B (Beta)",
        "PCB Revision": "?",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "Beta Board"
    },
    "0002": {
        "Release Date": "Q1 2012",
        "Model": "B",
        "PCB Revision": "1.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": ""
    },
    "0003": {
        "Release Date": "Q3 2012",
        "Model": "B (ECN0001)",
        "PCB Revision": "1.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "Fuses mod and D14 removed"
    },
    "0004": {
        "Release Date": "Q3 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "0005": {
        "Release Date": "Q4 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Qisda)"
    },
    "0006": {
        "Release Date": "Q4 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Egoman)"
    },
    "0007": {
        "Release Date": "Q1 2013",
        "Model": "A",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Egoman)"
    },
    "0008": {
        "Release Date": "Q1 2013",
        "Model": "A",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "0009": {
        "Release Date": "Q1 2013",
        "Model": "A",
        "PCB Revision": "2.0",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Qisda)"
    },
    "000d": {
        "Release Date": "Q4 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Egoman)"
    },
    "000e": {
        "Release Date": "Q4 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "000f": {
        "Release Date": "Q4 2012",
        "Model": "B",
        "PCB Revision": "2.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Qisda)"
    },
    "0010": {
        "Release Date": "Q3 2014",
        "Model": "B+",
        "PCB Revision": "1.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "0011": {
        "Release Date": "Q2 2014",
        "Model": "Compute Module 1",
        "PCB Revision": "1.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "0012": {
        "Release Date": "Q4 2014",
        "Model": "A+",
        "PCB Revision": "1.1",
        "Memory": "256 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "0013": {
        "Release Date": "Q1 2015",
        "Model": "B+",
        "PCB Revision": "1.2",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Embest)"
    },
    "0014": {
        "Release Date": "Q2 2014",
        "Model": "Compute Module 1",
        "PCB Revision": "1.0",
        "Memory": "512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Embest)"
    },
    "0015": {
        "Release Date": "?",
        "Model": "A+",
        "PCB Revision": "1.1",
        "Memory": "256 MB / 512 MB",
        "Frequency": 700 * MHz,
        "Notes": "(Mfg by Embest)"
    },
    "a01040": {
        "Release Date": "Unknown",
        "Model": "2 Model B",
        "PCB Revision": "1.0",
        "Memory": "1 GB",
        "Frequency": 900 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "a01041": {
        "Release Date": "Q1 2015",
        "Model": "2 Model B",
        "PCB Revision": "1.1",
        "Memory": "1 GB",
        "Frequency": 900 * MHz,
        "Notes": "(Mfg by Sony)"
    },
    "a21041": {
        "Release Date": "Q1 2015",
        "Model": "2 Model B",
        "PCB Revision": "1.1",
        "Memory": "1 GB",
        "Frequency": 900 * MHz,
        "Notes": "(Mfg by Embest)"
    },
    "a22042": {
        "Release Date": "Q3 2016",
        "Model": "2 Model B (with BCM2837)",
        "PCB Revision": "1.2",
        "Memory": "1 GB",
        "Frequency": 900 * MHz,
        "Notes": "(Mfg by Embest)"
    },
    "9000c1": {
        "Release Date": "Q1 2017",
        "Model": "Zero W",
        "PCB Revision": "1.1",
        "Memory": "512 MB",
        "Frequency": 1 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "a02082": {
        "Release Date": "Q1 2016",
        "Model": "3 Model B",
        "PCB Revision": "1.2",
        "Memory": "1 GB",
        "Frequency": 1.2 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "a020a0": {
        "Release Date": "Q1 2017",
        "Model": "Compute Module 3 (and CM3 Lite)",
        "PCB Revision": "1.0",
        "Memory": "1 GB",
        "Frequency": 1.2 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "a22082": {
        "Release Date": "Q1 2016",
        "Model": "3 Model B",
        "PCB Revision": "1.2",
        "Memory": "1 GB",
        "Frequency": 1.2 * GHz,
        "Notes": "(Mfg by Embest)"
    },
    "a32082": {
        "Release Date": "Q4 2016",
        "Model": "3 Model B",
        "PCB Revision": "1.2",
        "Memory": "1 GB",
        "Frequency": 1.2 * GHz,
        "Notes": "(Mfg by Sony Japan)"
    },
    "a020d3": {
        "Release Date": "Q1 2018",
        "Model": "3 Model B+",
        "PCB Revision": "1.3",
        "Memory": "1 GB",
        "Frequency": 1.4 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "9020e0": {
        "Release Date": "Q4 2018",
        "Model": "3 Model A+",
        "PCB Revision": "1.0",
        "Memory": "512 MB",
        "Frequency": 1.4 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "a02100": {
        "Release Date": "Q1 2019",
        "Model": "Compute Module 3+",
        "PCB Revision": "1.0",
        "Memory": "1 GB",
        "Frequency": 1.2 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "a03111": {
        "Release Date": "Q2 2019",
        "Model": "4 Model B",
        "PCB Revision": "1.1",
        "Memory": "1 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "b03111": {
        "Release Date": "Q2 2019",
        "Model": "4 Model B",
        "PCB Revision": "1.1",
        "Memory": "2 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "b03112": {
        "Release Date": "Q2 2019",
        "Model": "4 Model B",
        "PCB Revision": "1.2",
        "Memory": "2 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "c03111": {
        "Release Date": "Q2 2019",
        "Model": "4 Model B",
        "PCB Revision": "1.1",
        "Memory": "4 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "c03112": {
        "Release Date": "Q2 2019",
        "Model": "4 Model B",
        "PCB Revision": "1.2",
        "Memory": "4 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    },
    "d03114": {
        "Release Date": "Q2 2020",
        "Model": "4 Model B",
        "PCB Revision": "1.4",
        "Memory": "8 GB",
        "Frequency": 2.0 * GHz,
        "Notes": "(Mfg by Sony)"
    }
}


def get_hardware_info(revision):
    info = {
        "Board": "ND",
        "Model": "ND",
        "Release Date": "ND",
        "PCB Revision": "ND",
        "Memory": "ND",
        "Frequency": 0.0,
        "Notes": "ND"
    }
    if revision in RASPBERRY_PI_MODELS:
        info = RASPBERRY_PI_MODELS[revision]
        info['Board'] = 'Raspberry Pi'
    return info
