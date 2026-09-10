program week3_project
    implicit none

    integer, parameter :: max_data = 1000
    integer :: n
    double precision :: x(max_data), y(max_data)
    double precision :: mean, stddev
    double precision :: maximum, minimum
    double precision :: threshold

    print *, '========================================'
    print *, '   SCIENTIFIC DATA ANALYSIS PROGRAM'
    print *, '========================================'

    ! Part A: Functions and subroutines
    ! Part B: File input/output

    ! TODO 1: Read n and all (x,y) pairs from experiment.dat.
    
    call read_data('experiment.dat', x, y, n, max_data)

    ! TODO 2: Reuse the analysis procedures from Part A.
    
    mean = calc_mean(y, n)
    stddev = calc_stddev(y, n, mean)
    
    call find_max(y, n, maximum)
    call find_min(y, n, minimum)

    print *, 'Enter threshold:'
    read *, threshold

    ! TODO 3: Print the threshold-selected data.
    
    call print_threshold_data(x, y, n, threshold)

    print *, 'Number of data     = ', n
    print *, 'Mean               = ', mean
    print *, 'Standard deviation = ', stddev
    print *, 'Maximum            = ', maximum
    print *, 'Minimum            = ', minimum

    ! TODO 4: Save the same analysis results to result.dat.
    
    call save_results('result.dat', n, mean, stddev, maximum, minimum, x, y, threshold)

contains

    subroutine read_data(filename, x, y, n, max_data)
        implicit none
        character(len=*), intent(in) :: filename
        integer, intent(in) :: max_data
        integer, intent(out) :: n
        integer :: i
        double precision, intent(out) :: x(max_data), y(max_data)

        ! TODO 5: Open filename, read n and all (x,y) pairs, then close it.
        
        n = 0
        x = 0.0d0
        y = 0.0d0
    end subroutine read_data

    double precision function calc_mean(data, n)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: data(n)
        double precision :: sum

        ! TODO 6: Move the mean calculation into this function.
        
        sum = 0.0d0
        calc_mean = sum
    end function calc_mean

    double precision function calc_stddev(data, n, mean)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: data(n), mean
        double precision :: variance

        ! TODO 7: Implement the population standard deviation.
        
        variance = 0.0d0
        calc_stddev = 0.0d0
    end function calc_stddev

    subroutine find_max(data, n, maximum)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: data(n)
        double precision, intent(out) :: maximum

        ! TODO 8: Find the maximum value.
        
        maximum = 0.0d0
    end subroutine find_max

    subroutine find_min(data, n, minimum)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: data(n)
        double precision, intent(out) :: minimum

        ! TODO 9: Find the minimum value.
        
        minimum = 0.0d0
    end subroutine find_min

    subroutine print_threshold_data(x, y, n, threshold)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: x(n), y(n), threshold

        ! TODO 10: Print the index, x, and y for every y above threshold.
        
    end subroutine print_threshold_data

    subroutine save_results(filename, n, mean, stddev, maximum, minimum, x, y, threshold)
        implicit none
        character(len=*), intent(in) :: filename
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: mean, stddev, maximum, minimum
        double precision, intent(in) :: x(n), y(n), threshold

        ! TODO 11: Write the analysis result and threshold-selected data to result.dat.
        
    end subroutine save_results

end program week3_project
