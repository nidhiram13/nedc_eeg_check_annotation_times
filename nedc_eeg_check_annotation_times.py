#!/usr/bin/env python
#
# file: $NEDC_NFC/util/python/nedc_eeg_check_annotation_times/nedc_*check*.py
#
# revision history:
#
# 20221011 (JP): final review
# 20221011 (PM): code review
# 20221001 (NR): initial version
#
# This is a Python script that displays and can correct annotation files
# where the start/stop times extend beyond the file duration
#------------------------------------------------------------------------------

# import system modules
#
import os
import sys

# import nedc_modules
#
import nedc_ann_eeg_tools as nae
import nedc_cmdl_parser as ncp
import nedc_debug_tools as ndt
import nedc_file_tools as nft

#-----------------------------------------------------------------------------
#
# global variables are listed here
#
#-----------------------------------------------------------------------------

# set the filename using basename
#
__FILE__ = os.path.basename(__file__)

# define the location of the help files
#
HELP_FILE = \
    "$NEDC_NFC/util/python/nedc_eeg_check_annotation_times/" \
    "nedc_eeg_check_annotation_times.help"

USAGE_FILE = \
    "$NEDC_NFC/util/python/nedc_eeg_check_annotation_times/" \
    "nedc_eeg_check_annotation_times.usage"

# define default option values
#
ARG_UPDATE = "--update"
ARG_ABRV_UPDATE = "-u"

# define default argument values
#
DEF_UPDATE = False

#------------------------------------------------------------------------------
#
# functions are listed here
#
#------------------------------------------------------------------------------

# declare a global debug object so we can use it in functions
#
dbgl = ndt.Dbgl()

# function: nedc_eeg_check_ann_times
#
# arguments:
#  fname: input filename 
#  update: a flag to see if we want to override the current file
#  fp: file pointer (normally stdout)
#
# return: boolean 
#
# This method reads a file, checks each annotation event, and displays any
# event found to have a start time less than zero or stop time greater than the
# file duration.
#
def nedc_eeg_check_ann_times(fname, update, fp = sys.stdout):

    # declare local variables
    #
    ann = nae.AnnEeg()
    
    # check if the file is an annotation file
    #
    status = ann.load(fname)

    if status is True:
        
        # get the file duration
        #
        file_dur = ann.get_file_duration()
        
        # get annotation data
        #
        annotations = ann.get_graph()

        # get the channel and its corresponding annotations
        #
        for channel, data in annotations[0][0].items():

            # new annotations
            #
            new_anno = []
            
            # loop through each annotation
            #
            for anno in data:

                # unzip the list: annotation structure is
                # [start_time, stop_time, {'label': prob}]
                #
                start_time, stop_time, prob = anno

                # set the new start and stop times to 0 and the file duration,
                # respectively
                #
                new_start_time = float(0)
                new_stop_time = file_dur
                
                # check if start time is less than 0 and print out message
                # if so
                #
                if start_time < 0:
                    fp.write("channel %s:\n" %
                             (channel))
                    fp.write("orig: [start time = %0.4f]\n" %
                             (start_time))
                    fp.write("new:  [start time = %0.4f]\n" %
                             (new_start_time))
                    start_time = float(0.0)
                    
                # check if stop time is greater than the file duration and
                # print out message if so
                #
                if stop_time > file_dur:
                    fp.write("channel %s:\n" %
                             (channel))
                    fp.write("orig: [stop time = %0.4f]\n" %
                             (stop_time))
                    fp.write("new:  [stop time = %0.4f]\n" %
                             (new_stop_time))
                    stop_time = file_dur

                # build the new dictionary with the correct start/stop times
                #
                new_anno.append([start_time, stop_time, prob])

            # add correct annotation data back to each channel in dictionary
            #
            annotations[0][0][channel] = new_anno
            
        # update the annotation file with the correct start/stop times if the
        # update flag is given 
        #
        if update and annotations != ann.get_graph():

            # check if annotation dictionary exists
            #
            if ann.get_graph() == False:
                print("Error: %s (line: %s) %s: error getting ann data (%s)" %
                       (__FILE__, ndt.__LINE__, ndt.__NAME__, fname))
                sys.exit(os.EX_SOFTWARE)
            
            # set the annotation object to the new annotations
            #
            ann.set_graph(annotations)
                
            # write the new dictionary to the annotation file
            #   
            ann.write(fname)

    # display debug information
    #
    if dbgl > ndt.BRIEF:
        fp.write("%s (line: %s) %s: done in nedc_eeg_check_ann_times\n" %
                 (__FILE__, ndt.__LINE__, ndt.__NAME__))
            
    # exit gracefully
    #
    return True

