# eyes2mouth
!["01"](example01.png)
!["02"](example02.png)
!["03"](example03.png)
!["04"](example04.png)
## train
1. Preprocess cropped images
    ~~~bash
    $ cd input/
    $ ./untar.sh
    $ cd ..
    ~~~
2. Generate dataset by concatenating and resizing the images
    ~~~bash
    $ python3 gen_dataset.py
    ~~~
3. Start training
    ~~~bash
    $ python3 main.py --phase train --dataset_name face128 --batch_size 10 --fine_size 128 --lr 0.00002
    ~~~

## test
1. Start testing
    ~~~bash
    $ python3 main.py --phase test --dataset_name face128 --batch_size 10 --fine_size 128
    ~~~
