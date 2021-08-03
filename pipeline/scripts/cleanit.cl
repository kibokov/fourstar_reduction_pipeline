# code to do pixel filtering. it expects input files base1.fits, base2.fits, base3.fits, base4.fits

#remove temporary outputs
!rm out*fits
#call relevant IRAF packages
stsdas

#remove temporary files
!rm foo*

#compute a "ring median" with an innder radius of 0 and an outer
#radius of 1.5 pixels. can probably replace this with a 3x3 box median
#or a 5x5 box median. Experiment!
rmedian base1 foo2 0.0 1.5

#subtract the median filtered image from the original. This removes
#all larger scale patterns, leaving only small-scale fluctuations
imarith base1 - foo2 foo3

#add a baseline offset to the median smoothed image. This is ~~10x the
# stddev of the object-free portions of the image. We could get fancier
# here and measure that sky variation and copde that number in place of 100.
imarith foo2 + 100 foo4

#divide the high frequency image by the off smoothed image. The goal
# here is to create a rescaled version of the high frequency image in
# which locations where the original image has high pixel values are
# downweighted. I.e. the cores of star images, for example, are
# spatially changing fast and so will get captured by the high
# frequency residual image, but by dividing by original image (with a
# baseline offset so there's no divide by zero issues) we downweight
# those stellar cores.
imarith foo3 / foo4 foo5

#finally, find pixel which are outlying in the modified high frequency
# image. In the operation statement in quotes,
# im1,im2,im3=foo5,base1,foo2
imcalc foo5,base1,foo2 out1.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'

#same as above, for chips 2,3,4
!rm foo*
rmedian base2 foo2 0.0 1.5
imarith base2 - foo2 foo3
imarith foo2 + 100 foo4
imarith foo3 / foo4 foo5
imcalc foo5,base2,foo2 out2.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'
!rm foo*
rmedian base3 foo2 0.0 1.5
imarith base3 - foo2 foo3
imarith foo2 + 100 foo4
imarith foo3 / foo4 foo5
imcalc foo5,base3,foo2 out3.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'
!rm foo*
rmedian base4 foo2 0.0 1.5
imarith base4 - foo2 foo3
imarith foo2 + 100 foo4
imarith foo3 / foo4 foo5
imcalc foo5,base4,foo2 out4.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'
!rm diff*fits
imarith base1 - out1 diff1
imarith base2 - out2 diff2
imarith base3 - out3 diff3
imarith base4 - out4 diff4
log

