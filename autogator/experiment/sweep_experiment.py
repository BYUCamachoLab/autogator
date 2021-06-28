from autogator.experiment.experiment import ExperimentInterface, WavelengthAnalyzer
from autogator.data_cache import DataCache
from pathlib import Path
from autogator import SITE_CONFIG_DIR

COORDINATE_DIR = SITE_CONFIG_DIR / "sweep_data"
COORDINATE_DIR.mkdir(parents=True, exist_ok=True)


class SweepExperiment(ExperimentInterface):
    def run(self):
        print("Running...")
        # autogator
        cache = DataCache.get_instance()
        motion = cache.get_motion()

        # Laser Sweep
        lambda_start = float(input("Starting Wavelength: "))
        lambda_stop = float(input("Stopping Wavelength: "))
        duration = float(input("Duration: "))

        # Data Collection
        sample_rate = 10e09

        # Save Data
        # The first argument passed will be used as the file name.
        save_raw_data = True  # Save raw data collected from devices.

        # Oscilloscope
        take_screenshot = True
        active_channels = [1, 2, 3, 4]  # Channels to activate and use.
        trigger_channel = 1  # Channel for trigger signal.

        # Data Collection Folder
        folderName = COORDINATE_DIR

        for circuit in self.circuits:
            motion.go_to_circuit(circuit)
            # ---------------------------------------------------------------------------- #
            # Collect Data
            # ---------------------------------------------------------------------------- #
            print("Starting Acquisition")
            self.oscilliscope.start_acquisition(timeout=duration * 3)

            print("Sweeping Laser")
            self.laser.sweep_wavelength(lambda_start, lambda_stop, duration)

            print("Waiting for acquisition to complete.")
            self.oscilliscope.wait_for_device()

            if take_screenshot:
                self.oscilliscope.screenshot(folderName + "screenshot.png")

            # Acquire Data
            rawData = [None]  # Ugly hack to make the numbers line up nicely.
            rawData[1:] = [
                self.oscilliscope.get_data_ascii(channel) for channel in active_channels
            ]
            wavelengthLog = self.laser.wavelength_logging()
            wavelengthLogSize = self.laser.wavelength_logging_number()

            # Optional Save Raw Data
            if save_raw_data:
                print("Saving raw data.")
                for channel in active_channels:
                    with open(
                        folderName + "CHAN{}_Raw.txt".format(channel), "w"
                    ) as out:
                        out.write(str(rawData[channel]))
                with open(folderName + "Wavelength_Log.txt", "w") as out:
                    out.write(str(wavelengthLog))

            # ---------------------------------------------------------------------------- #
            # Process Data
            # ---------------------------------------------------------------------------- #
            analysis = WavelengthAnalyzer(
                sample_rate=sample_rate,
                wavelength_log=wavelengthLog,
                trigger_data=rawData[trigger_channel],
            )

            print("=" * 30)
            print(
                "Expected number of wavelength points: " + str(int(wavelengthLogSize))
            )
            print("Measured number of wavelength points: " + str(analysis.num_peaks()))
            print("=" * 30)

            data = [None]  # Really ugly hack to make index numbers line up.
            data[1:] = [
                # List comprehension to put all the datasets in this one array.
                analysis.process_data(rawData[channel])
                for channel in active_channels
            ]

            print("Raw Datasets: {}".format(len(rawData)))
            print("Datasets Returned: {}".format((len(data))))
