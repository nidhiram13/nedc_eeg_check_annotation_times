# nedc_eeg_check_annotation_times
This is a Python script for NEDC (Neural Engineering Data Consortium). It uses NEDC/s internal tools/libraries and is made specific to NEDC guidelines.
The program was made to fix seizure annotation files that contained events with e a start time less than zero or an end time greater than the file duration. It displays and can correct annotation files where the start/stop times extend beyond the file duration. 
