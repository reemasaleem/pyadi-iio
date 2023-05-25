import iio

import adi
import numpy as np
import pytest

try:
    import ad9361 as libad9361
except ImportError:
    libad9361 = None


hardware = "fmcomms5"
classname = "adi.FMComms5"

##################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize(
    "voltage_raw, low, high",
    [
        ("in_temp0", 80, 160),
        ("in_voltage0", 1578, 2087),
        ("in_voltage1", 2893, 3826),
        ("in_voltage2", 2893, 3826),
        ("in_voltage3", 3459, 4005),
        ("in_voltage4", 1140, 1507),
        ("in_voltage5", 1140, 1507),
        ("in_voltage6", 1140, 1507),
        ("in_voltage7", 1140, 1507),
    ],
)
def test_ad7291(context_desc, voltage_raw, low, high):
    ctx = None
    for ctx_desc in context_desc:
        if ctx_desc["hw"] in hardware:
            ctx = iio.Context(ctx_desc["uri"])
    if not ctx:
        pytest.skip("No valid hardware found")

    ad7291 = ctx.find_device("ad7291")

    for channel in ad7291.channels:
        c_name = "out" if channel.output else "in"
        c_name += "_" + str(channel.id)
        if c_name == voltage_raw:
            for attr in channel.attrs:
                if attr == "raw":
                    try:
                        print(channel.attrs[attr].value)
                        assert low <= int(channel.attrs[attr].value) <= high
                    except OSError:
                        continue


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
def test_init_fmcomms5(classname, iio_uri):
    #bring board to initial values in case of re-testing
    sdr = eval(classname + "(uri='" + iio_uri + "')")

    for channel in range(4):
        chname = "voltage" + str(channel)
        ch = sdr._rxadc.find_channel(chname, False)
        ch.attrs["calibphase"].value = str(0.0)
        ch.attrs["calibscale"].value = str(1.0)
        ch = sdr._txdac.find_channel(chname, True)
        ch.attrs["calibphase"].value = str(0.0)
        ch.attrs["calibscale"].value = str(1.0)
        ch = sdr._rxadc_chip_b.find_channel(chname, False)
        ch.attrs["calibphase"].value = str(0.0)
        ch.attrs["calibscale"].value = str(1.0)
        ch = sdr._txdac_chip_b.find_channel(chname, True)
        ch.attrs["calibphase"].value = str(0.0)
        ch.attrs["calibscale"].value = str(1.0)
    
    sdr._set_iio_attr("out", "voltage_filter_fir_en", False, 0)
    sdr._set_iio_attr("voltage0", "filter_fir_en", False, 0)
    sdr._set_iio_attr("voltage1", "filter_fir_en", False, 0)
    sdr._set_iio_attr("voltage2", "filter_fir_en", False, 0)
    sdr._set_iio_attr("out", "voltage_filter_fir_en", False, 0, sdr._ctrl_b)
    sdr._set_iio_attr("voltage0", "filter_fir_en", False, 0, sdr._ctrl_b)
    sdr._set_iio_attr("voltage1", "filter_fir_en", False, 0, sdr._ctrl_b)
    sdr._set_iio_attr("voltage2", "filter_fir_en", False, 0, sdr._ctrl_b)
    sdr._set_iio_attr("voltage0", "quadrature_tracking_en", False, 1)
    sdr._set_iio_attr("voltage1", "quadrature_tracking_en", False, 1)
    sdr._set_iio_attr("voltage2", "quadrature_tracking_en", False, 1)
    sdr._set_iio_attr("voltage0", "quadrature_tracking_en", False, 1, sdr._ctrl_b)
    sdr._set_iio_attr("voltage1", "quadrature_tracking_en", False, 1, sdr._ctrl_b)
    sdr._set_iio_attr("voltage2", "quadrature_tracking_en", False, 1, sdr._ctrl_b)
    del sdr

@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize(
    "attr, start, stop, step, tol",
    [
        ("tx_hardwaregain_chan0", -40.0, -7.0, 0.25, 0),
        ("tx_hardwaregain_chan1", -40.0, -7.0, 0.25, 0),
        ("rx_lo", 2300000000, 2500000000, 1, 8),
        ("tx_lo", 2300000000, 2500000000, 1, 8),
        ("sample_rate", 30700000, 30740000, 1, 4),
        ("rx_rf_bandwidth", 16000000, 19000000, 1, 4),
        ("tx_rf_bandwidth", 16000000, 19000000, 1, 4),
    ],
)
def test_fmcomms5_attr(
    test_attribute_single_value, iio_uri, classname, attr, start, stop, step, tol
):
    test_attribute_single_value(iio_uri, classname, attr, start, stop, step, tol)


