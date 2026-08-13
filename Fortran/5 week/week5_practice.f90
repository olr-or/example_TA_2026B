program week5_final_project
    implicit none

    integer, parameter :: max_data = 1000
    integer :: n
    double precision :: x(max_data), y(max_data)
    double precision :: mean, stddev
    double precision :: maximum, minimum
    double precision :: threshold

    ! TODO 1: Read experiment.dat into x, y, and n.
    call read_data('experiment.dat', x, y, n, max_data)

    ! TODO 2: Reuse Week 4 functions/subroutines.
    mean = calc_mean(y, n)


    print *, 'Enter threshold:'
    read *, threshold

    ! TODO 3: Print threshold-selected data.


    ! TODO 4: Save all analysis results to result.dat.


contains

    ! Copy/adapt your Week 4 procedures below.
    ! Required:
    !   read_data
    !   calc_mean
    !   calc_stddev
    !   find_max
    !   find_min
    !   print_threshold_data
    !   save_results

end program week5_final_project
