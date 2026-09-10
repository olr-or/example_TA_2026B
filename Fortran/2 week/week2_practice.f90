program week2_project
    implicit none

    integer, parameter :: max_data = 1000
    integer :: i, n, count_above
    double precision :: data(max_data)
    double precision :: sum, mean
    double precision :: variance, stddev
    double precision :: maximum, minimum
    double precision :: threshold

    print *, 'Number of measurements:'
    read *, n

    ! TODO 1: Stop the program if n <= 0 or n > max_data.

    ! Part A: Repeated input with DO
    ! Part B: Store every input value in data(i).
    
    ! TODO 2: Read n measurements into data(i).

    ! TODO 3: Calculate sum and mean by looping over the array.

    ! TODO 4: Calculate maximum and minimum.
    ! Hint: initialize both values with data(1), then loop from i = 2.

    ! TODO 5: Calculate population variance and standard deviation.
    ! variance = sum((data(i)-mean)**2) / n

    print *, 'Enter threshold:'
    read *, threshold

    count_above = 0
    print *, 'Index       Value'

    ! TODO 6: Print the index and value of every measurement
    ! greater than threshold, and update count_above.

    print *, 'Mean            = ', mean
    print *, 'Std. Dev.       = ', stddev
    print *, 'Maximum         = ', maximum
    print *, 'Minimum         = ', minimum
    print *, 'Above threshold = ', count_above

end program week2_project
