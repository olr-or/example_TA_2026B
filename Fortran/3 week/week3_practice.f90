program week3_project
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

    if (n <= 0 .or. n > max_data) stop 'Invalid n'

    ! TODO 1: Read n values into data(i).



    ! TODO 2: Calculate mean using the array.



    ! TODO 3: Calculate maximum and minimum.



    ! TODO 4: Calculate variance and stddev.



    print *, 'Enter threshold:'
    read *, threshold

    count_above = 0
    print *, 'Index       Value'

    ! TODO 5: Print index/value for data above threshold
    ! and count how many values satisfy the condition.



    print *, 'Mean            = ', mean
    print *, 'Std. Dev.       = ', stddev
    print *, 'Maximum         = ', maximum
    print *, 'Minimum         = ', minimum
    print *, 'Above threshold = ', count_above

end program week3_project