# CHIP B
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize(
    "attr, start, stop, step, tol",
    [
        ("tx_hardwaregain_chip_b_chan0", -40.0, -7.0, 0.25, 0),
        ("tx_hardwaregain_chip_b_chan1", -40.0, -7.0, 0.25, 0),
        ("rx_lo_chip_b", 2300000000, 2500000000, 1, 8),
        ("tx_lo_chip_b", 2300000000, 2500000000, 1, 8),
        ("sample_rate", 30700000, 30740000, 1, 4),
        ("rx_rf_bandwidth_chip_b", 16000000, 19000000, 1, 4),
        ("tx_rf_bandwidth_chip_b", 16000000, 19000000, 1, 4),
    ],
)
def test_fmcomms5_chip_b_attr(
    test_attribute_single_value, iio_uri, classname, attr, start, stop, step, tol
):
    test_attribute_single_value(iio_uri, classname, attr, start, stop, step, tol)


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [0, 1, 2, 3])
def test_fmcomms5_loopback(test_dma_loopback, iio_uri, classname, channel):
    test_dma_loopback(iio_uri, classname, channel)

@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [0, 1])
@pytest.mark.parametrize(
    "dds_scale, min_rssi, max_rssi, param_set",
    [
        (
            0.0,
            75,
            150,
            dict(
                sample_rate=30720000,
                tx_lo=2300000000,
                rx_lo=2400000000,
                gain_control_mode_chan0="slow_attack",
                gain_control_mode_chan1="slow_attack",
                rx_rf_bandwidth=18000000,
                tx_rf_bandwidth=18000000,
            ),
        ),
        (
            0.125,
            10,
            50,
            dict(
                gain_control_mode_chan0="slow_attack",
                gain_control_mode_chan1="slow_attack",
                rx_lo=2400000000,
                tx_lo=2400000000,
                tx_hardwaregain_chan0=-10,
                tx_hardwaregain_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth=18000000,
                tx_rf_bandwidth=18000000,
            ),
        ),
    ],
)
def test_rssi(
    test_gain_check,
    iio_uri,
    classname,
    channel,
    param_set,
    dds_scale,
    min_rssi,
    max_rssi,
):
    test_gain_check(
        iio_uri, classname, channel, param_set, dds_scale, min_rssi, max_rssi
    )


