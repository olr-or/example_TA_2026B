program week2_project
    implicit none

    integer :: i, n
    integer :: count_above
    double precision :: x
    double precision :: sum, mean
    double precision :: maximum, minimum
    double precision :: threshold

    print *, 'Number of measurements:'
    read *, n

    ! TODO 1: Stop the program if n <= 0.


    print *, 'Enter threshold:'
    read *, threshold

    sum = 0.0d0
    count_above = 0

    do i = 1, n
        print *, 'Enter measurement ', i
        read *, x

        ! TODO 2: Add x to sum.


        ! TODO 3: Update maximum and minimum.
        ! Hint: treat i == 1 separately.



        ! TODO 4: Increase count_above when x > threshold.


    end do

    ! TODO 5: Calculate mean.


    print *, 'Mean            = ', mean
    print *, 'Maximum         = ', maximum
    print *, 'Minimum         = ', minimum
    print *, 'Above threshold = ', count_above

end program week2_project
