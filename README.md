# What's this?
Is it possible to generate mouth image only from the information how eyes look like?  
Eyes2mouth network answers this question using Deep Learning and pix2pix network.  
Here, we show our scheme.  
!["a"](images/architecture.jpg)

# Samples
!["01"](images/test_0001.png)
!["02"](images/test_0002.png)
!["03"](images/test_0003.png)
!["04"](images/test_0004.png)  
!["05"](images/test_0005.png)
!["05"](images/test_0006.png)
!["05"](images/test_0007.png)
!["05"](images/test_0008.png)  
!["05"](images/test_0009.png)
!["05"](images/test_0010.png)
!["05"](images/test_0011.png)
!["05"](images/test_0012.png)  
!["05"](images/test_0013.png)
!["05"](images/test_0004.png)
!["05"](images/test_0015.png)
!["05"](images/test_0016.png)

# How to use
## Train
1. Download celeba dataset
    ~~~bash
    $ ./download_celeba/sh
    ~~~
2. Cropping faces
    ~~~bash
    $ python gen_dataset.py
    ~~~
3. Start training
    ~~~bash
    $ python main.py --phase train --dataset_name cropped_128 --batch_size 10 --fine_size 128 --lr 0.00002
    ~~~

## Test
1. Start testing
    ~~~bash
    $ python main.py --phase test --dataset_name cropped_128 --batch_size 10 --fine_size 128
    ~~~