# function: main
#
def main(argv):

    # declare local variables
    #
    dbgl = ndt.Dbgl()
    ann = nae.AnnEeg()
    
    # create a command line parser
    #
    cmdl = ncp.Cmdl(USAGE_FILE, HELP_FILE)
    cmdl.add_argument("files", type = str, nargs = '*')
    cmdl.add_argument(ARG_UPDATE, ARG_ABRV_UPDATE, action="store_true")
    
    # parse the command line
    #
    args = cmdl.parse_args()

    # check the number of arguments
    #
    if len(args.files) == int(0):
        cmdl.print_usage('stdout')

    # get the parameter values
    #
    if args.update is None:
        args.update = DEF_UPDATE

    if dbgl > ndt.NONE:
        print("command line arguments:")
        print(" update = %s" % (args.update))
        print(nft.STRING_EMPTY)

    # display an informational message
    #
    print("beginning argument processing...")

    # main processing loop: loop over all input filenames
    #
    num_files_att = int(0)
    num_files_proc = int(0)

    for fname in args.files:

        # expand the filename (checking for environment variables)
        #
        ffile = nft.get_fullpath(fname)

        # check if the file exists
        #
        if os.path.exists(ffile) is False:
            print("Error: %s (line: %s) %s: file does not exist (%s)" %
                  (__FILE__, ndt.__LINE__, ndt.__NAME__, fname))
            sys.exit(os.EX_SOFTWARE)

        # case (1): an annotation file
        #
        if ann.validate(fname):

            # display debug information
            #
            if dbgl > ndt.NONE:
                print("%s (line: %s) %s: opening file (%s)" %
                      (__FILE__, ndt.__LINE__, ndt.__NAME__, fname))

            # display informational message
            #
            num_files_att += int(1)
            print(" %6d: %s" % (num_files_att, fname))
        
            if nedc_eeg_check_ann_times(fname,
                                        args.update) == True:
                num_files_proc += int(1)
            
        # case (2): a list
        #
        else:
        
            # display debug information
            #
            if dbgl > ndt.NONE:
                print("%s (line: %s) %s: opening list (%s)" %
                      (__FILE__, ndt.__LINE__, ndt.__NAME__, fname))
                
            # fetch the list
            #
            files = nft.get_flist(ffile)
            if files is None:
                print("Error: %s (line: %s) %s: error opening (%s)" %
                      (__FILE__, ndt.__LINE__, ndt.__NAME__, fname))
                sys.exit(os.EX_SOFTWARE)

            else:

                # loop over all files in the list
                #
                for ann_fname in files:
                    
                    # expand the filename (checking for environment variables)
                    #
                    ffile = nft.get_fullpath(ann_fname)
                    
                    # check if the file exists
                    #
                    if os.path.exists(ffile) is False:
                        print("Error: %s (line: %s) %s: %s (%s)" %
                              (__FILE__, ndt.__LINE__, ndt.__NAME__,
                               "file does not exist", ann_fname))
                        sys.exit(os.EX_SOFTWARE)
                                            
                    # check each file type in the list
                    #
                    if ann.validate(ffile):

                        # display debug information
                        #
                        if dbgl > ndt.NONE:
                            print("%s (line: %s) %s: opening file (%s)" %
                                  (__FILE__, ndt.__LINE__, ndt.__NAME__,
                                   ann_fname))
                            
                        # display informational message
                        #                    
                        num_files_att += int(1)
                        print(" %6d: %s" % (num_files_att, ann_fname))

                        if nedc_eeg_check_ann_times(ffile,
                                                    args.update) == True:
                            num_files_proc += int(1)

                    # display error if invalid file type in list
                    #
                    else:
                        print("Error: %s (line: %s) %s: %s " %
                              (__FILE__, ndt.__LINE__, ndt.__NAME__,
                               "file type is invalid"))
                        sys.exit(os.EX_SOFTWARE)

    # display the results
    #
    print("processed %ld out of %ld files successfully" %
	  (num_files_proc, num_files_att))

    # exit gracefully
    #
    return True

# begin gracefully
#
if __name__ == '__main__':
    main(sys.argv[0:])
#
# end of file