# CHIP B
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [2, 3])
@pytest.mark.parametrize(
    "dds_scale, min_rssi, max_rssi, param_set",
    [
        (
            0.0,
            60,
            150,
            dict(
                sample_rate=30720000,
                tx_lo_chip_b=2300000000,
                rx_lo_chip_b=2400000000,
                gain_control_mode_chip_b_chan0="slow_attack",
                gain_control_mode_chip_b_chan1="slow_attack",
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                rx_rf_bandwidth_chip_b=18000000,
                tx_rf_bandwidth_chip_b=18000000,
            ),
        ),
        (
            0.125,
            10,
            50,
            dict(
                gain_control_mode_chip_b_chan0="slow_attack",
                gain_control_mode_chip_b_chan1="slow_attack",
                rx_lo_chip_b=2400000000,
                tx_lo_chip_b=2400000000,
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth_chip_b=18000000,
                tx_rf_bandwidth_chip_b=18000000,
            ),
        ),
    ],
)
def test_rssi_chip_b(
    test_gain_check,
    iio_uri,
    classname,
    channel,
    param_set,
    dds_scale,
    min_rssi,
    max_rssi,
):
    test_gain_check(
        iio_uri, classname, channel, param_set, dds_scale, min_rssi, max_rssi
    )


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [0, 1])
@pytest.mark.parametrize(
    "dds_scale, frequency, hardwaregain_low, hardwaregain_high, param_set",
    [
        (
            0.0,
            999859,
            50,
            80,
            dict(
                gain_control_mode_chan0="slow_attack",
                gain_control_mode_chan1="slow_attack",
                rx_lo=2400000000,
                tx_lo=2400000000,
                tx_hardwaregain_chan0=-10,
                tx_hardwaregain_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth=18000000,
                tx_rf_bandwidth=18000000,
            ),
        ),
        (
            0.125,
            999859,
            0.0,
            28,
            dict(
                gain_control_mode_chan0="slow_attack",
                gain_control_mode_chan1="slow_attack",
                rx_lo=2400000000,
                tx_lo=2400000000,
                tx_hardwaregain_chan0=-10,
                tx_hardwaregain_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth=18000000,
                tx_rf_bandwidth=18000000,
            ),
        ),
    ],
)
def test_hardware_gain(
    test_hardwaregain,
    iio_uri,
    classname,
    channel,
    dds_scale,
    frequency,
    hardwaregain_low,
    hardwaregain_high,
    param_set,
):
    test_hardwaregain(
        iio_uri,
        classname,
        channel,
        dds_scale,
        frequency,
        hardwaregain_low,
        hardwaregain_high,
        param_set,
    )


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [2, 3])
@pytest.mark.parametrize(
    "dds_scale, frequency, hardwaregain_low, hardwaregain_high, param_set",
    [
        (
            0.0,
            999859,
            50,
            80,
            dict(
                gain_control_mode_chip_b_chan0="slow_attack",
                gain_control_mode_chip_b_chan1="slow_attack",
                rx_lo_chip_b=2400000000,
                tx_lo_chip_b=2400000000,
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth_chip_b=18000000,
                tx_rf_bandwidth_chip_b=18000000,
            ),
        ),
        (
            0.125,
            999859,
            0.0,
            28,
            dict(
                gain_control_mode_chip_b_chan0="slow_attack",
                gain_control_mode_chip_b_chan1="slow_attack",
                rx_lo_chip_b=2400000000,
                tx_lo_chip_b=2400000000,
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                sample_rate=30720000,
                rx_rf_bandwidth_chip_b=18000000,
                tx_rf_bandwidth_chip_b=18000000,
            ),
        ),
    ],
)
def test_hardware_gain_chip_b(
    test_hardwaregain,
    iio_uri,
    classname,
    channel,
    dds_scale,
    frequency,
    hardwaregain_low,
    hardwaregain_high,
    param_set,
):
    test_hardwaregain(
        iio_uri,
        classname,
        channel,
        dds_scale,
        frequency,
        hardwaregain_low,
        hardwaregain_high,
        param_set,
    )


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("masterfile", [("/boot/fmcomms5_eeprom/fmcomms5.bin")])
@pytest.mark.parametrize("eeprom_path", [("/sys/devices/soc0/fpga-axi@0/41600000.i2c/i2c-0/i2c-6/6-0050/eeprom")])
def test_dcxo(test_dcxo_calibration, context_desc, classname, iio_uri, snumber, masterfile, eeprom_path):
    test_dcxo_calibration(context_desc, classname, iio_uri, snumber, masterfile, eeprom_path)


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [0, 1, 2, 3])
@pytest.mark.parametrize(
    "param_set, frequency, scale",
    [
        (
            dict(
                tx_lo=2400000000,
                rx_lo=2400000000,
                tx_hardwaregain_chan0=-10,
                tx_hardwaregain_chan1=-10,
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                sample_rate=30720000,
            ),
            2999577, 0.125
        )
    ],
)
@pytest.mark.parametrize(
    "low, high",
    [([-20.0, -110.0, -120.0, -120.0, -120.0], [-10.0, -60.0, -75.0, -75.0, -80.0])],
)
def test_harmonic_values(
    test_harmonics, classname, iio_uri, channel, param_set, low, high, frequency, scale, plot=False
):
    test_harmonics(classname, iio_uri, channel, param_set, low, high, frequency, scale, plot)


@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("channel", [0, 1, 2, 3])
@pytest.mark.parametrize(
    "param_set, frequency, scale",
    [
        (
            dict(
                tx_lo=3500000000,
                rx_lo=3500000000,
                tx_hardwaregain_chan0=-10,
                tx_hardwaregain_chan1=-10,
                tx_hardwaregain_chip_b_chan0=-10,
                tx_hardwaregain_chip_b_chan1=-10,
                sample_rate=30720000,
            ),
            2999577, 0.125
        ),
    ]
)
@pytest.mark.parametrize(
    "low, high",
    [([-20.0, -120.0, -120.0, -125.0, -125.0], [-10.0, -75.0, -75.0, -80.0, -80.0])],
)
def test_peaks(test_sfdrl, classname, iio_uri, channel, param_set, low, high, frequency, scale, plot=False):
    test_sfdrl(classname, iio_uri, channel, param_set, low, high, frequency, scale, plot)

@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("lo", [2400000000])
def test_fmcomms5_phase_sync(classname, iio_uri, lo):
    if libad9361:
        sdr = eval(classname + "(uri='" + iio_uri + "')")
        libad9361.fmcomms5_phase_sync(sdr._ctx, lo)
    else:
        raise Exception("libad9361-iio not installed/configured")

    del sdr
