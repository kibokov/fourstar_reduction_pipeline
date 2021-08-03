pro ffs

;this code just wraps the IRAF "engine" that does the actual
;filtering.  It expects pipeline processed files c1-c4, of equal number.

;open a file to output results
openw,1,'filtering.results'

;find lists of all the files
foo1=findfile('CJ*_c1.fits')
foo2=findfile('CJ*_c2.fits')
foo3=findfile('CJ*_c3.fits')
foo4=findfile('CJ*_c4.fits')

;check that the lists have the same number of entries, and if yes, proceed...
if(n_elements(foo1) eq n_elements(foo2) and n_elements(foo1) eq n_elements(foo3) and n_elements(foo1) eq n_elements(foo4))then begin
  ;step through the list of images
  for i=0,n_elements(foo1)-1 do begin
    ;copy images into simple names that are hardcoded into IRAF task 
    spawn,'cp '+foo1(i)+' base1.fits'
    spawn,'cp '+foo2(i)+' base2.fits'
    spawn,'cp '+foo3(i)+' base3.fits'
    spawn,'cp '+foo4(i)+' base4.fits'
    ;run ths IRAF task
    spawn,'cl < cleanit.cl'
                                ;cp the outputs of the IRAF task into
                                ;image names with "filtered_" pre-pended
    spawn,'cp out1.fits filtered_'+foo1(i)
    spawn,'cp out2.fits filtered_'+foo2(i)
    spawn,'cp out3.fits filtered_'+foo3(i)
    spawn,'cp out4.fits filtered_'+foo4(i)

    ;read the difference images 
    im1=readfits('diff1.fits')
    im2=readfits('diff2.fits')
    im3=readfits('diff3.fits')
    im4=readfits('diff4.fits')
    ;count the number of pixels that got altered
    qui=where(abs(im1) gt 1e-6,c1)
    qui=where(abs(im2) gt 1e-6,c2)
    qui=where(abs(im3) gt 1e-6,c3)
    qui=where(abs(im4) gt 1e-6,c4)
    ;record that number in the output file
    printf,1,foo1(i),c1,c2,c3,c4,format='(A,4I8)'
  endfor
endif  

;close the output file
close,1

end
