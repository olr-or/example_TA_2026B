program week4_project
    implicit none

    integer, parameter :: max_data = 1000
    integer :: i, n
    double precision :: data(max_data)
    double precision :: mean, stddev
    double precision :: maximum, minimum
    double precision :: threshold

    print *, 'Number of measurements:'
    read *, n
    if (n <= 0 .or. n > max_data) stop 'Invalid n'

    do i = 1, n
        read *, data(i)
    end do

    mean = calc_mean(data, n)

    ! TODO 1: Call calc_stddev().
    ! TODO 2: Call find_max() and find_min().


    print *, 'Enter threshold:'
    read *, threshold

    ! TODO 3: Call print_threshold_data().


    print *, 'Mean      = ', mean
    print *, 'Std. Dev. = ', stddev
    print *, 'Maximum   = ', maximum
    print *, 'Minimum   = ', minimum

contains

    double precision function calc_mean(data, n)
        implicit none
        integer, intent(in) :: n
        integer :: i
        double precision, intent(in) :: data(n)
        double precision :: sum

        sum = 0.0d0
        do i = 1, n
            sum = sum + data(i)
        end do
        calc_mean = sum / dble(n)
    end function calc_mean

    ! TODO 4: Implement calc_stddev().

    ! TODO 5: Implement find_max().

    ! TODO 6: Implement find_min().

    ! TODO 7: Implement print_threshold_data().

end program week4_project
